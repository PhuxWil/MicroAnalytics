# worker.Dockerfile
FROM python:3.9-slim
WORKDIR /app

# Install system dependencies for C++ and Matplotlib
RUN apt-get update && apt-get install -y g++ libpq-dev libpqxx-dev libfreetype6-dev libfontconfig1

COPY requirements.txt .
RUN pip install -r requirements.txt

# This new line pre-builds the matplotlib font cache to prevent hangs
RUN python3 -c "import matplotlib.pyplot"

COPY . .

# Compile the C++ worker and link against PostgreSQL libraries
RUN g++ -o worker worker.cpp -lpqxx -lpq

CMD ["python3", "consumer.py"]