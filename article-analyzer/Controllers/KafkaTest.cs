using Confluent.Kafka;

namespace article_analyzer.Controllers
{
    public class KafkaTest 
    {
        public KafkaTest() {
            var config = new ProducerConfig { 
                ClientId = "article-analyzer-frontend",
                BootstrapServers = "10.123.252.211:9092, 10.123.252.212:9092, 10.123.252.213:9092",
            };

            using (var producer = new ProducerBuilder<Null, string>(config).Build()) {
                producer.Produce("grammefars_test", new Message<Null, string>{Value ="Hello world from dotnet"});
            }
        }
    }
}
