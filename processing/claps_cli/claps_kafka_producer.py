#######################
# claps producer
#######################
import json
import datetime
from pykafka import KafkaClient
import base64

# Config
bootstrap_servers = 'node-master:9092,node1:9092,node2:9092'
kafka_topic_name = "predict_claps"
data_encoding = 'utf-8'

client = KafkaClient(bootstrap_servers)
topic = client.topics[kafka_topic_name]

publication_options = {
    0 : "None",
    1 : "Towards Data Science",
    2 : "UX Collective",
    3 : "The Startup",
    4 : "The Writing Cooperative",
    5 : "Data Driven Investor",
    6 : "Better Humans",
    7 : "Better Marketing",
}
active = True

while active:
    print("")
    title = input("Title:: ")
    title = "this is a title, robot, ai, beginner" if title is '' else title

    subtitle = input("Subtitle:: ")
    subtitle = "this is a subtitle, startup, startup nl, beginner, how to, beginner" if subtitle is '' else subtitle

    imagePath = input("Image path:: ")
    imagePath = "../populate/data/images/3.png" if imagePath is '' else imagePath

    reading_time = input("Reading time (int):: ")
    reading_time = 2 if reading_time is '' else int(reading_time)

    print(publication_options)
    publication = input("Publication (int):: ")
    publication = 2 if publication is '' else int(publication)
    publication = publication_options.get(publication, "None")

    with open(imagePath, "rb") as fid:
        data = fid.read()

    b64_bytes = base64.b64encode(data)
    b64_string = b64_bytes.decode()

    data_set = {"title": title, "subtitle": subtitle, "image": b64_string, "reading_time": reading_time, "publication": publication}
    json_dump = json.dumps(data_set)
    #print(json_dump)

    with topic.get_sync_producer(max_request_size = 15728640) as producer:
        producer.produce(bytes(json_dump, data_encoding))

    print("Data sent")
    active_answer = input("Run again?? y or n  ")
    if active_answer == "n":
        active = False