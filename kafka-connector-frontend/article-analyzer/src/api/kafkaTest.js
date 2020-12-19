const { Kafka } = require('kafkajs')

const kafka = new Kafka({
    clientId: 'article-analyzer',
    ssl: true,
    brokers: ['10.123.252.211:9092', '10.123.252.212:9092', '10.123.252.213:9092']
  })

const AnalyzingTopic = "grammefars_test"
const producer = kafka.producer()

await producer.connect()
    .catch(e => {
        console.log(e)
    })
    await producer.send({
        topic: AnalyzingTopic,
        messages: [
            {value: "Hello world"}
        ],
    })
    .catch(e => { 
        console.log(e)
    })
    