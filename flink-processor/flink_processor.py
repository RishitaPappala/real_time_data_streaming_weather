from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import KafkaSource
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.datastream import WatermarkStrategy
from pyflink.common.time import Time
from pyflink.datastream.window import TumblingEventTimeWindows
import json
import psycopg2

# Kafka configuration
BROKERS = "kafka:9092"

def weather_deserialization(message):
    """Deserialize the Kafka message to a Weather object"""
    try:
        data = json.loads(message)
        weather = Weather(data['city'], data['temperature'])
        print(f"Deserialized weather: {weather}")
        return weather
    except Exception as e:
        print(f"Error during deserialization: {e}")
        return None

class Weather:
    """Weather class similar to the Java version"""
    def __init__(self, city=None, temperature=None):
        self.city = city
        self.temperature = float(temperature) if temperature else None
    
    def __str__(self):
        return f"Weather(city={self.city}, temperature={self.temperature})"

class MyAverage:
    """Accumulator class for calculating average temperature"""
    def __init__(self):
        self.city = None
        self.count = 0
        self.sum = 0.0
    
    def add(self, weather):
        self.city = weather.city
        self.count += 1
        self.sum += weather.temperature
        print(f"Accumulating for city {self.city}: {self.count} readings, sum={self.sum}")
    
    def merge(self, other):
        self.sum += other.sum
        self.count += other.count
        print(f"Merged accumulator: count={self.count}, sum={self.sum}")
        return self
    
    def get_result(self):
        return self.city, self.sum / self.count

# Set up the Flink environment
env = StreamExecutionEnvironment.get_execution_environment()
env.set_parallelism(1)
print("Flink environment created.")

# Create Kafka source
kafka_source = KafkaSource.builder()\
    .set_bootstrap_servers(BROKERS)\
    .set_property("partition.discovery.interval.ms", "1000")\
    .set_topics("weather")\
    .set_group_id("groupdId-919292")\
    .set_starting_offsets("earliest")\
    .set_value_only_deserializer(SimpleStringSchema())\
    .build()
print("Kafka source configured.")

# Set the watermark strategy
watermark_strategy = WatermarkStrategy.for_monotonous_timestamps()
print("Watermark strategy configured.")

# Create the stream from Kafka
stream = env.from_source(kafka_source, watermark_strategy, "Kafka Source")
print("Kafka source created.")

# Deserialize the data
weather_stream = stream.map(weather_deserialization, output_type=Types.PICKLED_BYTE_ARRAY())
print("Weather stream deserialized.")

# Key by city and aggregate
def aggregate_weather(event, accumulator):
    print(f"Aggregating event: {event}")
    accumulator.add(event)
    return accumulator

weather_aggregated_stream = weather_stream.key_by(lambda event: event.city) \
    .window(TumblingEventTimeWindows.of(Time.seconds(60))) \
    .reduce(aggregate_weather)
print("Aggregation setup complete.")

# Convert results to tuple
def map_to_tuple(event):
    print(f"Mapping result: {event}")
    return (event.city, event.sum / event.count)

city_and_avg_stream = weather_aggregated_stream.map(map_to_tuple, output_type=Types.TUPLE([Types.STRING(), Types.FLOAT()]))
print("Mapped results to tuple.")

# PostgreSQL connection setup outside sink
def setup_postgres_connection():
    """Establish and return a PostgreSQL connection."""
    try:
        conn = psycopg2.connect("dbname=test user=postgres password=postgres host=postgres port=5432")
        return conn
    except Exception as e:
        print(f"Error setting up PostgreSQL connection: {e}")
        return None

# PostgreSQL Sink
def postgres_sink(value, conn):
    """Function to insert data into PostgreSQL"""
    try:
        print(f"Inserting into PostgreSQL: {value}")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO weather (city, average_temperature) VALUES (%s, %s)", (value[0], value[1]))
        conn.commit()
        cursor.close()
        print(f"Inserted {value} into PostgreSQL successfully.")
    except Exception as e:
        print(f"Error inserting into PostgreSQL: {e}")

# Initialize PostgreSQL connection
postgres_conn = setup_postgres_connection()
if postgres_conn:
    city_and_avg_stream.add_sink(lambda value: postgres_sink(value, postgres_conn))
    print("Sink to PostgreSQL added.")
else:
    print("PostgreSQL connection failed, sink not added.")

# Execute the job
try:
    env.execute("Kafka-Flask-Postgres Data Pipeline")
    print("Flink job executed successfully.")
except Exception as e:
    print(f"Error during Flink job execution: {e}")