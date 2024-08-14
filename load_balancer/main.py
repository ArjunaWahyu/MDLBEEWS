import json
from kafka import KafkaConsumer
from kafka.admin import KafkaAdminClient
from time import sleep
import requests

class TraceConsumer:
  def __init__(self):
    self.consumer = None
    self.producer = None

  def configureConnection(self, topic, group, server):
    self.consumer = KafkaConsumer(
      topic,
      group_id=group,
      bootstrap_servers=server,
      value_deserializer=lambda x: json.loads(x.decode('utf-8')),
      key_deserializer=lambda x: json.loads(x.decode('utf-8'))
    )

  def topic_exists(selft, topic_name, server):
      kafkaAdminClient = KafkaAdminClient(bootstrap_servers=server)
      is_topic_exist = topic_name in kafkaAdminClient.list_topics()
      print(f"Topic '{topic_name}' exists: {is_topic_exist}")
      return is_topic_exist

  def connectConsumer(self):
    for msg in self.consumer:
      data = msg.value
      print(f"Partition: {msg.partition},\tOffset: {msg.offset},\tStation: {data['station']},\tChannel: {data['channel']}")
      response = requests.post('http://p_wave_detector_load_balance:8004/trace', json=data)

if __name__ == '__main__':
  consumer = TraceConsumer()
  server = 'kafka:9092'
  topic = 'p_wave_topic'

  while not consumer.topic_exists(topic, server):
    sleep(3)

  consumer.configureConnection('p_wave_topic', 'load_balancer_group', 'kafka:9092')
  consumer.connectConsumer()
