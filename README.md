# MicroAnalytics

# This project is a distributed, microservices-based platform designed to execute scientific computing jobs asynchronously. It allows users to submit Python scripts via a REST API, which are then processed by a high-performance C++ backend, with a message queue handling the communication to ensure scalability and resilience.

Architecture Overview
The system is decoupled into several distinct services that communicate asynchronously:

API Gateway (Flask): A lightweight Python web server that exposes a single POST /api/jobs endpoint. Its only job is to receive a script from the user and publish it to the message queue.

Message Queue (RabbitMQ): A Dockerized RabbitMQ instance that acts as a message broker. It receives jobs from the API and holds them in a queue until a worker is ready.

Python Consumer: A Python script that continuously listens to the RabbitMQ queue. When a new job arrives, it consumes the message and hands it off to the C++ worker.

C++ Worker: A compiled C++ application that receives the Python script via standard input from the consumer. It executes the script and prints the output, completing the job.