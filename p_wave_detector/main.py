import json
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient
from time import sleep, time
import obspy
import numpy as np
import tensorflow as tf
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
from kafka.admin import KafkaAdminClient, NewTopic
import concurrent.futures

class TraceConsumer:
    def __init__(self):
        self.consumer = None
        self.producer = None
        self.model = tf.keras.models.load_model(
            './model_p_wave.h5', compile=False)
        self.query_api = self.connectInfluxDB()
        self.last_waveform = {}
        self.executor = concurrent.futures.ThreadPoolExecutor(max_workers=32)

    def configureConnection(self, topic, group, server):
        self.consumer = KafkaConsumer(
            topic,
            group_id=group,
            bootstrap_servers=server,
            value_deserializer=lambda x: json.loads(x.decode('utf-8')),
            key_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )

    def configureProducer(self, server):
        self.producer = KafkaProducer(
            bootstrap_servers=server,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def topic_exists(selft, topic_name, server):
        kafkaAdminClient = KafkaAdminClient(bootstrap_servers=server)
        is_topic_exist = topic_name in kafkaAdminClient.list_topics()
        print(f"Topic '{topic_name}' exists: {is_topic_exist}")
        return is_topic_exist

    def create_topic(self, kafka_topic, num_partitions, replication_factor, bootstrap_servers):
        kafkaAdminClient = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        while not self.topic_exists(kafka_topic, bootstrap_servers):
            try:
                new_topic = NewTopic(
                    name=kafka_topic,
                    num_partitions=num_partitions,
                    replication_factor=replication_factor
                )
                print(f"Creating topic '{kafka_topic}'...")
                kafkaAdminClient.create_topics(new_topics=[new_topic])
                print(f"Topic '{kafka_topic}' created successfully.")
            except Exception as e:
                print(f"Error creating topic '{kafka_topic}': {e}")
            sleep(3)

    def setTrace(self, data):
        trace = obspy.Trace(np.array(data['data']))
        trace.stats.network = data['network']
        trace.stats.station = data['station']
        trace.stats.location = data['location']
        trace.stats.channel = data['channel']
        trace.stats.starttime = obspy.UTCDateTime(data['start_time'])
        # trace.stats.endtime = obspy.UTCDateTime(data['end_time'])
        trace.stats.sampling_rate = data['sampling_rate']
        trace.stats.delta = data['delta']
        trace.stats.npts = data['npts']
        trace.stats.calib = data['calib']
        trace.stats.dataquality = data['data_quality']
        trace.stats.numsamples = data['num_samples']
        trace.stats.samplecnt = data['sample_cnt']
        trace.stats.sampletype = data['sample_type']

        # interpolate to 20 Hz
        trace.interpolate(sampling_rate=20)

        return trace

    def preprocessingPWave(self, data: np.ndarray):
        return data / np.max(np.abs(data), axis=0)

    def predict(self, trace):
        try:
            # duplicate the trace to 3 channels
            converter_np_array = np.array(
                [trace.data, trace.data, trace.data]).T
            sliding_array = np.lib.stride_tricks.sliding_window_view(
                converter_np_array, (160, 3)).reshape(-1, 160, 3)

            # preprocessing
            preprocessed_array = np.apply_along_axis(
                self.preprocessingPWave, axis=1, arr=sliding_array)

            # melakukan prediksi p wave dengan model Machine Learning
            predictions_p_wave = self.model.predict(
                preprocessed_array, verbose=0)

            # n check if p wave detected
            n = 20
            for i in range(len(predictions_p_wave) - n + 1):
                if np.all(predictions_p_wave[i:i + n] >= 0.5):
                    p_wave_time = trace.stats.starttime.timestamp + i * trace.stats.delta
                    print(
                        f"Station: {trace.stats.station},\tChannel: {trace.stats.channel},\tSampling Rate: {trace.stats.sampling_rate},\tP Wave Detected at time: {p_wave_time}")
                    # get 4 seconds data before p wave time and 4 seconds data after p wave time
                    # p_wave_waveform = trace.data[i - 80:i + 80]
                    p_wave_waveform = trace.data.tolist()[i + 40:i + 120]
                    # send to kafka
                    data = {
                        'network': trace.stats.network,
                        'station': trace.stats.station,
                        'location': trace.stats.location,
                        'channel': trace.stats.channel,
                        'sampling_rate': trace.stats.sampling_rate,
                        'p_wave_time': p_wave_time,
                        'data_provider_time': trace.stats.endtime.timestamp,
                        'p_wave_detector_time': time(),
                        'data': p_wave_waveform
                    }
                    # print(data)
                    self.producer.send('loc_mag_topic', data, key=f"{data['station']}-{data['channel']}")
                    self.producer.flush()
                    break

        except Exception as e:
            print(
                f"Error predict {trace.stats.station} {trace.stats.channel} {len(trace.data)}: {e}")

    def connectInfluxDB(self):
        influxdb_org = "owner"
        influxdb_url = "http://influxdb:8086"
        influxdb_token = "eFWu0UGcCzvGAX1w-z43heHjfDk8swujfryImhIsTrAkNJOgfMRSYsgYVki-QTiWHDwKLJtxsSnCmHhxisCN1w=="
        client = InfluxDBClient(url=influxdb_url, token=influxdb_token, org=influxdb_org)
        query_api = client.query_api()
        return query_api

    def readInfluxDB(self, station, channel, start_time, end_time):
        influxdb_bucket = "eews"
        influxdb_measurement = "wave"
        query = f'from(bucket: "{influxdb_bucket}") |> range(start: {start_time}, stop: {end_time}) |> filter(fn: (r) => r["_measurement"] == "{influxdb_measurement}") |> filter(fn: (r) => r["stat"] == "{station}") |> filter(fn: (r) => r["_field"] == "{channel}")'
        
        tables = self.query_api.query(query)
        return tables

    def process(self, data, data_delay):
        start_time = time()
        # concatenate last 4 seconds waveform with current waveform
        key = f"{data['station']}-{data['channel']}"
        if key in self.last_waveform:
            data['data'] = self.last_waveform[key] + data['data']
            data['start_time'] = data['start_time'] - 4
            data['npts'] = len(data['data'])
            data['sample_cnt'] = len(data['data'])
            data['num_samples'] = len(data['data'])

        sampling_rate = data['sampling_rate']
        ratio = sampling_rate / 20
        new_length = int(len(data['data']) / ratio)
        if new_length >= 160:
            trace = self.setTrace(data)
            self.predict(trace)
            # delete last 4 seconds waveform
            self.last_waveform[key] = []

        # print(f"Process Time: {time() - start_time}")
        print(f"Delay Kafka: {data_delay}\tDelay Start: {start_time - data['data_provider_time']}\tProcess Time: {time() - start_time}")

    def connectConsumer(self):
        for msg in self.consumer:
            data = msg.value
            data_delay = time() - data['data_provider_time']

            # concate last 4 seconds waveform with current waveform
            # self.process(data)
            self.executor.submit(self.process, data, data_delay)
            # save only last 4 seconds waveform
            key = f"{data['station']}-{data['channel']}"
            if key in self.last_waveform:
                self.last_waveform[key] = self.last_waveform[key] + data['data']
            else:
                self.last_waveform[key] = data['data']

            # check if last 4 seconds waveform
            cut_length = int(4 * data['sampling_rate'])
            if len(self.last_waveform[key]) > cut_length:
                self.last_waveform[key] = self.last_waveform[key][-cut_length:]

if __name__ == '__main__':
    influxdb_url = "http://influxdb:8086"
    influxdb_token = "eFWu0UGcCzvGAX1w-z43heHjfDk8swujfryImhIsTrAkNJOgfMRSYsgYVki-QTiWHDwKLJtxsSnCmHhxisCN1w=="
    influxdb_org = "owner"
    influxdb_bucket = "eews"

    bootstrap_servers = 'kafka:9092'
    kafka_topic = 'loc_mag_topic'
    num_partitions = 3
    replication_factor = 1

    traceConsumer = TraceConsumer()
    server = 'kafka:9092'
    topic = 'p_wave_topic'

    while not traceConsumer.topic_exists(topic, server):
        sleep(3)

    traceConsumer.create_topic(kafka_topic, num_partitions, replication_factor, bootstrap_servers)

    traceConsumer.configureConnection('p_wave_topic', 'trace_group', 'kafka:9092')
    traceConsumer.configureProducer(server)
    traceConsumer.connectConsumer()