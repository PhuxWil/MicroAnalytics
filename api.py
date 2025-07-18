from flask import Flask, request, jsonify
import pika # RabbitMQ client


app = Flask(__name__)

@app.route('/api/jobs', methods=['POST'])
def submit_job():

    script_code = request.get_data(as_text=True)

    if not script_code:
        return jsonify({"error": "No script provided"}), 400

    try:
       
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()

        channel.queue_declare(queue='job_queue', durable=True)

        channel.basic_publish(
            exchange='',
            routing_key='job_queue', 
            body=script_code,
            properties=pika.BasicProperties(
                delivery_mode=2,  
            ))

        connection.close()

        print(f" [x] Sent job to queue")
        return jsonify({"status": "success", "message": "Job submitted successfully!"}), 202

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "Failed to submit job to queue"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)