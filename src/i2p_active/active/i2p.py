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

config = getconfig.config
# logger = getlog.setup_logging("i2p")


def start_isi2p(ip_port):
    host = ip_port[0]
    port = ip_port[1]
    
    get_result(host, port)

def action():
    # i2p_note = MySQLPusher()
    file_name = os.path.join(*os.path.dirname(os.path.abspath(__file__)).split("/")[:-3])
    file_name = os.path.join("/" + file_name, "data", f"output.csv")

    # 创建一个空列表，用于存储从文件中读取的数据
    my_list = []

    with open(file_name, newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            my_list.append((row['ntcp2_ipv4'], int(row['ntcp2_ipv4_port'])))
    
    max_threads = int(config['i2p']['threads_num'])  # 最多开70个线程
    semaphore = threading.Semaphore(max_threads)
    threads = []
    
    def thread_task(ip_port):
        with semaphore:
            start_isi2p(ip_port)
    
    for ip_port in my_list:
        thread = threading.Thread(target=thread_task, args=(ip_port,))
        # start_isi2p(ip_port)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


if __name__=='__main__':
    action()