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
        self.connect(self, durable, arguments, host, port)
        

    def connect(self, durable, arguments, host, port):
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host, port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=self.queue_name, durable=durable, arguments=arguments)

    def send_result(self, mydic):
        message = json.dumps(mydic)
        try:
            self.channel.basic_publish(exchange='',
                                       routing_key=self.queue_name,
                                       body=message)
        except (pika.exceptions.ConnectionClosedByBroker, 
                pika.exceptions.AMQPChannelError, 
                pika.exceptions.AMQPConnectionError) as e:
            logger.error(f"生产result失败，尝试重连。错误详情: {e}")
            self.reconnect()
            return
        except Exception as e:
            logger.error(f"生产result失败，错误详情: {e}")
            return
        logger.info(f" [x] Sent '{message}' to queue '{self.queue_name}'")

    def reconnect(self):
        self.connection.close()
        self.connect()

if __name__ == "__main__":
    i2p_note_with2 = RabbitMQProducer("i2p_note_with2", True, {'x-message-ttl': 60000})
    mydic = {"ip": "12.12.34.64", "port": "7896", "result": "1"}
    i2p_note_with2.send_result(mydic)