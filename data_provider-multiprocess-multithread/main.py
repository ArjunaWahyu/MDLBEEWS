from multi_process import main
from kafka.admin import KafkaAdminClient, NewTopic
from time import sleep
from utils.util import topic_exists, check_kafka_connection

if __name__ == '__main__':
    print("Starting data provider...")

    # bootstrap_servers = 'kafka:9092'
    bootstrap_servers = ['kafka1:9092', 'kafka2:9093']
    bootstrap_servers2 = ['kafka3:9094']
    kafka_topic = 'trace_topic'
    # kafka_topic = 'p_wave_topic'
    kafka_topic2 = 'p_wave_topic'
    num_partitions = 5
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

    while not topic_exists(kafka_topic2, bootstrap_servers):
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

    # while True:
    #     try:
    #         kafkaAdminClient = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    #         new_topic = NewTopic(
    #             name=kafka_topic,
    #             num_partitions=num_partitions,
    #             replication_factor=replication_factor,
    #         )
    #         new_topic2 = NewTopic(
    #             name=kafka_topic2,
    #             num_partitions=num_partitions,
    #             replication_factor=replication_factor,
    #         )
    #         if not topic_exists(kafka_topic, bootstrap_servers) and not topic_exists(kafka_topic2, bootstrap_servers):
    #             print(f"Creating topic '{kafka_topic}' and '{kafka_topic2}'...")
    #             kafkaAdminClient.create_topics(new_topics=[new_topic])
    #             # sleep(1)
    #             kafkaAdminClient.create_topics(new_topics=[new_topic2])
    #             print(f"Topic '{kafka_topic}' and '{kafka_topic2}' created successfully.")
    #     except Exception as e:
    #         print(f"Error creating topic '{kafka_topic}' and '{kafka_topic2}': {e}")

    #     if topic_exists(kafka_topic, bootstrap_servers) and topic_exists(kafka_topic2, bootstrap_servers):
    #         print(f"Topic '{kafka_topic}' and '{kafka_topic2}' exists")

    main(station_path='./data/stations.json',num_processes=30, num_station_configs=6000)