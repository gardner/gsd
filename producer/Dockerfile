FROM python:3.11-slim

RUN python3 -m pip install -U pip \
  && python3 -m pip install -U pika datasets huggingface_hub

WORKDIR /app

COPY producer.py /app/producer.py
CMD python3 /app/producer.py