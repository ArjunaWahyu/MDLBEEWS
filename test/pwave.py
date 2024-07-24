# import json
# from kafka import KafkaConsumer
# from kafka.admin import KafkaAdminClient
# from time import sleep
# import obspy
# import numpy as np
# import tensorflow as tf


# class TraceConsumer:
#     def __init__(self):
#         self.consumer = None
#         self.producer = None
#         self.model = tf.keras.models.load_model('./model_p_wave.h5', compile=False)

#     def configureConnection(self, topic, group, server):
#         self.consumer = KafkaConsumer(
#             topic,
#             group_id=group,
#             bootstrap_servers=server,
#             value_deserializer=lambda x: json.loads(x.decode('utf-8')),
#             key_deserializer=lambda x: json.loads(x.decode('utf-8'))
#         )

#     def topic_exists(selft, topic_name, server):
#         kafkaAdminClient = KafkaAdminClient(bootstrap_servers=server)
#         is_topic_exist = topic_name in kafkaAdminClient.list_topics()
#         print(f"Topic '{topic_name}' exists: {is_topic_exist}")
#         return is_topic_exist

#     def setTrace(self, data):
#         trace = obspy.Trace(np.array(data['data']))
#         trace.stats.network = data['network']
#         trace.stats.station = data['station']
#         trace.stats.location = data['location']
#         trace.stats.channel = data['channel']
#         trace.stats.starttime = obspy.UTCDateTime(data['start_time'])
#         # trace.stats.endtime = obspy.UTCDateTime(data['end_time'])
#         trace.stats.sampling_rate = data['sampling_rate']
#         trace.stats.delta = data['delta']
#         trace.stats.npts = data['npts']
#         trace.stats.calib = data['calib']
#         trace.stats.dataquality = data['data_quality']
#         trace.stats.numsamples = data['num_samples']
#         trace.stats.samplecnt = data['sample_cnt']
#         trace.stats.sampletype = data['sample_type']

#         # interpolate to 20 Hz
#         trace.interpolate(sampling_rate=20)

#         return trace

#     def preprocessingPWave(self, data: np.ndarray):
#         return data / np.max(np.abs(data), axis=0)

#     def predict(self, trace):
#         try:
#             # duplicate the trace to 3 channels
#             converter_np_array = np.array(
#                 [trace.data, trace.data, trace.data]).T
#             sliding_array = np.lib.stride_tricks.sliding_window_view(
#                 converter_np_array, (160, 3)).reshape(-1, 160, 3)

#             # preprocessing
#             preprocessed_array = np.apply_along_axis(
#                 self.preprocessingPWave, axis=1, arr=sliding_array)

#             # print(f"Preprocessed Array {trace.stats.station}: {preprocessed_array.shape}")
#             # print(f"type: {type(preprocessed_array)}")

#             # melakukan prediksi p wave dengan model Machine Learning
#             predictions_p_wave = self.model.predict(preprocessed_array,verbose=0)
#             print(f"Predictions P Wave {trace.stats.station}: {predictions_p_wave.shape}")

#             # # mencari index dari prediksi p wave
#             # index_p_wave = np.argmax(predictions_p_wave)
#             # print(f"Index P Wave: {index_p_wave}")
#             # print(f"Predicted P Wave: {predictions_p_wave[index_p_wave]}")

#         except Exception as e:
#             print(f"Error predict {trace.stats.station} {trace.stats.channel} {len(trace.data)}: {e}")

#     def connectConsumer(self):

#         for msg in self.consumer:
#             data = msg.value
#             if not data['channel'].endswith('Z'):
#                 continue
#             try:
#                 trace = self.setTrace(data)
#                 self.predict(trace)

#                 # print station channel sampling rate from trace
#                 # print(f"Station: {trace.stats.station},\tChannel: {trace.stats.channel},\tSampling Rate: {trace.stats.sampling_rate}")
#                 # print(f"Partition: {msg.partition},\tOffset: {msg.offset},\tKey: {msg.key},\tStation: {data['station']},\tChannel: {data['channel']},\tsampling_rate: {data['sampling_rate']}")
#                 # print(f"Partition: {msg.partition},\tOffset: {msg.offset},\tStation: {data['station']},\tChannel: {data['channel']},\tsampling_rate: {data['sampling_rate']}")
#             except Exception as e:
#                 print(f"Error connectConsumer {data['station']}\t{data['channel']}:\t{e}")


# if __name__ == '__main__':
#     consumer = TraceConsumer()
#     server = 'kafka:9092'
#     topic = 'trace_topic'

#     while not consumer.topic_exists(topic, server):
#         sleep(3)

#     consumer.configureConnection('trace_topic', 'trace_group', 'kafka:9092')
#     consumer.connectConsumer()

from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS
import time

influxdb_url = "http://localhost:8086"
influxdb_token = "eFWu0UGcCzvGAX1w-z43heHjfDk8swujfryImhIsTrAkNJOgfMRSYsgYVki-QTiWHDwKLJtxsSnCmHhxisCN1w=="
influxdb_org = "owner"
influxdb_bucket = "eews"

client = InfluxDBClient(
    url=influxdb_url, token=influxdb_token, org=influxdb_org)
query_api = client.query_api()


def readInfluxDB(station, channel, start_time, end_time):
    influxdb_bucket = "eews"
    influxdb_measurement = "wave"
    query = f'from(bucket: "{influxdb_bucket}") |> range(start: {start_time}, stop: {end_time}) |> filter(fn: (r) => r["_measurement"] == "{influxdb_measurement}") |> filter(fn: (r) => r["stat"] == "{station}") |> filter(fn: (r) => r["_field"] == "{channel}")'

    tables = query_api.query(query)
    return tables

# get 4 second data from influxdb
end_time = int(time.time() * 1e9)
start_time = int((time.time() - 4) * 1e9)
print(start_time, end_time)
print("delta time: ", (end_time - start_time) / 1e9)
tables = readInfluxDB('BBJI', 'BHE', start_time, end_time)
if len(tables) > 0:
    wave = []
    for table in tables:
        for record in table.records:
            wave.append(record.get_value())

    print(len(wave))