# create code to connect to rabbit mq container username admin password password port 5672 and send message
import pika
from time import sleep

credentials = pika.PlainCredentials('admin', 'password')
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost', 5672, '/', credentials))
channel = connection.channel()

channel.queue_declare(queue='hello')

channel.basic_publish(exchange='', routing_key='hello', body='Hello World!')
print(" [x] Sent 'Hello World!'")

for i in range(1000):
    channel.basic_publish(exchange='', routing_key='hello', body=f'Hello World! {i}')
    print(f" [x] Sent 'Hello World! {i}'")
    sleep(0.01)