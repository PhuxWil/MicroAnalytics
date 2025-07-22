FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y g++ libpq-dev libpqxx-dev

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN g++ -o worker worker.cpp -lpqxx -lpq

CMD ["python3", "consumer.py"]