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

class TraceConsumer:
    def __init__(self):
        self.consumer = None
        self.producer = None
        self.model = tf.keras.models.load_model(
            './model_p_wave.h5', compile=False)
        self.query_api = self.connectInfluxDB()
        self.last_waveform = {}

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
        try:
            new_topic = NewTopic(
                name=kafka_topic,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
                # topic_configs=topic_config
                )
            kafkaAdminClient = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
            # add partition kafka
            try:
                kafkaAdminClient.create_topics(new_topics=[new_topic])
                print(f"Creating topic '{kafka_topic}'...")
            except Exception as e:
                kafkaAdminClient.delete_topics(topics=[kafka_topic])
                kafkaAdminClient.create_topics(new_topics=[new_topic])
                print(f"Topic '{kafka_topic}' already exists. Deleting and recreating...")
            sleep(3)
            if self.topic_exists(kafka_topic, bootstrap_servers):
                print(f"Topic '{kafka_topic}' created successfully.")
        except Exception as e:
            print(f"[Create Kafka Topic] Error: {e}")

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
                if np.all(predictions_p_wave[i:i + n] >= 0.9):
                    p_wave_time = trace.stats.starttime.timestamp + i * trace.stats.delta
                    print(
                        f"Station: {trace.stats.station},\tChannel: {trace.stats.channel},\tSampling Rate: {trace.stats.sampling_rate},\tP Wave Detected at time: {p_wave_time}")
                    # get 4 seconds data before p wave time and 4 seconds data after p wave time
                    p_wave_waveform = trace.data[i - 80:i + 80]
                    # send to kafka
                    data = {
                        'network': trace.stats.network,
                        'station': trace.stats.station,
                        'location': trace.stats.location,
                        'channel': trace.stats.channel,
                        'p_wave_time': p_wave_time,
                        'data_provider_time': trace.stats.endtime.timestamp,
                        'p_wave_detector_time': time(),
                        'data': p_wave_waveform.tolist()
                    }
                    self.producer.send('p_wave_topic', data, key=f"{data['station']}-{data['channel']}")
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

    def process(self, data):
        # # read 4 seconds data before start_time from influxdb
        # start_time = int((data['start_time']) * 1e9 - 4 * 1e9)
        # end_time = int(data['start_time'] * 1e9)
        # tables = self.readInfluxDB(
        #     data['station'], data['channel'], start_time, end_time)
        # if len(tables) > 0:
        #     # get list of data from influxdb
        #     influxdb_data = [record.get_value() for table in tables for record in table.records]
        #     print(f"frequency: {data['sampling_rate']}\tLength 4 seconds: {data['sampling_rate'] * 4}\tData from InfluxDB: {len(influxdb_data)}")
        #     # concatenate list data from kafka and influxdb
        #     data['data'] = influxdb_data + data['data']

        # concatenate last 4 seconds waveform with current waveform
        key = f"{data['station']}-{data['channel']}"
        # print(f"{key}\tBefore Length: {len(data['data'])}\tBefore Start Time: {data['start_time']}")
        if key in self.last_waveform:
            data['data'] = self.last_waveform[key] + data['data']
            data['start_time'] = data['start_time'] - 4
            data['npts'] = len(data['data'])
            data['sample_cnt'] = len(data['data'])
            data['num_samples'] = len(data['data'])
        # print(f"{key}\tAfter Length: {len(data['data'])}\tAfter Start Time: {data['start_time']}")

        sampling_rate = data['sampling_rate']
        ratio = sampling_rate / 20
        new_length = int(len(data['data']) / ratio)
        # print(f"{key}\tLength: {len(data['data'])}\tNew Length: {new_length}")
        if new_length >= 160:
            trace = self.setTrace(data)
            self.predict(trace)
            # delete last 4 seconds waveform
            self.last_waveform[key] = []

    def connectConsumer(self):
        for msg in self.consumer:
            data = msg.value
            if data['channel'].endswith('Z'):
                print(f"Delay: {time() - data['data_provider_time']}")
                # concate last 4 seconds waveform with current waveform
                self.process(data)
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

            # sampling_rate = data['sampling_rate']
            # ratio = sampling_rate / 20
            # new_length = int(len(data['data']) / ratio)
            # if data['channel'].endswith('Z') and new_length >= 160:
            #     try:
            #         # read 4 seconds data before start_time from influxdb
            #         start_time = int((data['start_time']) * 1e9 - 4 * 1e9)
            #         end_time = int(data['start_time'] * 1e9)
            #         tables = self.readInfluxDB(
            #             data['station'], data['channel'], start_time, end_time)
            #         if len(tables) > 0:
            #             # get list of data from influxdb
            #             influxdb_data = [record.get_value() for table in tables for record in table.records]
            #             print(f"frequency: {data['sampling_rate']}\tLength 4 seconds: {data['sampling_rate'] * 4}\tData from InfluxDB: {len(influxdb_data)}")

                    # trace = self.setTrace(data)
                    # self.predict(trace)

                    # print station channel sampling rate from trace
                    # print(f"Station: {trace.stats.station},\tChannel: {trace.stats.channel},\tSampling Rate: {trace.stats.sampling_rate}")
                    # print(f"Partition: {msg.partition},\tOffset: {msg.offset},\tKey: {msg.key},\tStation: {data['station']},\tChannel: {data['channel']},\tsampling_rate: {data['sampling_rate']}")
                    # print(f"Partition: {msg.partition},\tOffset: {msg.offset},\tStation: {data['station']},\tChannel: {data['channel']},\tsampling_rate: {data['sampling_rate']}")
                # except Exception as e:
                #     print(
                #         f"Error connectConsumer {data['station']}\t{data['channel']}:\t{e}")

if __name__ == '__main__':
    influxdb_url = "http://influxdb:8086"
    influxdb_token = "eFWu0UGcCzvGAX1w-z43heHjfDk8swujfryImhIsTrAkNJOgfMRSYsgYVki-QTiWHDwKLJtxsSnCmHhxisCN1w=="
    influxdb_org = "owner"
    influxdb_bucket = "eews"

    bootstrap_servers = 'kafka:9092'
    kafka_topic = 'p_wave_topic'
    num_partitions = 3
    replication_factor = 1

    traceConsumer = TraceConsumer()
    server = 'kafka:9092'
    topic = 'trace_topic'

    while not traceConsumer.topic_exists(topic, server):
        sleep(3)

    traceConsumer.create_topic(kafka_topic, num_partitions, replication_factor, bootstrap_servers)

    traceConsumer.configureConnection('trace_topic', 'trace_group', 'kafka:9092')
    traceConsumer.connectConsumer()