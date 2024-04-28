from active.packet import *
from active.connection import connect, start_isi2p_1, logger
import time
import socket
from scapy.all import IP, TCP, send, sr1



def solo(host, port):
    dic = {"ip" : host, "port": port}
    result1 = start_isi2p_1(dic['ip'], int(dic['port']))
    if result1:
        print(result1)



def client(host, port):
    while True:
        
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
    # 尝试连接到目标主机和端口
            client_socket.settimeout(5)
            client_socket.connect((host, port))
            logger.info("连接成功")
            
            time.sleep(15)



if __name__ == "__main__":
    host = "74.48.140.28"
    port = 13758
    client(host, port)