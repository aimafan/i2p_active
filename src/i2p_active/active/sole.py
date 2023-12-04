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
# logger = getlog.setup_logging("i2p")


def start_isi2p(ip_port):
    host = ip_port[0]
    port = ip_port[1]
    
    # 使用 acquire() 获取信号量，控制并发数量
    # with semaphore:
    get_result(host, port)

def action():

    my_list = ["142.171.48.35", 27759]
    start_isi2p(my_list)



if __name__=='__main__':
    action()