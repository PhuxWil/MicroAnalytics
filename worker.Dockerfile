FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y g++

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

RUN g++ -o worker worker.cpp

CMD ["python3", "consumer.py"]