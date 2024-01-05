# 在dell主机上运行，开多线程
import time
import socket
import os
import threading
import secrets
from utils import getconfig, getlog
from .packet import generate_consecutive_packets, detectReplayAttackPacket, customized_packet
from .connection import get_result
# from mysql_handle.mysql import MySQLPusher
import csv
from i2p_rabbitmq.rabbitmq_consumer import RabbitMQConsumer
from i2p_rabbitmq.rabbitmq_producer import RabbitMQProducer


config = getconfig.config
# logger = getlog.setup_logging("i2p")




def start_isi2p(ip_port):
    host = ip_port[0]
    port = ip_port[1]
    
    get_result(host, port)

def action():
    i2p_note = RabbitMQConsumer("without_reg")
    result = RabbitMQProducer("result")
    file_name = os.path.join(*os.path.dirname(os.path.abspath(__file__)).split("/")[:-3])
    file_name = os.path.join("/" + file_name, "data", f"output.csv")

    while(True):
        dic = i2p_note.consuming()





if __name__=='__main__':
    action()