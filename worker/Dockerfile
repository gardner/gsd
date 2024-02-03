FROM vllm/vllm-openai:latest

RUN python3 -m pip install -U pip \
  && python3 -m pip install -U pika vllm

ENTRYPOINT []

WORKDIR /app

COPY worker.py /app/worker.py
CMD python3 /app/worker.py