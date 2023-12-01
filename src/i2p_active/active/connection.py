import socket
from utils import getconfig, getlog
from packet import packet_generate
import time

config = getconfig.config
logger = getlog.setup_logging()
logger_result = getlog.setup_logging("result")
logger_isi2p = getlog.setup_logging("isi2p")

timeout_second = int(config['Connection']['timeout_second'])
socket_second = int(config['Connection']['socket_second'])
correctCountThreshold = int(config['Connection']['correctCountThreshold'])

def is_i2p(result, elapsed_time):
    host = result[0]
    port = result[1]
    true_count = 0
    for i in range(2, len(result)):
        result[i] = int(result[i])
        if result[i] == -1:
            logger_isi2p.info(f'{host}:{port} 无法连接')
            return
    ## 连接持续时间测试
    if elapsed_time > 9.5 and elapsed_time < 12.5:
        true_count += 1
    elif elapsed_time < 1:
        pass
    else:
        logger_isi2p.info(f'{host}:{port} 不是i2p节点，连接持续时间测试未通过')
        return
    
    # 包大小测试
    if result[3] >= 3 and result[3] <= 6:
        true_count += 1
    elif result[3] > 6:
        logger_isi2p.info(f'{host}:{port} 不是i2p节点，数据包大小测试 1 未通过')
        return
    
    # 重放中断测试
    if result[4] == 2:
        true_count += 1
    elif result[4] > 2:
        logger_isi2p.info(f'{host}:{port} 不是i2p节点，重放测试未通过')
        return
    
    # 数据包大小测试2
    if result[5] == 2:
        true_count += 1
    elif result[5] > 2:
        logger_isi2p.info(f'{host}:{port} 不是i2p节点，数据包测试2未通过')
        return

    # 黑名单测试
    if result[7] == 1:
        true_count += 1
    else:
        logger_isi2p.info(f'{host}:{port} 不是i2p节点，黑名单测试未通过')
        return
    
    # 总结
    if true_count >= correctCountThreshold:
        logger_isi2p.info(f'{host}:{port} 是i2p节点')
    else:
        logger_isi2p.info(f'{host}:{port} 无法确定')
    return



def get_result(host, port):
    logger.info("connect " + host + " " + str(port))
    result = []
    result.append(host)
    result.append(str(port))
    
    byteNumSinglePacket = packet_generate()
    elapsed_time = 0
    for num in byteNumSinglePacket:
        packet = byteNumSinglePacket[num]
        for i in range(1, 4):       # 测试3次，防止因网络问题中断，只要有一次没中断就按照没中断的这次来
            if num == 0:
                start_time = time.time()
            count = connect(host, port, packet)
            if count == 1:
                continue
            elif count == -1:
                result.append(str(count))
                break
            else:
                if num == 0:
                    end_time = time.time()
                    elapsed_time = end_time - start_time
                break
            

        result.append(str(count))
    logger_result.info(":".join(result))
    is_i2p(result, elapsed_time)


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