from datetime import datetime, timedelta
import multiprocessing
import json
import time
from kafka import KafkaConsumer, KafkaProducer, KafkaAdminClient
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import logging
import concurrent.futures
import threading
from pymongo import MongoClient
import os
import numpy as np
from obspy import Trace, Stream, read
import io

# Configure logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s %(levelname)s %(message)s')

# Global variables
# bootstrap_servers = 'kafka:9092'
bootstrap_servers = ['kafka1:9092', 'kafka2:9093']
kafka_topic = 'trace_topic'
group_id = 'data_archiver_group'
# mongo_url = "mongodb://root:example@mongo:27017/"
mongo_url = "mongodb://mongo:27017/"
influxdb_url = "http://influxdb:8086"
influxdb_token = "eFWu0UGcCzvGAX1w-z43heHjfDk8swujfryImhIsTrAkNJOgfMRSYsgYVki-QTiWHDwKLJtxsSnCmHhxisCN1w=="
influxdb_org = "owner"
influxdb_bucket = "eews"

# Initialize MongoDB connection
mongo_client = MongoClient(mongo_url)

mongo_db = mongo_client['timeseries_db']

# Create time series collection if it doesn't exist
try:
    if 'timeseries_collection' not in mongo_db.list_collection_names():
        mongo_db.create_collection(
            'timeseries_collection',
            timeseries={
                'timeField': 'timestamp',
                'metaField': 'metadata',
                'granularity': 'seconds'
            }
        )
    mongo_collection = mongo_db['timeseries_collection']
except Exception as e:
    logging.error(f"Error initializing MongoDB: {e}")

# Initialize InfluxDB client
influxdb_client = InfluxDBClient(
    url=influxdb_url, token=influxdb_token, org=influxdb_org)
influxdb_write_api = influxdb_client.write_api(write_options=SYNCHRONOUS)


def check_kafka_connection(bootstrap_servers):
    logging.info("Checking Kafka connection...")
    try:
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        is_connected = producer.bootstrap_connected()
        logging.info(f"Kafka connection established: {is_connected}")
        return is_connected
    except Exception as e:
        logging.error(f"Error connecting to Kafka: {e}")
        return False


def topic_exists(topic_name, bootstrap_servers):
    logging.info("Checking Kafka topic...")
    try:
        kafka_admin_client = KafkaAdminClient(
            bootstrap_servers=bootstrap_servers)
        is_topic_exist = topic_name in kafka_admin_client.list_topics()
        logging.info(f"Topic '{topic_name}' exists: {is_topic_exist}")
        return is_topic_exist
    except Exception as e:
        logging.error(f"Error checking Kafka topic: {e}")
        return False


def save_data_to_influxdb(data):
    try:
        start_run_time = time.time()
        start_time = int(data['start_time'] * 1e9)
        increment = int(1 / data['sampling_rate'] * 1e9)
        points = []

        for i, value in enumerate(data['data']):
            point = (
                Point("wave")
                .tag("stat", data['station'])
                .field(data['channel'], value)
                .time(start_time + i * increment, WritePrecision.NS)
            )
            points.append(point)

        influxdb_write_api.write(
            bucket=influxdb_bucket, org=influxdb_org, record=points)
        end_run_time = time.time()

        logging.info(f"InfluxDB Time: {end_run_time - start_run_time} seconds")
    except Exception as e:
        logging.error(f"Error saving data to InfluxDB: {e}")


def save_data_to_mongodb(data):
    try:
        start_run_time = time.time()
        start_time = datetime.utcfromtimestamp(data['start_time'])
        increment = timedelta(seconds=1 / data['sampling_rate'])
        documents = []

        for i, value in enumerate(data['data']):
            timestamp = start_time + i * increment
            document = {
                "timestamp": timestamp,
                "metadata": {
                    "station": data['station'],
                    "channel": data['channel']
                },
                "value": value
            }
            documents.append(document)

        mongo_collection.insert_many(documents)
        end_run_time = time.time()

        logging.info(f"MongoDB Time: {end_run_time - start_run_time} seconds")
    except Exception as e:
        logging.error(f"Error saving data to MongoDB: {e}")


def read_existing_mseed(filepath):
    reclen = 512
    with open(filepath, 'rb') as fh:
        data_blocks = []
        block = fh.read(reclen)
        while block:
            data_blocks.append(block)
            block = fh.read(reclen)
    data_io = io.BytesIO(b''.join(data_blocks))
    data_io.seek(0)
    return read(data_io, format='MSEED')


def merge_and_write_mseed(existing_traces, new_trace, filepath):
    if existing_traces:
        for tr in existing_traces:
            existing_traces.remove(tr)
        existing_traces.append(new_trace)
    else:
        existing_traces.append(new_trace)
    existing_traces.sort(keys=['starttime'])
    existing_traces.write(filepath, format='MSEED')


