
# Real-Time Data Streaming Weather

## Abstract
This project streams real-time weather data using **Apache Kafka**, **Apache Flink**, and **PostgreSQL**. It processes the data from Kafka, cleans and aggregates the temperature readings, and stores the results in a PostgreSQL database. The real-time nature of this project ensures up-to-date information is always available for further analysis or reporting.

This project utilizes Kafka for message brokering, Flink for real-time data processing, and PostgreSQL for storage. The Flink processor aggregates temperature data over time and inserts it into PostgreSQL. This setup is ideal for systems requiring continuous monitoring and storage of dynamic data streams.

---

## Keywords
real-time data streaming; Kafka; Flink; PostgreSQL; weather data; aggregation; Python; microservices architecture; data processing

---

## Folder Structure
The **`real_time_data_streaming_weather`** directory is organized as follows:

### 1. Docker Containers
- **`kafka-producer/`**:
  - Contains the Kafka producer Dockerfile for generating the Kafka producer container.
  - Responsible for generating and sending weather data.

- **`flink-processor/`**:
  - Contains the Flink processor Dockerfile and the Python script `flink_processor.py`.
  - The Flink processor listens to Kafka topics, aggregates temperature readings, and writes the results to PostgreSQL.

- **`wait-for-it.sh`**:
  - A shell script used for ensuring Kafka and PostgreSQL services are up and ready before starting the Python script.

### 2. Configuration and Setup
- **`docker-compose.yml`**:
  - Defines the multi-container setup (Kafka, PostgreSQL, Flink) for Docker Compose to handle orchestration.

- **`README.md`**:
  - Project documentation providing setup and usage instructions.

---

## How to Run the Code
Follow these steps to set up and run the project:

### 1. Clone the Repository
Start by cloning the repository to your local machine:

```bash
git clone https://github.com/RishitaPappala/real_time_data_streaming_weather.git
cd real_time_data_streaming_weather
```

### 2. Build Docker Containers
We have provided a Docker Compose configuration to build and run the necessary containers. These services include Kafka, PostgreSQL, and Flink.

#### Clean Up Existing Docker Containers, Volumes, and Images
Before building the containers, clean up any existing Docker images, containers, and volumes:

```bash
docker ps -a        # Lists all containers (including stopped ones)
docker images -a    # Lists all Docker images
docker volume ls    # Lists all Docker volumes
```

To remove any leftovers, run:

```bash
docker container prune -f  # Removes all stopped containers
docker image prune -a -f  # Removes all unused images
docker volume prune -f    # Removes all unused volumes
```

#### Build the Containers
Now, build the containers for Kafka, Flink, and the Python processor.

- **Kafka Producer Container**:

```bash
cd kafka-producer
docker build -t kafka-producer .
```

- **Flink Processor Container**:

```bash
cd ../flink-processor
docker build -t flink-processor .
```

#### Start the Services
Once the containers are built, use Docker Compose to start all services (Kafka, PostgreSQL, Flink):

```bash
docker-compose up -d
```

This will start the following services in the background:

- **Kafka**: For message brokering (produces and consumes weather data).
- **PostgreSQL**: For storing weather data.
- **Flink**: For processing the weather data in real-time and inserting it into PostgreSQL.

### 3. Monitor the Application
To check the logs of the running services and monitor real-time weather data processing, use the following commands:

- To view logs for the Flink processor:

```bash
docker-compose logs -f flink-processor
```

This will display logs from the Python-based Flink processor, where you can track the real-time processing of weather data.

- To check logs of a specific container (for example, Kafka Producer):

```bash
docker logs --tail 2000 <container_id>
```

You can find the `container_id` by running `docker ps -a` to list the active containers.

### 4. Access PostgreSQL
PostgreSQL will be running on the default port `5432`. You can access the database via any PostgreSQL client (such as `psql` or pgAdmin).

To access the PostgreSQL container from within the Docker network, run the following command:

```bash
docker exec -it data-streaming-kafka-producer-1 /bin/bash
```

Use the following credentials to connect to the database:

- **Username**: postgres
- **Password**: postgres
- **Database**: test

### 5. Access Kafka (Optional)
If you want to inspect the Kafka topics or use Kafka from your local machine, use the following configuration:

- **Kafka Broker**: kafka:9092
- **Topic**: weather

You can use any Kafka client to subscribe and produce messages to the `weather` topic.

### 6. Stop the Services
Once you're done, you can stop all running services by using the following command:

```bash
docker-compose down
```

This will stop and remove the containers, networks, and volumes defined in the `docker-compose.yml` file.

---

## Notes

- **Docker Stuck or Issues**: If Docker is stuck or you're facing issues, try using Docker Desktop's troubleshooting options to clean and reset the environment. You can reset to factory defaults or uninstall Docker Desktop and reinstall it.

---

## Directory Structure

Here’s an overview of the project’s structure:

```
real_time_data_streaming_weather/
│
├── docker-compose.yml           # Docker Compose configuration for the services
├── kafka-producer/              # Kafka producer directory
│   ├── Dockerfile               # Dockerfile to build Kafka producer container
│   └── ...
├── flink-processor/             # Flink processor with Python script
│   ├── flink_processor.py       # Python script to process weather data
│   ├── Dockerfile               # Dockerfile to build the Flink container
│   └── wait-for-it.sh           # Shell script to wait for Kafka and PostgreSQL
└── README.md                    # Project documentation (this file)
```

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

