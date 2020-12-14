# Multi node kafka and multi node zookeeper
Create a kafka user
```bash
$ sudo useradd kafka
$ sudo passwd kafka
```

Install kafka
```bash
$ wget https://mirrors.dotsrc.org/apache/kafka/2.6.0/kafka_2.13-2.6.0.tgz
$ sudo tar -zxvof kafka_2.13-2.6.0.tgz
$ rm kafka_2.13-2.6.0.tgz
$ sudo mv kafka_2.13-2.6.0 /opt
$ sudo chown -R kafka:kafka kafka_2.13-2.6.0
$ sudo ln -s /opt/kafka_2.13-2.6.0 /opt/kafka
```

To manage the ip's add the following to `/etc/hosts` 
```bash
10.123.252.213  node-master
10.123.252.211  node1
10.123.252.212  node2
```

Create a data folder
```bash
$ sudo mkdir -p /data1/zookeeper
$ sudo chown -R kafka:kafka /data1/
```

The following id has to be unique, e.g on machine 1 myid contains 1, on machine 2 myid contains 2... 
```bash
$ echo 1 > /data1/zookeeper/myid
```

`/opt/kafka/config/zookeeper.properties` has to contain the following
```bash
dataDir=/data1/zookeeper
clientPort=2181
maxClientCnxns=0
admin.enableServer=false
tickTime=2000
initLimit=5
syncLimit=2

server.1=node-master:2888:3888
server.2=node1:2888:3888
server.3=node2:2888:3888
```

`/opt/kafka/config/server.properties` has to contain the following. The broker.id has to be unique, e.g on machine 1 myid contains 1, on machine 2 myid contains 2... 
```bash
broker.id=1
listeners=PLAINTEXT://:9092
num.network.threads=3
num.io.threads=8
socket.send.buffer.bytes=102400
socket.receive.buffer.bytes=102400
socket.request.max.bytes=104857600

############################# Log Basics #############################
log.dirs=/data1/kafka-logs
num.partitions=1
num.recovery.threads.per.data.dir=1

############################# Internal Topic Settings  #############################
offsets.topic.replication.factor=1
transaction.state.log.replication.factor=1
transaction.state.log.min.isr=1

############################# Log Retention Policy #############################
log.retention.hours=168
log.segment.bytes=1073741824
log.retention.check.interval.ms=300000

############################# Zookeeper #############################
zookeeper.connect=master-node:2181,node1:2181,node2:2181
zookeeper.connection.timeout.ms=18000

############################# Group Coordinator Settings #############################
group.initial.rebalance.delay.ms=0
```

Increase message size:
In `kafka/config/server.properties` add/change:
```
message.max.bytes=15728640
replica.fetch.max.bytes=15728640
```
In `kafka/config/producer.properties` add/change:
```
max.request.size=15728640
```
In `kafka/config/consumer.properties` add/change:
```
fetch.message.max.bytes=15728640
```

Start zookeeper, on all machines
```bash
$ su kafka
$ /opt/kafka/bin/zookeeper-server-start.sh /opt/kafka/config/zookeeper.properties
% or
$ /opt/kafka/bin/zookeeper-server-start.sh -daemon /opt/kafka/config/zookeeper.properties
```

And start the kafka brokers
```bash
$ su kafka
$ /opt/kafka/bin/kafka-server-start.sh /opt/kafka/config/server.properties
% or
$ /opt/kafka/bin/kafka-server-start.sh -daemon /opt/kafka/config/server.properties
```

## Test the setup
Create a topic
```bash
$ /opt/kafka/bin/kafka-topics.sh \
  --create \
  --zookeeper master-node:2181,node1:2181,node2:2181 \
  --replication-factor 1 \
  --partitions 1 \
  --topic test
```

Assuming the command is run from master-node
```bash
$ /opt/kafka/bin/kafka-console-producer.sh \
  --broker-list 0.0.0.0:9092,node1:9092,node2:9092 \
  --topic test
```

Assuming the command is run from master-node
```bash
/opt/kafka/bin/kafka-console-consumer.sh \
  --bootstrap-server 0.0.0.0:9092,node1:9092,node2:9092 \
  --topic test \
  --from-beginning
```

# Commands to remember
List topics
```bash
$ /opt/kafka/bin/kafka-topics.sh --list --zookeeper 0.0.0.0:2181
```

# stop servers
```bash
$ sudo /opt/kafka/bin/kafka-server-stop.sh
$ sudo /opt/kafka/bin/zookeeper-server-stop.sh
```