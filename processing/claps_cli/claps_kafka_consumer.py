#######################
# Claps consumer
#######################
from pykafka import KafkaClient

# Config
bootstrap_servers = "node-master:9092,node1:9092,node2:9092"
kafka_topic_name = "claps_predicted"
data_encoding = 'utf-8'

client = KafkaClient(bootstrap_servers)
topic = client.topics[kafka_topic_name]
consumer = topic.get_simple_consumer()
for msg in consumer:
  print("%s [key=%s, id=%s, offset=%s]" %(msg.value, msg.partition_key, msg.partition_id, msg.offset))