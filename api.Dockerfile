FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Expose the port the app runs on
EXPOSE 5000

# The command to run when the container starts
CMD ["python3", "api.py"]