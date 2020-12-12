#######################
# SIMPLE test producer
#######################
import json
import datetime
from pykafka import KafkaClient
import base64

# Config
bootstrap_servers = '10.123.252.211:9092,10.123.252.212:9092,10.123.252.213:9092'
kafka_topic_name = "test_json"
data_encoding = 'utf-8'

client = KafkaClient(bootstrap_servers)
topic = client.topics[kafka_topic_name]

filename = "./tests/1.png"
with open(filename, "rb") as fid:
    data = fid.read()

b64_bytes = base64.b64encode(data)
b64_string = b64_bytes.decode()

data_set = {"id": 1, "url": "url", "title": "this is a title, blockchain, ai, beginner", "subtitle": "this is a subtitle, startup, startup nl, beginner, how to, beginner", "image": b64_string, "claps": 2, "responses": 3, "reading_time": 4, "publication": "publication", "date": "dateData"}
json_dump = json.dumps(data_set)
print(json_dump)

with topic.get_sync_producer() as producer:
    producer.produce(bytes(json_dump, data_encoding))

print("DONE")

