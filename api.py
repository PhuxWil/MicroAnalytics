from flask import Flask, request, jsonify
import pika
import time # Import the time module

app = Flask(__name__)

def connect_to_rabbitmq():
    retries = 5
    while retries > 0:
        try:
            # Try to establish a connection
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            print("Successfully connected to RabbitMQ.")
            return connection
        except pika.exceptions.AMQPConnectionError:
            print(f"RabbitMQ is not ready yet. Retrying in 5 seconds... ({retries} retries left)")
            retries -= 1
            time.sleep(5) # Wait for 5 seconds before retrying
    # If all retries fail, raise an exception
    raise Exception("Could not connect to RabbitMQ after several retries.")


@app.route('/api/jobs', methods=['POST'])
def submit_job():
    script_code = request.get_data(as_text=True)

    if not script_code:
        return jsonify({"error": "No script provided"}), 400

    connection = None # Initialize connection to None
    try:
        connection = connect_to_rabbitmq()
        channel = connection.channel()
        channel.queue_declare(queue='job_queue', durable=True)
        channel.basic_publish(
            exchange='',
            routing_key='job_queue',
            body=script_code,
            properties=pika.BasicProperties(delivery_mode=2)
        )
        print(f" [x] Sent job to queue")
        return jsonify({"status": "success", "message": "Job submitted successfully!"}), 202
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to submit job to queue"}), 500
    finally:
        # Make sure to close the connection if it was opened
        if connection and connection.is_open:
            connection.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5000)