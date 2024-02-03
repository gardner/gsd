# conda create -y -n vllm python=3.11 && conda activate vllm
# python3 -m pip install -U pika vllm

import json
import time
from vllm import LLM, SamplingParams
import pika
import os

if not os.environ.get('RABBITMQ_PASS'):
    print("RABBITMQ_PASS not set")
    exit(1)


system = "A chat between a curious user and an artificial intelligence assistant. The assistant gives helpful, detailed, and polite answers to the questions."

prompt_list = {
    "easy": "For the following paragraph give me a paraphrase of the same using a very small vocabulary and extremely simple sentences that a toddler will understand:\n\n",
    "medium": "For the following paragraph give me a diverse paraphrase of the same in high quality English language as in sentences on Wikipedia::\n\n",
    "hard": "For the following paragraph give me a paraphrase of the same using very terse and abstruse language that only an erudite scholar will understand. Replace simple words and phrases with rare and complex ones:\n\n",
    "qastyle": 'Convert the following paragraph into a conversational format with multiple tags of "Question:" followed by "Answer:":\n\n',
}

### vLLM
sampling_params = SamplingParams(
    temperature=0.8,
    top_p=0.95,
    max_tokens=2048,
    # logprobs=1 ## TODO Should we include logprops?
)

llm = LLM(
    model="TheBloke/Mistral-7B-Instruct-v0.2-AWQ",
    max_model_len=4096,
    enforce_eager=True,
)

tokenizer = llm.get_tokenizer()

### pika / rabbitmq
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

c4_task_queue = 'c4_task_queue'
c4_result_queue = 'c4_result_queue'
channel.queue_declare(queue=c4_task_queue, durable=True)
channel.queue_declare(queue=c4_result_queue, durable=True)


### Functions
def check_size(new_prompt):
    prompt_len = len(tokenizer.encode(new_prompt))
    rc = prompt_len < 4096
    if not rc:
        print("Prompt too long: ", prompt_len)
    return rc

def get_response(prompts):
    return llm.generate(
        prompts,
        sampling_params=sampling_params,
    )

def get_all(system, prompts, input):
    prompt = []
    for p in prompts.values():
        new_prompt = "[INST]" + system + p + input + "[/INST]\n\n"
        if check_size(new_prompt):
            prompt.append(new_prompt)
    return get_response(prompt)

def submit_work_packet(work_packet):
    print('+', end='', flush=True)
    channel.basic_publish(
        exchange='',
        routing_key=c4_result_queue,
        body=json.dumps(work_packet),
        properties=pika.BasicProperties(
            delivery_mode=pika.DeliveryMode.Persistent
        ))

    pass

def callback(ch, method, properties, body):
    print('-', end='', flush=True)
    job = json.loads(body)

    try:
        res = {}
        outputs = get_all(system, prompt_list, job['text'])
        for idx, key in enumerate(prompt_list.keys()):
            res[key] = outputs[idx].outputs[0].text

        res['timestamp'] = job['timestamp']
        res['url'] = job['url']
        submit_work_packet(res)
        ch.basic_ack(delivery_tag=method.delivery_tag)

    except Exception as e:
        print(f" [x] Error {e}")
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)
        raise e

    print(" [x] Done")

def main():
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue=c4_task_queue, on_message_callback=callback)
    channel.start_consuming()


if __name__ == "__main__":
    main()


