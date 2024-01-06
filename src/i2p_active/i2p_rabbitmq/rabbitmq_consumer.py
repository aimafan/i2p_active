import pika
from utils import getconfig, getlog
import json
import re
import time

config = getconfig.config
logger = getlog.setup_logging("rabbitmq")

host = config['rabbitmq']['host']
port = int(config['rabbitmq']['port'])

class RabbitMQConsumer:
    def __init__(self, queue_name, durable=False, arguments=None, host='localhost', port=5672):
        self.queue_name = queue_name
        self.host = host
        self.port = port
        self.durable = durable
        self.arguments = arguments
        self.connect()

    def connect(self):
        try:
            self.connection = pika.BlockingConnection(pika.ConnectionParameters(self.host, self.port))
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue=self.queue_name, durable=self.durable, arguments=self.arguments)
        except Exception as e:
            logger.error(f"连接RabbitMQ失败: {e}")
            # 这里可以加入重试逻辑或等待

    def reconnect(self):
        # 尝试关闭旧的连接（如果存在）
        try:
            if self.connection.is_open:
                self.connection.close()
        except Exception as e:
            logger.error(f"关闭旧连接时发生错误: {e}")
        
        # 重建连接
        self.connect()

    def consuming_i2pnote(self):
        try:
            method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name, auto_ack=True)
        except Exception as e:
            logger.error(f"消费i2pnote失败: {e}")
            self.reconnect()
            return None

        if body:
            decoded_data = body.decode()
            ip_port_match = re.search(r'IP: (\d+\.\d+\.\d+\.\d+), Port: (\d+)', decoded_data)
            if ip_port_match:
                return {"ip": ip_port_match.group(1), "port": ip_port_match.group(2)}
            else:
                return None
        else:
            return None

    def consuming_result(self):
        try:
            method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name, auto_ack=True)
        except Exception as e:
            logger.error(f"消费result失败: {e}")
            self.reconnect()
            return None

        if body:
            return json.loads(body.decode())
        else:
            return None


if __name__ == "__main__":
    mq = RabbitMQConsumer("result")
    while(True):
        dic = mq.consuming_result()
        print(dic)
        time.sleep(5)

