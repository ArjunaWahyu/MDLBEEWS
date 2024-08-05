import json
from kafka import KafkaAdminClient, KafkaProducer

def get_station_configs(station_path, num_seednames=6000):
    with open(station_path, 'r') as file:
        stations = json.load(file)

    station_configs = []
    countSeednames = 0
    isStopped = False
    for station in stations:
        for seedname in station['seednames']:
            station_configs.append({
                'network': station['network'],
                'station': station['station_name'],
                'seedname': seedname
            })
            countSeednames += 1

            if countSeednames == num_seednames:
                isStopped = True
                break

        if isStopped:
            break

    return station_configs

def get_station_by_network(station_path, network, num_seednames=6000):
    added_station_channels = []
    with open(station_path, 'r') as file:
        stations = json.load(file)

    station_configs = []
    countSeednames = 0
    isStopped = False
    for station in stations:
        if station['network'] in network:
            for seedname in station['seednames']:
                if f'{station["network"]}.{station["station_name"]}.{seedname}' in added_station_channels or not seedname.endswith('Z'):
                    continue
                station_configs.append({
                    'network': station['network'],
                    'station': station['station_name'],
                    'seedname': seedname
                })
                added_station_channels.append(f'{station["network"]}.{station["station_name"]}.{seedname}')
                
                countSeednames += 1
                
                if countSeednames == num_seednames:
                    isStopped = True
                    break
                
            if isStopped:
                break

    return station_configs

def topic_exists(topic_name, bootstrap_servers):
    kafkaAdminClient = KafkaAdminClient(bootstrap_servers=bootstrap_servers)
    is_topic_exist = topic_name in kafkaAdminClient.list_topics()
    print(f"Topic '{topic_name}' exists: {is_topic_exist}")
    return is_topic_exist

def check_kafka_connection(bootstrap_servers):
    try:
        producer = KafkaProducer(bootstrap_servers=bootstrap_servers)
        is_connected = producer.bootstrap_connected()
        producer.close()
        print(f"Kafka connection established: {is_connected}")
        return is_connected
    except Exception as e:
        print(f"Error: {e}")
        return False