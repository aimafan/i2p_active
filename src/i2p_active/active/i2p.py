# 在dell主机上运行，开多线程
import time
import socket
import os
import threading
import secrets
import csv
from utils import getconfig, getlog
from .connection import start_isi2p_1, start_isi2p_2
# from mysql_handle.mysql import MySQLPusher
import csv
from i2p_rabbitmq.rabbitmq_consumer import RabbitMQConsumer
from i2p_rabbitmq.rabbitmq_producer import RabbitMQProducer


config = getconfig.config
# logger = getlog.setup_logging("i2p")


def write_result():
    # 1表示第一个测试通过，2表示第二个测试通过，0表示不通过
    # 只要1或2有任意一个通过，那么即通过
    file_name = os.path.join(*os.path.dirname(os.path.abspath(__file__)).split("/")[:-3])
    file_name = os.path.join("/" + file_name, "data", f"output.csv")
    result_con = RabbitMQConsumer("result")      # 返回一个字典如 {'ip': '12.12.34.64', 'port': '7896', 'result': '1'}
    # 将字典写入CSV文件
    dic = result_con.consuming_result()
    # 检查文件是否存在
    file_exists = os.path.isfile(file_name)

    # 写入CSV文件
    with open(file_name, mode='a', newline='') as file:
        fieldnames = dic.keys()
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # 如果文件不存在，则写入标题行
        if not file_exists:
            writer.writeheader()

        writer.writerow(dic)


# vps1进行第一次测试，也就是java版本测试
# 第一次测试通过，将结果写入result队列，如果第一次测试不通过，将ip和port写入i2p_note_with2队列
def action_1():
    # 写一个线程，不断从result通道中读取数据到output.csv
    address_pool = []
    thread = threading.Thread(target=write_result)
    thread.start()

    # 从vps3中读取ip和port
    i2p_note = RabbitMQConsumer("i2p_note", True, {'x-message-ttl': 60000})
    i2p_note_with2 = RabbitMQProducer("i2p_note_with2", True, {'x-message-ttl': 60000})
    result_pro = RabbitMQProducer("result")

    while(True):
        dic = i2p_note.consuming_i2pnote()
        if(dic == None):
            continue
        if(dic['ip'] in address_pool):
            continue
        else:
            address_pool.append(dic['ip'])
        result1 = start_isi2p_1(dic['ip'], int(dic['port']))
        if(result1):
            result_message = {"ip": dic['ip'], "port": dic['port'], "result": "1"}
            result_pro.send_result(result_message)
        else:
            i2p_note_with2.send_result(dic)


# vps2进行第二次测试，也就是C++版本测试
# 第二次测试通过，将结果写入result队列，测试不通过，同样将结果写入result队列
def action_2():

    # 从vps3中读取ip和port
    i2p_note = RabbitMQConsumer("i2p_note_with2", True, {'x-message-ttl': 300000})
    result_pro = RabbitMQProducer("result")

    while(True):
        dic = i2p_note.consuming_i2pnote()
        result2 = start_isi2p_2(dic['ip'], int(dic['port']))
        if(result2):
            result_message = {"ip": dic['ip'], "port": dic['port'], "result": "2"}
            result_pro.send_result(result_message)
        else:
            result_message = {"ip": dic['ip'], "port": dic['port'], "result": "0"}
            result_pro.send_result(result_message)


if __name__=='__main__':
    action_1()