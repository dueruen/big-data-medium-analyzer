import json
import datetime
from pykafka import KafkaClient
import base64
import csv

# Config
bootstrap_servers = '10.123.252.211:9092,10.123.252.212:9092,10.123.252.213:9092'
kafka_topic_name = "test_json"
data_encoding = 'utf-8'

#client = KafkaClient(bootstrap_servers)
#topic = client.topics[kafka_topic_name]

# id,url,title,subtitle,image,claps,responses,reading_time,publication,date

def readFile(filePath):
  with open(filePath, "rb") as fid:
    data = fid.read()
    b64_bytes = base64.b64encode(data)
    return b64_bytes.decode()

count = 0
with open('data/medium_data.csv', newline='') as csvfile:
  spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
  for row in spamreader:
    if count == 0:
      count += 1
      continue

    b64_string = readFile(f'./data/images/{row[4]}')

    data_set = {
      "id": row[0], 
      "url": row[1], 
      "title": row[2], 
      "subtitle": row[3], 
      "image": b64_string, 
      "claps": row[5], 
      "responses": row[6], 
      "reading_time": row[7], 
      "publication": row[8], 
      "date": row[9]}
    
    json_dump = json.dumps(data_set)
    # print(json_dump)

    with topic.get_sync_producer(max_request_size = 15728640) as producer:
      producer.produce(bytes(json_dump, data_encoding))
    count+= 1 
    # if count == 5:
    #   break