FROM python:3.7-slim

WORKDIR /app

RUN apt-get update \
    && apt install -y netcat

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY ./requirements.txt .

RUN pip3 install -U pip

RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./docker-entrypoint.sh ./docker-entrypoint.sh

COPY . .

ENTRYPOINT ["./docker-entrypoint.sh" ]
