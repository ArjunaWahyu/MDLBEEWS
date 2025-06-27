from multi_process import main
# from multi_thread import main
# from sequence import main
from kafka.admin import KafkaAdminClient, NewTopic
from time import sleep, time
from utils.util import topic_exists, check_kafka_connection
from random import randint
from kafka import KafkaProducer
import json

network = ['GE', 'IA']
station = ['BBJI', 'JAGI', 'SMRI', 'PARI', 
            'KUJI', 'BKB', 'TNTI', 'KUJI']
location = ''
channel = ['BHZ', 'BHN', 'BHE', 
            'SHZ', 'SHN', 'SHE', 
            'HHZ', 'HHN', 'HHE',
            'EHZ', 'EHN', 'EHE'
            'LHZ', 'LHN', 'LHE',
            'VHZ', 'VHN', 'VHE',
            'UHZ', 'UHN', 'UHE',
            'CHZ', 'CHN', 'CHE',
            'FHZ', 'FHN', 'FHE',
            'GZ', 'GN', 'GE',
            'DZ', 'DN', 'DE',
            'HZ', 'HN', 'HE',
            'IZ', 'IN', 'IE',
            'JZ', 'JN', 'JE',
            'KZ', 'KN', 'KE',
            'LZ', 'LN', 'LE',
            'MZ', 'MN', 'ME',
            'NZ', 'NN', 'NE',
            'OZ', 'ON', 'OE',
            'PZ', 'PN', 'PE',
            'QZ', 'QN', 'QE',
            'RZ', 'RN', 'RE',
            'SZ', 'SN', 'SE',
            'TZ', 'TN', 'TE',
            'UZ', 'UN', 'UE',
            'VZ', 'VN', 'VE',
            'WZ', 'WN', 'WE',
            'XZ', 'XN', 'XE',
            'YZ', 'YN', 'YE',
            'ZZ', 'ZN', 'ZE',
            '1Z', '1N', '1E',
            '2Z', '2N', '2E',
            '3Z', '3N', '3E',
            '4Z', '4N', '4E',
            '5Z', '5N', '5E',    
            '6Z', '6N', '6E',
            '7Z', '7N', '7E',
            '8Z', '8N', '8E',
            '9Z', '9N', '9E',
            '0Z', '0N', '0E',
            'AZ', 'AN', 'AE']
sampling_rate = 100
delta = 0.01
npts = 900
calib = 1.0
data_quality = 'D'
num_samples = 900
sample_cnt = 900
sample_type = 'i'
def generate_waveform():
    starttime = time() - 9
    endtime = time()

    # generate random waveform
    wave = [randint(-1000, 1000) for i in range(npts)]

    data = {
        'network': network[randint(0, 1)],
        'station': station[randint(0, 7)],
        'location': location,
        'channel': channel[randint(0, 119)],
        'start_time': starttime,
        'end_time': endtime,
        'sampling_rate': sampling_rate,
        'delta': delta,
        'npts': npts,
        'calib': calib,
        'data_quality': data_quality,
        'num_samples': num_samples,
        'sample_cnt': sample_cnt,
        'sample_type': sample_type,
        'data_provider_time': time(),
        'data': wave
    }
    return data

if __name__ == '__main__':
    print("Starting data provider...")

    # bootstrap_servers = 'kafka:9092'
    bootstrap_servers = ['kafka1:9092', 'kafka2:9093']
    bootstrap_servers2 = ['kafka3:9094']
    kafka_topic = 'trace_topic'
    # kafka_topic = 'p_wave_topic'
    kafka_topic2 = 'p_wave_topic'
    num_partitions = 3
    num_partitions2 = 5
    replication_factor = 2
    replication_factor2 = 1

    while not check_kafka_connection(bootstrap_servers):
        sleep(3)

    while not topic_exists(kafka_topic, bootstrap_servers):
        try:
            kafkaAdminClient = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
            new_topic = NewTopic(
                name=kafka_topic,
                num_partitions=num_partitions,
                replication_factor=replication_factor,
            )
            if not topic_exists(kafka_topic, bootstrap_servers):
                print(f"Creating topic '{kafka_topic}'...")
                kafkaAdminClient.create_topics(new_topics=[new_topic])
                print(f"Topic '{kafka_topic}' created successfully.")
        except Exception as e:
            print(f"Error creating topic '{kafka_topic}': {e}")

    while not topic_exists(kafka_topic2, bootstrap_servers2):
        try:
            kafkaAdminClient = KafkaAdminClient(bootstrap_servers=bootstrap_servers2)
            new_topic2 = NewTopic(
                name=kafka_topic2,
                num_partitions=num_partitions2,
                replication_factor=replication_factor2,
            )
            if not topic_exists(kafka_topic2, bootstrap_servers2):
                print(f"Creating topic '{kafka_topic2}'...")
                kafkaAdminClient.create_topics(new_topics=[new_topic2])
                print(f"Topic '{kafka_topic2}' created successfully.")
        except Exception as e:
            print(f"Error creating topic '{kafka_topic2}': {e}")

    producer = KafkaProducer(
            # bootstrap_servers='kafka:9092',
            bootstrap_servers=['kafka1:9092', 'kafka2:9093', 'kafka3:9094'],
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            key_serializer=lambda v: json.dumps(v).encode('utf-8'),
        )

    sleep(5)

    # throughput 125 data points per second
    throughput = 125

    # time to sleep between each data point
    sleep_time = 1/throughput

    while True:
        start_time = time()
        data = generate_waveform()
        print(f"Sending data {data['station']}\t{data['channel']}")

        producer.send('trace_topic', data, key=f"{data['station']}-{data['channel']}")
        producer.flush()

        if data['channel'].endswith('Z'):
            producer.send('p_wave_topic', data, key=f"{data['station']}-{data['channel']}")
            producer.flush()

        end_time = time()
        sleep(max(0, sleep_time - (end_time - start_time)))