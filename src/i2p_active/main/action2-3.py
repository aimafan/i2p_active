# 在dell主机上运行，开多线程
import time
import socket
import os
import threading
import secrets
from utils import getconfig, getlog
from active.connection import start_isi2p_1, start_isi2p_2

# from mysql_handle.mysql import MySQLPusher
import csv
from i2p_rabbitmq.rabbitmq_consumer import RabbitMQConsumer
from i2p_rabbitmq.rabbitmq_producer import RabbitMQProducer


config = getconfig.config
# logger = getlog.setup_logging("i2p")


# 第二轮测试
def action_2_3():
    address_pool = []
    i2p_note_with3 = RabbitMQConsumer("i2p_note_with3")
    result_pro = RabbitMQProducer("result")

    while True:
        dic = i2p_note_with3.consuming_result()
        if dic == None:
            time.sleep(5)
            continue
        if dic["ip"] in address_pool:
            continue
        else:
            address_pool.append(dic["ip"])
        result1 = start_isi2p_1(dic["ip"], int(dic["port"]))
        if result1:
            result_message = {"ip": dic["ip"], "port": dic["port"], "result": "3-1"}
            result_pro.send_result(result_message)
        else:
            time.sleep(30)
            result2 = start_isi2p_2(dic["ip"], int(dic["port"]))
            if result2:
                result_message = {"ip": dic["ip"], "port": dic["port"], "result": "3-2"}
                result_pro.send_result(result_message)
            else:
                result_message = {"ip": dic["ip"], "port": dic["port"], "result": "0"}
                result_pro.send_result(result_message)


if __name__ == "__main__":
    action_2_3()
