from multi_process import main
# from multi_thread import main
# from sequence import main
from kafka.admin import KafkaAdminClient, NewTopic
from time import sleep
from utils.util import topic_exists, check_kafka_connection

if __name__ == '__main__':
    bootstrap_servers = 'kafka:9092'
    kafka_topic = 'trace_topic'
    num_partitions = 3
    replication_factor = 1

    while not check_kafka_connection(bootstrap_servers):
        sleep(3)

    try:
        kafkaAdminClient = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
        new_topic = NewTopic(
            name=kafka_topic,
            num_partitions=num_partitions,
            replication_factor=replication_factor,
        )
        print(f"Creating topic '{kafka_topic}'...")
        kafkaAdminClient.create_topics(new_topics=[new_topic])
        print(f"Topic '{kafka_topic}' created successfully.")
    except Exception as e:
        print(f"Error creating topic '{kafka_topic}': {e}")
        
    if topic_exists(kafka_topic, bootstrap_servers):
        print(f"Topic '{kafka_topic}' created successfully.")

    main(station_path='./data/stations.json',num_processes=30, num_station_configs=6000)