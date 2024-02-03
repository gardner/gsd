## Writes results to file

import json
from datasets import load_dataset
import pika
import os
from linecount import rawbigcount

# if not set RABBITMQ_PASS exit
if not os.environ.get('RABBITMQ_PASS'):
    print("RABBITMQ_PASS not set")
    exit(1)

queue = 'c4_result_queue'

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

def callback(ch, method, properties, body):
    print('.', end='', flush=True)
    job = json.loads(body)
    try:
        with open("/app/c4-wrap.jsonl", "a") as f:
            f.write(json.dumps(job) + "\n")

        ch.basic_ack(delivery_tag=method.delivery_tag)

        # TODO upload to huggingface dataset
        if rawbigcount("/app/c4-wrap.jsonl") > 10000:
            pass
            # upload to huggingface dataset
            # print("Uploading to huggingface dataset")
            # dataset = load_dataset("json", data_files="/app/c4-wrap.jsonl")
            # dataset.save_to_disk("/app/c4-wrap")
            # os.remove("/app/c4-wrap.jsonl")

    except Exception as e:
        print(f" [x] Error {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        raise e

def main():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=queue, on_message_callback=callback)
    channel.start_consuming()

if __name__ == "__main__":
    main()
