const { Kafka } = require('kafkajs')

const config = require('./config/kafkaConnection')
const kafka = new Kafka(config)

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
        
        const message = { 
            title: articleData.title,
            subtitle: articleData.subtitle,
            readingTime: articleData.readingTime,
            publication: articleData.publication,
            image: b64
        }

        await producer.connect()
        .catch(e => {
            console.log(e)
        })
        await producer.send({
          topic: AnalyzingTopic,
          messages: [
            {
                value: JSON.stringify(message)
            }
          ],
        })
        .catch(e => { 
            console.log(e)
        })
      }   
}