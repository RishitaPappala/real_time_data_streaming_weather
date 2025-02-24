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

# Download and install Flink's Kafka connector JAR (version 1.17.0) to enable Kafka integration.
# This connector allows Flink to consume/produce data from/to Kafka topics.
# Version MUST match the Flink version (1.17.0) for compatibility.
RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/flink/flink-connector-kafka/1.17.0/flink-connector-kafka-1.17.0.jar

# Explicitly add Kafka client library (version 3.2.0) to resolve NoClassDefFoundError for Kafka classes.
# The Flink connector requires Kafka client dependencies at runtime.
# Version 3.2.0 is specifically chosen as it's compatible with Flink 1.17.0's Kafka connector.
RUN wget -P /opt/flink/lib/ https://repo.maven.apache.org/maven2/org/apache/kafka/kafka-clients/3.2.0/kafka-clients-3.2.0.jar

# Set the working directory to /app inside the container.
WORKDIR /app

# Copy the wait-for-it.sh script from the repository root into /app.
COPY wait-for-it.sh /app/wait-for-it.sh

# Make the wait-for-it.sh script executable.
RUN chmod +x /app/wait-for-it.sh

# Copy the Flink processor script from its directory into /app
COPY flink-processor/flink_processor.py /app/

# Default command: wait for dependencies and then run the Flink processor.
CMD ./wait-for-it.sh -s -t 30 $ZOOKEEPER_SERVER -- ./wait-for-it.sh -s -t 30 $KAFKA_SERVER -- python -u flink_processor.py





