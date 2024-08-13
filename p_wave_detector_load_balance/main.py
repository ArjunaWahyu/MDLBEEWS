import json
from kafka import KafkaConsumer, KafkaProducer
from kafka.admin import KafkaAdminClient
from time import sleep, time
import obspy
import numpy as np
import tensorflow as tf
from kafka.admin import KafkaAdminClient, NewTopic
import concurrent.futures
import threading
from fastapi import FastAPI
import uvicorn

app = FastAPI()
last_waveform = {}
model = tf.keras.models.load_model('./model_p_wave.h5', compile=False)
bootstrap_servers = 'kafka:9092'
kafka_topic = 'loc_mag_topic'
num_partitions = 1
replication_factor = 1

def topic_exists(topic_name, server):
    kafkaAdminClient = KafkaAdminClient(bootstrap_servers=server)
    is_topic_exist = topic_name in kafkaAdminClient.list_topics()
    print(f"Topic '{topic_name}' exists: {is_topic_exist}")
    return is_topic_exist


def create_topic(kafka_topic, num_partitions, replication_factor, bootstrap_servers):
    kafkaAdminClient = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    while not topic_exists(kafka_topic, bootstrap_servers):
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

while not topic_exists(kafka_topic, bootstrap_servers):
    create_topic(kafka_topic, num_partitions, replication_factor, bootstrap_servers)
    sleep(3)

producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def setTrace(data):
    trace = obspy.Trace(np.array(data['data']))
    trace.stats.network = data['network']
    trace.stats.station = data['station']
    trace.stats.location = data['location']
    trace.stats.channel = data['channel']
    trace.stats.starttime = obspy.UTCDateTime(data['start_time'])
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

def preprocessingPWave(data: np.ndarray):
    return data / np.max(np.abs(data), axis=0)

def predict(trace, data_provider_time):
    try:
        # duplicate the trace to 3 channels
        converter_np_array = np.array(
            [trace.data, trace.data, trace.data]).T
        sliding_array = np.lib.stride_tricks.sliding_window_view(
            converter_np_array, (160, 3)).reshape(-1, 160, 3)

        # preprocessing
        preprocessed_array = np.apply_along_axis(
            preprocessingPWave, axis=1, arr=sliding_array)

        # melakukan prediksi p wave dengan model Machine Learning
        predictions_p_wave = model.predict(
            preprocessed_array, verbose=0)

        # get max value and index of max value from predictions 20 points
        idx = 0
        max_value = 0
        n = 20
        for i in range(len(predictions_p_wave) - n + 1):
            if np.all(predictions_p_wave[i:i + n] >= 0.9):
                p_wave_time = trace.stats.starttime.timestamp + i * trace.stats.delta
                if max_value < np.max(predictions_p_wave[i:i + n]):
                    max_value = np.max(predictions_p_wave[i:i + n])
                    idx = i
        if max_value == 0:
            return

        # get 4 seconds data before p wave time and 4 seconds data after p wave time
        p_wave_waveform = trace.data.tolist()[idx + 40:idx + 120]
        # send to kafka
        data = {
            'network': trace.stats.network,
            'station': trace.stats.station,
            'location': trace.stats.location,
            'channel': trace.stats.channel,
            'sampling_rate': trace.stats.sampling_rate,
            'p_wave_time': p_wave_time,
            'data_provider_time': data_provider_time,
            'p_wave_detector_time': time(),
            'data': p_wave_waveform
        }
        # print(data)

        producer.send('loc_mag_topic', data, key=f"{data['station']}-{data['channel']}")
        producer.flush()

        data = None

    except Exception as e:
        print(
            f"Error predict {trace.stats.station} {trace.stats.channel} {len(trace.data)}: {e}")

def process(data, data_delay):
    start_time = time()
    # concatenate last 4 seconds waveform with current waveform
    key = f"{data['station']}-{data['channel']}"
    if key in last_waveform:
        data['data'] = last_waveform[key] + data['data']
        data['start_time'] = data['start_time'] - 4
        data['npts'] = len(data['data'])
        data['sample_cnt'] = len(data['data'])
        data['num_samples'] = len(data['data'])

    sampling_rate = data['sampling_rate']
    ratio = sampling_rate / 20
    new_length = int(len(data['data']) / ratio)
    if new_length >= 160:
        trace = setTrace(data)
        predict(trace, data['data_provider_time'])
        # delete last 4 seconds waveform
        last_waveform[key] = []

    # print(f"Process Time: {time() - start_time}")
    print(f"Delay Kafka: {data_delay}\tDelay Start: {start_time - data['data_provider_time'] - data_delay}\tProcess Time: {time() - start_time}")

@app.post("/trace")
async def trace(data: dict):
    data_delay = time() - data['data_provider_time']

    # concate last 4 seconds waveform with current waveform
    # self.process(data)
    # self.executor.submit(self.process, data, data_delay)
    threading.Thread(target=process, args=(data, data_delay)).start()

    # save only last 4 seconds waveform
    key = f"{data['station']}-{data['channel']}"
    if key in last_waveform:
        last_waveform[key] = last_waveform[key] + data['data']
    else:
        last_waveform[key] = data['data']

    # check if last 4 seconds waveform
    cut_length = int(4 * data['sampling_rate'])
    if len(last_waveform[key]) > cut_length:
        last_waveform[key] = last_waveform[key][-cut_length:]

if __name__ == '__main__':    
    uvicorn.run(app, host="0.0.0.0", port=8000)