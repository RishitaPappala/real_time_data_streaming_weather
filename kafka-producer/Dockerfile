FROM python:3.8-slim

# Set the working directory to /app inside the container.
WORKDIR /app

# Copy the requirements file from the kafka-producer directory in the repository root.
COPY kafka-producer/requirements.txt .

# Install Python dependencies.
RUN set -ex; \
    pip install --no-cache-dir -r requirements.txt

# Copy the wait-for-it.sh script from the repository root into /app.
COPY wait-for-it.sh /app/wait-for-it.sh

# Copy the Kafka producer script from the kafka-producer directory.
COPY kafka-producer/python-producer.py .

# Make the wait-for-it.sh script executable.
RUN chmod +x /app/wait-for-it.sh

# Set the default command.
# This command waits for Zookeeper and Kafka to be available (using environment variables)
# then runs the python-producer.py script.
CMD ./wait-for-it.sh -s -t 30 $ZOOKEEPER_SERVER -- ./wait-for-it.sh -s -t 30 $KAFKA_SERVER -- python -u python-producer.py
