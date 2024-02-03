import json
from datasets import load_dataset
import pika
from time import sleep
import os
from zlib import adler32

# if not set RABBITMQ_PASS exit
if not os.environ.get('RABBITMQ_PASS'):
    print("RABBITMQ_PASS not set")
    exit(1)

queue = 'c4_task_queue'

connection = pika.BlockingConnection(
    pika.ConnectionParameters(
        # host='localhost',
        host='rabbitmq',
        credentials=pika.PlainCredentials(
            username=os.environ['RABBITMQ_USER'],
            password=os.environ['RABBITMQ_PASS']
        )
    )
)
channel = connection.channel()

channel.queue_declare(queue=queue, durable=True)

ds = load_dataset("c4", 'en.noblocklist', split='train', streaming=True, trust_remote_code=True)
# done = load_dataset("json", data_files="/app/c4-wrap.jsonl", split='train')
# updated_dataset = ds.filter(lambda x: x['timestamp'] not in done['timestamp'])

# print(f"Done: {len(done)}")
# print(next(iter(ds)))
# print(next(iter(done)))
# print(next(iter(updated_dataset)))
# exit()

def publish(task):
    channel.basic_publish(
        exchange='',
        routing_key=queue,
        body=json.dumps(task),
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent
        ))

try:

    while row := next(iter(ds)):
        q = channel.queue_declare(queue=queue, passive=True)

        # Prevent queue from getting too big
        while q.method.message_count > 200:
            print('.', end='', flush=True)
            sleep(2)
            q = channel.queue_declare(queue=queue, passive=True)

        print('+', end='', flush=True)

        publish({
            "timestamp": row['timestamp'],
            "text": row['text'],
            "url": row['url'],
            "alder32": adler32(row['text'].encode('utf-8')),
        })

finally:
    connection.close()

