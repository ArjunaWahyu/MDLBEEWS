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
        # topic_config = {
        #     # cleanup.policy is used to set the topic retention policy to delete
        #     "cleanup.policy": "delete",
        #     # retention.ms is used to set the time to wait before deleting a message
        #     "retention.ms": 10000,  # 10 detik
        #     # segment.ms is used to set the time to wait before creating a new log segment
        #     "segment.ms": 10000,  # 10 detik
        #     # Minimize the size of each log segment file to ensure rapid log segment rotation
        #     "segment.bytes": 1024,  # 1 KB
        #     # Delete log segments as soon as possible
        #     "log.retention.bytes": 1,  # 1 byte (effectively immediate deletion)
        #     # Flush the log at least once every 10 seconds
        #     "flush.ms": 10000,  # 10 detik
        #     # Flush the log to disk after every message (minimize disk usage)
        #     "flush.messages": 1,
        #     # Minimize the amount of data retained
        #     "log.retention.check.interval.ms": 1000  # Check for log retention every second
        # }
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
        if topic_exists(kafka_topic, bootstrap_servers):
            print(f"Topic '{kafka_topic}' created successfully.")
    except Exception as e:
        print(f"[Create Kafka Topic] Error: {e}")

    main(station_path='./data/stations.json',num_processes=30, num_station_configs=6000)