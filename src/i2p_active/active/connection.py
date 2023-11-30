import socket
from utils import getconfig, getlog

config = getconfig.config
logger = getlog.setup_logging()

timeout_second = int(config['Connection']['timeout_second'])
socket_second = int(config['Connection']['socket_second'])

def connect(host, port, packetbyte):
    """
    与I2P结点建立连接，并发送数据，列表中数据发送结束，断开连接
    参数：
        host(string): 连接的主机ip
        port(int): 连接的主机port
        packetbyte(list of byte): 要发送的数据列表

    Returns:
        int: 成功发送的数据包数量。如果连接失败，则返回-1。
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        # 尝试连接到目标主机和端口
        client_socket.settimeout(timeout_second)
        try:
            client_socket.connect((host, port))
            logger.info(host + " " + str(port) + " " + "connect success!")
        except Exception as e:
            logger.warn(host + " " + str(port) + " " + f"connect error! {e}")
            return -1
        # 构造要发送的数据包
        count = 0
        while(True):
            try:
                client_socket.settimeout(socket_second) # 发送数据包之后等的时间
                if(len(packetbyte) > count):
                    client_socket.sendall(packetbyte[count])
                else:
                    break

            except Exception as e:
                #发送错误，对方连接关闭
                logger.warn(f'send出错:{e}')
                break
            count += 1
            try:
                data = client_socket.recv(1024)
                if not data:
                    #接收连接出错，对方连接关闭
                    logger.warn(host + " " + str(port) + " " + 'read接收到not data,可能是对方断开了连接')
                    break
                else:
                    #能够接收到数据，不符合obfs4，obfs4应该接收不到数据
                    logger.warn(f'能够接收到返回消息:{data},不符合I2P协议特征')
                    hasReturnByte=True
                    break 
            except socket.timeout:
            #正常收不到数据，超时2秒
                logger.debug(host + " " + str(port) + " " + "收不到数据")
                pass
            except Exception as e:
            #接收连接出错，对方连接关闭？
                logger.info(host + " " + str(port) + " " + f'read出错:{e}')
                break
            
        return count