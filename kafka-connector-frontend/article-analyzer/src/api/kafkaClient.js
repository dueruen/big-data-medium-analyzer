const { Kafka } = require('kafkajs')

const kafka = new Kafka({
    clientId: 'article-analyzer',
    ssl: true,
    brokers: ['10.123.252.211:9092', '10.123.252.212:9092', '10.123.252.213:9092']
  })

const AnalyzingTopic = "grammefars_test"
const producer = kafka.producer()

export const publishNewArticle = async(articleData) => {
    console.log(articleData)

    const reader = new FileReader();
    reader.readAsDataURL(articleData.articlePicture)
    reader.onload = async function () {
        // convert image file to base64 string
        const b64WithMeta = reader.result;
        //Cuts of metadata about file, leaving only the b64 string
        const stringSplit = b64WithMeta.split(",")
        const b64 = stringSplit[1]
        
        await producer.connect()
        .catch(e => {
            console.log(e)
        })
        await producer.send({
          topic: AnalyzingTopic,
          messages: [
            {
                value: { 
                title: articleData.title,
                subtitle: articleData.subtitle,
                readingTime: articleData.readingTime,
                publication: articleData.publication,
                image: b64
            },
        },
          ],
        })
        .catch(e => { 
            console.log(e)
        })
      }   
}