import pika
import subprocess
import time # Import the time module

def main():
    retries = 5
    connection = None
    while retries > 0:
        try:
            # Try to establish a connection
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            print("Consumer successfully connected to RabbitMQ.")
            break # Exit loop if connection is successful
        except pika.exceptions.AMQPConnectionError:
            print(f"RabbitMQ is not ready yet. Retrying in 5 seconds... ({retries} retries left)")
            retries -= 1
            time.sleep(5)

    if not connection:
        print("Could not connect to RabbitMQ after several retries. Exiting.")
        return # Exit the script if connection fails

    channel = connection.channel()
    channel.queue_declare(queue='job_queue', durable=True)
    print(' [*] Waiting for jobs. To exit press CTRL+C')

    def callback(ch, method, properties, body):
        print(f" [x] Received a new job.")
        script_code = body.decode()
        try:
            process = subprocess.run(
                ['./worker'],
                input=script_code,
                text=True,
                capture_output=True
            )
            print("--- C++ Worker Output ---")
            print(process.stdout)
            if process.stderr:
                print("--- C++ Worker Error ---")
                print(process.stderr)
            print("-------------------------")
        except Exception as e:
            print(f"Failed to execute C++ worker: {e}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue='job_queue', on_message_callback=callback)
    channel.start_consuming()

if __name__ == '__main__':
    main()