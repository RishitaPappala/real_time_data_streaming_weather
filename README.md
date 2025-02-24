# Real-Time Data Streaming Weather

## Abstract
This project streams real-time weather data using **Apache Kafka**, **Apache Flink**, and **PostgreSQL**. It processes data from Kafka, cleans and aggregates temperature readings, and stores the results in a PostgreSQL database. The real-time nature of this project ensures up-to-date information is always available for further analysis or reporting.

This setup is ideal for systems requiring continuous monitoring and storage of dynamic data streams.

## Keywords
real-time data streaming; Kafka; Flink; PostgreSQL; weather data; aggregation; Python; microservices architecture; data processing

## Folder Structure
The `real_time_data_streaming_weather` directory is organized as follows:

```
real_time_data_streaming_weather/
├── docker-compose.yml          # Docker Compose configuration for the services
├── wait-for-it.sh              # Shell script to wait for Kafka and PostgreSQL
├── flink-processor/            # Flink processor directory
│   ├── Dockerfile              # Dockerfile to build Flink processor container
│   ├── flink_processor.py      # Python script to process weather data
│   └── requirements.txt        # Python dependencies for the Flink processor
├── kafka-producer/             # Kafka producer directory
│   ├── Dockerfile              # Dockerfile to build Kafka producer container
│   ├── kafka_producer.py       # Python script to produce weather data to Kafka
│   └── requirements.txt        # Python dependencies for the Kafka producer
├── postgres/                   # PostgreSQL directory
│   ├── Dockerfile              # Dockerfile to build PostgreSQL container
│   └── create_table.sql        # SQL script to initialize the PostgreSQL database
└── README.md                   # Project documentation (this file)
```

## How to Run the Code

### 1. Clone the Repository
Start by cloning the repository to your local machine:

```bash
git clone https://github.com/RishitaPappala/real_time_data_streaming_weather.git
cd real_time_data_streaming_weather
```

### 2. Build Docker Containers Using Docker Compose
Open the Docker app for login credentails to automatiicallly login you in
```bash
docker login
```

To ensure a fresh build for the project, run the below commands:
```bash
docker build --no-cache -t kafka-producer -f kafka-producer/Dockerfile .
```
```bash
docker build --no-cache -t flink-processor -f flink-processor/Dockerfile .
```

This command rebuilds your images without using cached layers and targets only the services defined in your docker-compose.yml file. You coud veriffy if the image has been created or not using the below command:
```bash
docker image ls
```

### 3. Start the Services
After the build, start the containers in detached mode:

```bash
docker-compose up
```

- **Detached Mode (-d)**: The -d flag in docker-compose up -d runs your containers in the background, freeing up your terminal for other tasks (ideal for production servers). It does not affect the image build process. Without -d option, you could see the logs automatically as the proceess attached itself to the terminal. 

This command launches the following services in the background:
- Kafka: For message brokering (produces and consumes weather data)
- PostgreSQL: For storing weather data
- Flink: For processing the weather data in real-time and inserting it into PostgreSQL

Check for the status:
```bash
docker ps -a
```

### 4. Monitor and Interact with the Application
If you need to view logs or interact with a specific container, you can use these commands:

To view logs for the any container:
```bash
docker-compose logs -f <container_name>
```

To execute a command inside a container (e.g., open a bash shell):
```bash
docker-compose exec <service_name> /bin/bash
```

Replace `<service_name>` with the appropriate service name from your docker-compose.yml.

### 5. Access PostgreSQL
PostgreSQL will be running on the default port 5432. You can access the database using any PostgreSQL client (such as psql or pgAdmin).

To access the PostgreSQL from within the Docker network, run:
```bash
docker exec -it postgres psql -U postgres -d postgres
```

For list of relations
```psql
\dt List of relations
```

To view records in weather table
 ```psql
select * from weather;
```

### 6. Access Kafka (Optional)
If you want to inspect the Kafka topics or use Kafka from your local machine, use the following configuration:
- Kafka Broker: kafka:9092
- Topic: weather

To inspect Kafka topics or produce/consume messages from your local machine, you can use Kafka's command-line tools. For example, to list all topics:
```bash
docker-compose exec kafka kafka-topics --bootstrap-server kafka:9092 --list
```

To consume messages from the "weather" topic from the beginning, run:
```
docker-compose exec kafka kafka-console-consumer --bootstrap-server kafka:9092 --topic weather --from-beginning
```

To produce messages to the "weather" topic, run:
```
docker-compose exec kafka kafka-console-producer --bootstrap-server kafka:9092 --topic weather
```


### 7. Stop the Services
Once you're finished, you can stop and remove the containers, networks, and volumes with:

```bash
docker-compose down
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.