# Simple experiment

import sys
from pyspark import SparkContext
from pyspark.streaming import StreamingContext
from pyspark.streaming.kafka import KafkaUtils

if __name__ == "__main__":
  sc = SparkContext(appName="PythonStreamingDirectKafkaWordCount")
  ssc = StreamingContext(sc, 2)
  brokers = sys.argv[1:-1]
  topic = sys.argv[-1]

  stream = KafkaUtils.createDirectStream(ssc, [topic],{"metadata.broker.list": brokers})

  lines = stream.map(lambda x: x[1])
  counts = lines.flatMap(lambda line: line.split(" ")) \
                .map(lambda word: (word, 1)) \
                .reduceByKey(lambda a, b: a+b)
  counts.pprint()

  ssc.start()
  ssc.awaitTermination()

# /home/hadoop/spark/bin/spark-submit sparkStream.py 0.0.0.0:9092 node1:9092 node2:9092 test