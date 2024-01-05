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
    def __init__(self, queue_name, durable=False, arguments=None, host=host, port=port):
        self.queue_name = queue_name
        self.received_message = None
        self.connection = pika.BlockingConnection(pika.ConnectionParameters(host, port))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue=queue_name, durable=durable, arguments=arguments)

    def consuming_i2pnote(self):
        try:
            method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name, auto_ack=True)
        except:
            logger.error("消费i2pnote失败")
            return
        # 将字节字符串解码为普通字符串
        if(body):
            decoded_data = body.decode()

            # 使用正则表达式提取IP和端口
            ip_port_match = re.search(r'IP: (\d+\.\d+\.\d+\.\d+), Port: (\d+)', decoded_data)
            if ip_port_match:
                ip = ip_port_match.group(1)
                port = ip_port_match.group(2)
            else:
                ip = None
                port = None
            
            return {"ip": ip, "port": port}
        else:
            return None
        
    def consuming_result(self):
        method_frame, header_frame, body = self.channel.basic_get(queue=self.queue_name, auto_ack=True)
        # 将字节字符串解码为普通字符串
        if(body):
            message = json.loads(body)
            return message
        else:
            return None


    def close_connection(self):
        self.connection.close()


if __name__ == "__main__":
    mq = RabbitMQConsumer("result")
    while(True):
        dic = mq.consuming_result()
        print(dic)
        time.sleep(5)

