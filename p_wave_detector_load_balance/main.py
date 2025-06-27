import json
import asyncio
from time import sleep, time
from fastapi import FastAPI
import uvicorn
import obspy
import numpy as np
import tensorflow as tf
from kafka import KafkaProducer
from kafka.admin import KafkaAdminClient, NewTopic
import logging
from concurrent.futures import ThreadPoolExecutor
from cachetools import LRUCache

app = FastAPI()
last_waveform = LRUCache(maxsize=6000)
# last_waveform = {}
model = tf.keras.models.load_model('./model_p_wave.h5', compile=False)
# bootstrap_servers = 'kafka:9092'
bootstrap_servers = ['kafka1:9092', 'kafka2:9093']
kafka_topic = 'loc_mag_topic'
num_partitions = 1
replication_factor = 1

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def topic_exists(topic_name, server):
    kafkaAdminClient = KafkaAdminClient(bootstrap_servers=server)
    is_topic_exist = topic_name in kafkaAdminClient.list_topics()
    logger.info(f"Topic '{topic_name}' exists: {is_topic_exist}")
    return is_topic_exist

def create_topic(kafka_topic, num_partitions, replication_factor, bootstrap_servers):
    kafkaAdminClient = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    if not topic_exists(kafka_topic, bootstrap_servers):
        try:
            new_topic = NewTopic(
                name=kafka_topic,
                num_partitions=num_partitions,
                replication_factor=replication_factor
            )
            logger.info(f"Creating topic '{kafka_topic}'...")
            kafkaAdminClient.create_topics(new_topics=[new_topic])
            logger.info(f"Topic '{kafka_topic}' created successfully.")
        except Exception as e:
            logger.error(f"Error creating topic '{kafka_topic}': {e}")
            sleep(3)
            create_topic(kafka_topic, num_partitions, replication_factor, bootstrap_servers)

# Ensure the Kafka topic exists
create_topic(kafka_topic, num_partitions, replication_factor, bootstrap_servers)

producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    key_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def set_trace(data):
    trace = obspy.Trace(np.array(data['data']))
    trace.stats.update({
        'network': data['network'],
        'station': data['station'],
        'location': data['location'],
        'channel': data['channel'],
        'starttime': obspy.UTCDateTime(data['start_time']),
        'sampling_rate': data['sampling_rate'],
        'delta': data['delta'],
        'npts': data['npts'],
        'calib': data['calib'],
        'dataquality': data['data_quality'],
        'numsamples': data['num_samples'],
        'samplecnt': data['sample_cnt'],
        'sampletype': data['sample_type']
    })
    trace.interpolate(sampling_rate=20)
    return trace

def preprocessing_p_wave(data: np.ndarray):
    return data / np.max(np.abs(data), axis=0)

async def predict(trace, data_provider_time):
    try:
        converter_np_array = np.stack([trace.data]*3, axis=-1)
        sliding_array = np.lib.stride_tricks.sliding_window_view(
            converter_np_array, (160, 3)).reshape(-1, 160, 3)

        preprocessed_array = preprocessing_p_wave(sliding_array)
        
        # Perform prediction in a thread pool to avoid blocking the event loop
        predictions_p_wave = await asyncio.get_event_loop().run_in_executor(
            None, lambda: model.predict(preprocessed_array, verbose=0)
        )

        idx, max_value = max(
            ((i, np.max(predictions_p_wave[i:i + 20])) for i in range(len(predictions_p_wave) - 19)),
            key=lambda x: x[1],
            default=(0, 0)
        )

        if max_value == 0 or max_value < 0.95:
            return

        p_wave_time = trace.stats.starttime.timestamp + idx * trace.stats.delta
        p_wave_waveform = trace.data[idx + 40:idx + 120].tolist()

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

        # Send the data asynchronously in the executor
        await asyncio.get_event_loop().run_in_executor(
            None, lambda: producer.send(kafka_topic, data, key=f"{data['station']}-{data['channel']}")
        )
        producer.flush()

        # Explicitly delete large objects to free up memory
        del converter_np_array
        del sliding_array
        del preprocessed_array
        del predictions_p_wave

    except Exception as e:
        logger.error(f"Error predict {trace.stats.station} {trace.stats.channel} {len(trace.data)}: {e}")

async def process(data, data_delay):
    start_time = time()
    key = f"{data['station']}-{data['channel']}"

    if key in last_waveform:
        data['data'] = last_waveform[key] + data['data']
        data['start_time'] -= 4
        data['npts'] = len(data['data'])
        data['sample_cnt'] = len(data['data'])
        data['num_samples'] = len(data['data'])

    sampling_rate = data['sampling_rate']
    ratio = sampling_rate / 20
    new_length = int(len(data['data']) / ratio)
    if new_length >= 160:
        trace = set_trace(data)
        await predict(trace, data['data_provider_time'])
        last_waveform[key] = []

    logger.info(f"Delay Kafka: {data_delay}\tDelay Start: {start_time - data['data_provider_time'] - data_delay}\tProcess Time: {time() - start_time}")

@app.post("/trace")
async def trace(data: dict):
    data_delay = time() - data['data_provider_time']

    # Schedule the processing task asynchronously
    asyncio.create_task(process(data, data_delay))

    key = f"{data['station']}-{data['channel']}"

    if key in last_waveform:
        last_waveform[key] += data['data']
    else:
        last_waveform[key] = data['data']

    cut_length = int(4 * data['sampling_rate'])
    if len(last_waveform[key]) > cut_length:
        last_waveform[key] = last_waveform[key][-cut_length:]

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=8000)
