from flask import Flask, request, jsonify
import pika
import time
import psycopg2
from psycopg2 import sql
import uuid # For generating unique job IDs
import json # To send structured data to the queue

app = Flask(__name__)

# --- Database Setup ---
def get_db_connection():
    retries = 5
    while retries > 0:
        try:
            conn = psycopg2.connect(
                host="db", # The service name from docker-compose
                database="analytics",
                user="user",
                password="password"
            )
            print("Successfully connected to Database.")
            return conn
        except psycopg2.OperationalError:
            retries -= 1
            print(f"Database is not ready yet. Retrying in 5 seconds... ({retries} retries left)")
            time.sleep(5)
    raise Exception("Could not connect to database after several retries.")

def setup_database():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            job_id UUID PRIMARY KEY,
            script_code TEXT,
            status VARCHAR(20),
            result TEXT,
            created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

# --- RabbitMQ Connection (from last week, now inside a function) ---
def connect_to_rabbitmq():
    # This function can remain largely the same, just for clarity
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
    return connection

# --- API Endpoints ---
@app.route('/api/jobs', methods=['POST'])
def submit_job():
    script_code = request.get_data(as_text=True)
    if not script_code:
        return jsonify({"error": "No script provided"}), 400

    db_conn = None
    mq_conn = None
    try:
        job_id = str(uuid.uuid4())

        # 1. Insert job into database with 'SUBMITTED' status
        db_conn = get_db_connection()
        cur = db_conn.cursor()
        cur.execute(
            "INSERT INTO jobs (job_id, script_code, status) VALUES (%s, %s, %s)",
            (job_id, script_code, 'SUBMITTED')
        )
        db_conn.commit()
        cur.close()

        # 2. Prepare message for RabbitMQ
        message = {
            "job_id": job_id,
            "script_code": script_code
        }

        # 3. Publish job to RabbitMQ
        mq_conn = connect_to_rabbitmq()
        channel = mq_conn.channel()
        channel.queue_declare(queue='job_queue', durable=True)
        channel.basic_publish(
            exchange='', routing_key='job_queue',
            body=json.dumps(message), # Send as a JSON string
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f" [x] Sent job {job_id} to queue")
        return jsonify({"status": "success", "job_id": job_id}), 202

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to submit job"}), 500
    finally:
        if db_conn: db_conn.close()
        if mq_conn and mq_conn.is_open: mq_conn.close()


@app.route('/api/jobs/<string:job_id>', methods=['GET'])
def get_job_status(job_id):
    db_conn = None
    try:
        db_conn = get_db_connection()
        cur = db_conn.cursor()
        cur.execute("SELECT job_id, status, result, created_at FROM jobs WHERE job_id = %s", (job_id,))
        job = cur.fetchone()
        cur.close()

        if job:
            return jsonify({
                "job_id": job[0],
                "status": job[1],
                "result": job[2],
                "created_at": job[3]
            })
        else:
            return jsonify({"error": "Job not found"}), 404

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to retrieve job status"}), 500
    finally:
        if db_conn: db_conn.close()

if __name__ == '__main__':
    # On startup, ensure the database table exists
    setup_database()
    app.run(host='0.0.0.0', debug=True, port=5000)