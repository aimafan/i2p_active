import pika
from utils import getconfig, getlog
import json

config = getconfig.config
logger = getlog.setup_logging("rabbitmq")

host = config['rabbitmq']['host']
port = int(config['rabbitmq']['port'])

class RabbitMQConsumer:
    def __init__(self, queue_name, host=host, port=port):
        self.queue_name = queue_name
        self.received_message = None
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host, port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name)

    def consuming(self):
        method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name, auto_ack=True)
        if method_frame:
            return json.loads(body)  
        else:
            return None


    def close_connection(self):
        self.connection.close()


if __name__ == "__main__":
    mq = RabbitMQConsumer("i2p_note")
    while(True):
        dic = mq.consuming()
        print(dic)

