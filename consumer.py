import pika
import subprocess 


connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
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