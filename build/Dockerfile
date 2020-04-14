FROM python:3.7-slim

ENV PYTHONUNBUFFERED 1

RUN mkdir /app
WORKDIR /app

COPY ./build/requirements.txt /app/
COPY ./app/* /app/

RUN pip install --upgrade pip && pip install -r ./requirements.txt
