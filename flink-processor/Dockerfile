# Use the official PyFlink image
FROM apache/flink:1.17.0

# Install python3, pip, and other required dependencies
RUN apt-get update && \
    apt-get install -y python3 python3-pip build-essential libpq-dev && \
    rm -rf /var/lib/apt/lists/*

# Ensure symbolic links for python3 and pip
RUN ln -sf /usr/bin/python3 /usr/bin/python && \
    ln -sf /usr/bin/pip3 /usr/bin/pip

# Install required Python dependencies
RUN pip install --no-cache-dir kafka-python psycopg2-binary apache-flink

# Copy the Kafka connector JAR into Flink's lib directory
COPY flink-connector-kafka_2.12-1.17.2.jar /opt/flink/lib/

# Set the working directory for your Python script
WORKDIR /app

# Copy the Python script and wait-for-it.sh
COPY flink_processor.py /app/flink_processor.py
COPY wait-for-it.sh /app/wait-for-it.sh

# Make the shell script executable
RUN chmod +x /app/wait-for-it.sh

# Set the entry point to wait for Kafka and PostgreSQL services, then run the Python script
CMD ["./wait-for-it.sh", "-s", "-t", "30", "kafka:9092", "--", \
     "./wait-for-it.sh", "-s", "-t", "30", "postgres:5432", "--", \
     "python", "/app/flink_processor.py"]