def save_data_to_mseed(data):
    start_run_time = time.time()
    today = datetime.utcnow().date()

    try:
        required_keys = ["network", "station", "channel",
                         "data", "location", "start_time", "sampling_rate"]
        if not all(key in data for key in required_keys):
            logging.error("Missing one or more required keys in data")
            return

        # Define paths
        path_save = f"/mnt/data/{today}/{data['network']}/{data['station']}/{data['channel']}"
        path_save_day = f"{path_save}/day_mseed"
        os.makedirs(path_save, exist_ok=True)
        os.makedirs(path_save_day, exist_ok=True)

        utc_year = str(today.year)
        utc_julian_day = today.strftime('%j')

        trace = Trace(data=np.array(data["data"], dtype=float))
        trace.stats.station = data["station"]
        trace.stats.network = data["network"]
        trace.stats.location = data["location"]
        trace.stats.channel = data["channel"]
        trace.stats.starttime = datetime.utcfromtimestamp(data["start_time"])
        trace.stats.sampling_rate = float(data["sampling_rate"])

        day_mseed_filename = f"{data['network']}.{data['station']}.{data['location']}.{data['channel']}.{utc_year}.{utc_julian_day}.mseed"
        day_mseed_filepath = os.path.join(path_save_day, day_mseed_filename)

        # Handle daily MiniSEED file
        if not os.path.isfile(day_mseed_filepath):
            Stream([trace]).write(day_mseed_filepath, format="MSEED")
        else:
            try:
                st1 = read_existing_mseed(day_mseed_filepath)
                existing_traces = [
                    tr for tr in st1 if tr.stats.station == trace.stats.station and
                    tr.stats.network == trace.stats.network and
                    tr.stats.starttime == trace.stats.starttime and
                    tr.stats.endtime == trace.stats.endtime]
                merge_and_write_mseed(st1, trace, day_mseed_filepath)
            except (UserWarning, Exception) as e:
                logging.error(
                    f"Error while reading/writing daily MiniSEED file: {e}")

        # Handle archival MiniSEED file
        date_str = trace.stats.starttime.strftime("%Y.%j")
        fmtstr = '/'.join(
            date_str.split('.')[:1] + [trace.id.split('.')[i] for i in [0, 1, 3]]) + ".D"
        directory = f"/mnt/data/{fmtstr}"
        os.makedirs(directory, exist_ok=True)

        filename1 = f"{directory}/{trace.id}.D.{date_str}.mseed"

        if os.path.exists(filename1):
            try:
                st2 = read_existing_mseed(filename1)
                existing_traces = [
                    tr for tr in st2 if tr.stats.station == trace.stats.station and
                    tr.stats.network == trace.stats.network and
                    tr.stats.starttime == trace.stats.starttime and
                    tr.stats.endtime == trace.stats.endtime]
                merge_and_write_mseed(st2, trace, filename1)
            except (UserWarning, Exception) as e:
                logging.error(
                    f"Error while reading/writing archival MiniSEED file: {e}")
        else:
            trace.write(filename1, format='MSEED')

        end_run_time = time.time()
        logging.info(f"MiniSEED Time: {end_run_time - start_run_time} seconds")

    except Exception as e:
        logging.error(
            f"Unexpected error while processing data to MiniSEED: {e}")


def initialize_system():
    while True:
        if check_kafka_connection(bootstrap_servers) and topic_exists(kafka_topic, bootstrap_servers):
            logging.info("System initialization successful.")
            break
        time.sleep(3)


def consume_and_save_data():
    consumer = KafkaConsumer(
        kafka_topic,
        group_id=group_id,
        bootstrap_servers=bootstrap_servers,
        value_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

    # with multiprocessing.Pool(processes=12) as pool:
    #     with concurrent.futures.ThreadPoolExecutor(max_workers=24) as executor:
    #         try:
    #             for msg in consumer:
    #                 data = msg.value
    #                 logging.info(
    #                     f"Delay: {time.time() - data['data_provider_time']}")

    #                 pool.apply_async(save_data_to_influxdb, args=(data,))
    #                 pool.apply_async(save_data_to_mongodb, args=(data,))
    #                 # pool.apply_async(save_data_to_mseed, args=(data,))
    #         except KeyboardInterrupt:
    #             logging.info("Shutting down gracefully...")
    #         finally:
    #             logging.info("Waiting for all subprocesses to complete...")
    #             pool.close()
    #             pool.join()

    try:
        for msg in consumer:
            data = msg.value

            start_time = time.time()
            threading.Thread(target=save_data_to_influxdb, args=(data,)).start()
            # threading.Thread(target=save_data_to_mongodb, args=(data,)).start()
            # threading.Thread(target=save_data_to_mseed, args=(data,)).start()

            logging.info(f"Delay: {time.time() - data['data_provider_time']}\tProcessing Time: {time.time() - start_time}")

    except KeyboardInterrupt:
        logging.info("Shutting down gracefully...")
    finally:
        logging.info("Waiting for all threads to complete...")
        consumer.close()
        consumer.join()

if __name__ == "__main__":
    initialize_system()
    consume_and_save_data()
