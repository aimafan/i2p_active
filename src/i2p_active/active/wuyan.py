# 在dell主机上运行，开多线程
import time
import socket
import os
import threading
import secrets
from utils import getconfig, getlog
from .packet import generate_consecutive_packets, detectReplayAttackPacket, customized_packet
from .connection import get_result

config = getconfig.config
logger = getlog.setup_logging("wuyan")
max_threads = int(config['wuyan']['threads_num'])  # 最多开70个线程
semaphore = threading.Semaphore(max_threads)


def start_isi2p(ip_port):
    host = ip_port[0]
    port = ip_port[1]
    
    # 使用 acquire() 获取信号量，控制并发数量
    # with semaphore:
    get_result(host, port)

def action():
    file_name = os.path.join(*os.path.dirname(os.path.abspath(__file__)).split("/")[:-3])
    file_name = os.path.join("/" + file_name, "data", "wuyan.txt")

    # 创建一个空列表，用于存储从文件中读取的数据
    my_list = []

    # 打开文件以读取模式
    with open(file_name, "r") as file:
        # 逐行读取文件
        for line in file:
            # 去除行尾的换行符并将其分割成元素
            elements = line.split(":")
            # 将元素转换为适当的数据类型，这里假设元素是整数
            # elements.pop()
            
            elements[1] = int(elements[1])

            # 将元素添加到列表
            my_list.append(elements)

    threads = []
    
    for ip_port in my_list:
        thread = threading.Thread(target=start_isi2p, args=(ip_port,))
        # start_isi2p(ip_port)
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


if __name__=='__main__':
    action()