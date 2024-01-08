# 在dell主机上运行，开多线程
import time
import socket
import os
import threading
import secrets
import csv
from utils import getconfig, getlog
from active.connection import start_isi2p_1, start_isi2p_2
# from mysql_handle.mysql import MySQLPusher
import csv
from i2p_rabbitmq.rabbitmq_consumer import RabbitMQConsumer
from i2p_rabbitmq.rabbitmq_producer import RabbitMQProducer

# vps2进行第二次测试，也就是C++版本测试
# 第二次测试通过，将结果写入result队列，测试不通过，同样将结果写入result队列
def action_2(): 
    address_pool = []
    # 从vps3中读取ip和port
    i2p_note = RabbitMQConsumer("i2p_note_with2", True, {'x-message-ttl': 60000})
    result_pro = RabbitMQProducer("result")

    while(True):
        dic = i2p_note.consuming_result()
        if(dic == None):
            continue
        if(dic['ip'] in address_pool):
            continue
        else:
            address_pool.append(dic['ip'])
        result2 = start_isi2p_2(dic['ip'], int(dic['port']))
        if(result2):
            result_message = {"ip": dic['ip'], "port": dic['port'], "result": "2"}
            result_pro.send_result(result_message)
        else:
            result_message = {"ip": dic['ip'], "port": dic['port'], "result": "0"}
            result_pro.send_result(result_message)


if __name__=='__main__':
    action_2()