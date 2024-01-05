import json

from utils import getconfig, getlog

import pika
config = getconfig.config
logger = getlog.setup_logging("rabbitmq")

host = config['rabbitmq']['host']
port = int(config['rabbitmq']['port'])

class RabbitMQProducer:
    def __init__(self, queue_name, durable=False, arguments=None, host=host, port=port):
        self.queue_name = queue_name
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host, port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name, durable=durable, arguments=arguments)

    def send_result(self, mydic):
        message = json.dumps(mydic)
        self.channel.basic_publish(exchange='',
                                   routing_key=self.queue_name,
                                   body=message)
        logger.info(f" [x] Sent '{message}' to queue '{self.queue_name}'")

    def close_connection(self):
        self.connection.close()

if __name__ == "__main__":
    mq = RabbitMQProducer("result")
    mydic = {"ip": "12.12.34.64", "port": "7896", "result": "1"}
    mq.send_result(mydic)