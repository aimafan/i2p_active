from time import sleep
from mysql_handle.mysql import MySQLPusher
from utils import getconfig, getlog
from .connection import connect, logger
from .NTCP2 import NTCP2Establisher
import base64
import os



config = getconfig.config


sole_host = config['solo']['host']
sole_port = int(config['solo']['port'])

with_active_times = int(config['with_active']['times'])

def start_isi2p(ip_port, m_RemoteIdentHash, m_IV, m_remoteStaticKey):
    host = ip_port[0]
    port = ip_port[1]
    
    ntcp2 = NTCP2Establisher(m_RemoteIdentHash, m_IV, m_remoteStaticKey)
    ntcp2.CreateSessionRequestMessage()
    # logger.info(f"Router Hash: {m_RemoteIdentHash}, IV: {m_IV}, remote static key: {m_remoteStaticKey}")
    data = connect(host, port, ntcp2.m_SessionRequestBuffer)
    if data == 201 or data == 200:
        return data
    else:
        return ntcp2.SessionConfirmed_key(data)

def base64replace(m_RemoteIdentHash, m_IV, m_remoteStaticKey):
    return base64.urlsafe_b64decode(m_RemoteIdentHash.replace('-', '+').replace('~', '/')), base64.urlsafe_b64decode(m_IV.replace('-', '+').replace('~', '/')), base64.urlsafe_b64decode(m_remoteStaticKey.replace('-', '+').replace('~', '/'))

def write_result(host, port, result, times):
    result_file_path = os.path.join(*os.path.dirname(os.path.abspath(__file__)).split("/")[:-3])
    result_file_path = os.path.join("/" + result_file_path, "data", "with_active_result.txt")
    
    # 将结果以 "host:port result" 的形式写入文件
    with open(result_file_path, 'a') as file:  # 使用 'a' 模式以追加数据到文件
        file.write(f"{host}:{port}  {result}, 第{times}次\n")


def run():
    mysql_i2p_node = MySQLPusher()
    while(True):
        i2p_node = mysql_i2p_node.get_i2pnote()
        host = i2p_node[1]
        port = i2p_node[2]

        # [ip, port], m_RemoteIdentHash, m_IV, m_remoteStaticKey
        # 32byte, 16byte, 32byte
        m_RemoteIdentHash = i2p_node[0]
        m_IV = i2p_node[3]
        m_remoteStaticKey = i2p_node[4]
        m_RemoteIdentHash, m_IV, m_remoteStaticKey = base64replace(m_RemoteIdentHash, m_IV, m_remoteStaticKey)

        # 检测10次
        for i in range(1, with_active_times + 1):
            logger.info(f"开始识别{host}:{port}，第{i}次识别")
            count = i
            isi2p = start_isi2p([host, port], m_RemoteIdentHash, m_IV, m_remoteStaticKey)
            if isi2p == 100:
                break

        write_result(host, port, isi2p, count)
        sleep(0.5)

if __name__ == "__main__":
    run()
    # ('5NW-Aq~v29-pcU3pQPWqDABug2y~MB09bSR9DnKlpCE=', '173.175.15.19', 16788, 'M5Tq~1jvbXJtn1dhG~ZRDHNyY7Ttl-oKRfDe4vlm978=', 'exeXb27Btn6wkjisC8INBJJ3w-1RJxWZQb0MClHeNhU=')