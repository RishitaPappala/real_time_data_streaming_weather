from pyflink.datastream import StreamExecutionEnvironment
from pyflink.datastream.connectors import KafkaSource
from pyflink.common.serialization import SimpleStringSchema
from pyflink.common.typeinfo import Types
from pyflink.common.watermark_strategy import WatermarkStrategy
from pyflink.java_gateway import get_gateway
from pyflink.datastream.window import TumblingEventTimeWindows
from pyflink.datastream.connectors.kafka import KafkaSource, KafkaOffsetsInitializer
from pyflink.datastream.functions import ProcessFunction
import json
import psycopg2
from pyflink.common import Row, Types

# Initialize JVM reference
jvm = get_gateway().jvm

class DurationWrapper:
    def __init__(self, java_duration):
        self._j_duration = java_duration
    def to_milliseconds(self):
        return self._j_duration.toMillis()

wrapped_duration = DurationWrapper(jvm.java.time.Duration.ofSeconds(10))

# Define the Weather class
class Weather:
    def __init__(self, city, temperature):
        self.city = city
        self.temperature = temperature
    def __str__(self):
        return f"Weather(city={self.city}, temperature={self.temperature})"

# Define the MyAverage accumulator class
class MyAverage:
    def __init__(self):
        self.city = None
        self.count = 0
        self.sum = 0.0

# Function to convert a Weather event into a MyAverage accumulator
def event_to_accumulator(event):
    acc = MyAverage()
    acc.city = event.city
    acc.count = 1
    acc.sum = event.temperature
    return acc

# Function to aggregate two MyAverage accumulators
def aggregate_weather(acc1, acc2):
    combined = MyAverage()
    combined.city = acc1.city  # They share the same key (city)
    combined.count = acc1.count + acc2.count
    combined.sum = acc1.sum + acc2.sum
    return combined

# Function to map the accumulator to a tuple (city, average_temperature)
def map_to_tuple(acc):
    if acc is None or acc.count == 0:
        return Row("N/A", 0.0)
    average = acc.sum / acc.count
    print(f"Mapping accumulator to result: city={acc.city}, average={average}")
    return Row(acc.city, average)

# Function to deserialize Kafka messages into Weather objects
def weather_deserialization(message):
    try:
        data = json.loads(message)
        weather = Weather(data['city'], data['temperature'])
        print(f"Deserialized weather: {weather}")
        return weather
    except Exception as e:
        print(f"Error during deserialization: {e}")
        return None

# PostgreSQL sink function
class PostgresSinkFunction(ProcessFunction):
    def __init__(self):
        super().__init__()
        self.connection = None
    
    def open(self, runtime_context):
        try:
            self.connection = psycopg2.connect(
                dbname="postgres",
                user="postgres",
                password="postgres",
                host="postgres",
                port=5432
            )
            print("PostgreSQL connection established in sink.")
        except Exception as e:
            print(f"Error connecting to PostgreSQL in sink: {e}")
            raise

    def process_element(self, value, ctx):
        if not self.connection or self.connection.closed:
            self.open(None)
            
        try:
            cursor = self.connection.cursor()
            cursor.execute(
                "INSERT INTO weather (city, average_temperature) VALUES (%s, %s)",
                (value[0], value[1])
            )
            self.connection.commit()
            cursor.close()
            print(f"Successfully inserted data: {value}")
        except Exception as e:
            print(f"Error inserting data into PostgreSQL: {e}")
            if not self.connection.closed:
                self.connection.rollback()

    def close(self):
        if self.connection and not self.connection.closed:
            self.connection.close()
            print("PostgreSQL connection closed.")

def main():
    # Set up the Flink environment
    env = StreamExecutionEnvironment.get_execution_environment()
    env.set_parallelism(1)
    print("Flink environment created.")

    # Create Kafka source
    kafka_source = KafkaSource.builder()\
        .set_bootstrap_servers("kafka:9092")\
        .set_topics("weather")\
        .set_group_id("groupdId-919292")\
        .set_starting_offsets(KafkaOffsetsInitializer.earliest())\
        .set_value_only_deserializer(SimpleStringSchema())\
        .build()
    print("Kafka source configured.")

    # Create the watermark strategy
    watermark_strategy = WatermarkStrategy.for_bounded_out_of_orderness(wrapped_duration)
    print("Watermark strategy configured.")

    # Create the stream from Kafka
    stream = env.from_source(kafka_source, watermark_strategy, "Kafka Source")
    print("Kafka source created.")

    # Deserialize the stream into Weather objects
    weather_stream = stream.map(weather_deserialization, output_type=Types.PICKLED_BYTE_ARRAY())
    print("Weather stream deserialized.")

    # Convert Weather objects into MyAverage accumulators
    acc_stream = weather_stream.map(event_to_accumulator, output_type=Types.PICKLED_BYTE_ARRAY())

    # Create a wrapped duration of 60 seconds for the window
    window_duration = DurationWrapper(jvm.java.time.Duration.ofSeconds(60))

    # Define the result type for the output
    result_type = Types.ROW([Types.STRING(), Types.DOUBLE()])

    # Apply windowing, reduce, and map to tuples
    city_and_avg_stream = acc_stream.key_by(lambda acc: acc.city) \
        .window(TumblingEventTimeWindows.of(window_duration)) \
        .reduce(aggregate_weather) \
        .map(map_to_tuple, output_type=result_type)

    # Add the PostgreSQL sink
    city_and_avg_stream.process(PostgresSinkFunction())
    print("Sink to PostgreSQL added.")

    # Execute the Flink job
    try:
        env.execute("Kafka-Flask-Postgres Data Pipeline")
        print("Flink job executed successfully.")
    except Exception as e:
        print(f"Error during Flink job execution: {e}")

if __name__ == "__main__":
    main()
