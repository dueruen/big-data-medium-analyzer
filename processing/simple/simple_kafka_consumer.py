#######################
# SIMPLE test consumer
#######################
from pykafka import KafkaClient

# Config
bootstrap_servers = "10.123.252.211:9092,10.123.252.212:9092,10.123.252.213:9092"
kafka_topic_name = "test"
data_encoding = 'utf-8'

client = KafkaClient(bootstrap_servers)
topic = client.topics[kafka_topic_name]
consumer = topic.get_simple_consumer()
for msg in consumer:
        print("%s [key=%s, id=%s, offset=%s]" %(msg.value, msg.partition_key, msg.partition_id, msg.offset))