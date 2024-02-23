import socket
from utils import getconfig, getlog
from .packet import packet_generate, packet2_generate
import time

config = getconfig.config
logger = getlog.setup_logging()

logger_isi2p = getlog.setup_logging("isi2p.log")
logger_isi2p2 = getlog.setup_logging("isi2p2.log")
logger_result = getlog.setup_logging("result.log")
logger_result2 = getlog.setup_logging("result2.log")

timeout_second = int(config["Connection"]["timeout_second"])
socket_second = int(config["Connection"]["socket_second"])
correctCountThreshold = int(config["Connection"]["correctCountThreshold"])


def is_i2p(result):
    host = result[0]
    port = result[1]
    true_count = 0
    for i in range(2, len(result)):
        result[i] = int(result[i])
        if result[i] == -1:
            logger_isi2p.info(f"{host}:{port} 无法连接")
            return True
        elif result[i] == -2:
            logger_isi2p.info(f"{host}:{port} 第一次测试失败")
            return True

    # 连接持续时间测试
    if result[2] >= 5:
        true_count += 1
    elif result[2] > 1 and result[2] < 5:
        logger_isi2p.info(f"{host}:{port} 第一次测试失败，连接持续性测试未通过")
        return

    # 包大小测试
    if result[3] >= 3 and result[3] <= 6:
        true_count += 1
    elif result[3] > 6:
        logger_isi2p.info(f"{host}:{port} 第一次测试失败，数据包大小测试 1 未通过")
        return False

    # 重放中断测试
    if result[4] == 2:
        true_count += 1
    elif result[4] > 2:
        logger_isi2p.info(f"{host}:{port} 第一次测试失败，重放测试未通过")
        return False

    # 数据包大小测试2
    if result[5] == 2:
        true_count += 1
    elif result[5] > 2:
        logger_isi2p.info(f"{host}:{port} 第一次测试失败，数据包测试2未通过")
        return False

    # 黑名单测试
    if result[7] == 1:
        true_count += 1
    else:
        logger_isi2p.info(f"{host}:{port} 第一次测试失败，黑名单测试未通过")
        return False

    # 总结
    if true_count >= correctCountThreshold:
        logger_isi2p.info(f"{host}:{port} 是i2p节点")
        return True
    else:
        logger_isi2p.info(f"{host}:{port} 第一次测试无法确定")
        return False


def is_i2p2(result):
    host = result[0]
    port = result[1]
    true_count = 0
    correctCountThreshold_test2 = int(
        config["Connection"]["correctCountThreshold_test2"]
    )
    for i in range(2, len(result)):
        result[i] = int(result[i])
        if result[i] == -1:
            logger_isi2p2.info(f"{host}:{port} 无法连接")
            return False
        elif result[i] == -2:
            logger_isi2p2.info(f"{host}:{port} 该结点不是i2p结点")
            return False
    # 连接持续时间测试
    if result[2] >= 5:
        true_count += 1
    elif result[2] > 1 and result[2] < 5:
        logger_isi2p2.info(f"{host}:{port} 连接持续性测试未通过")

    if result[3] == 3:
        true_count += 1
    else:
        logger_isi2p2.info(f"{host}:{port} 间断处测试不通过")

    if result[4] == 1:
        true_count += 1
    else:
        logger_isi2p2.info(f"{host}:{port} 间隔时间测试不通过")

    if result[5] == 3:
        true_count += 1
    else:
        logger_isi2p2.info(f"{host}:{port} 间隔时间测试2不通过")

        # 总结
    if true_count >= correctCountThreshold_test2:
        logger_isi2p2.info(f"{host}:{port} 是i2p节点")
        return True
    else:
        logger_isi2p2.info(f"{host}:{port} 该结点不是i2p结点")
        return False


def test(byteNumSinglePacket, host, port):
    count = 0
    result = []
    result.append(host)
    result.append(str(port))
    for num in byteNumSinglePacket:
        packet = byteNumSinglePacket[num]
        if num == 9:
            time.sleep(30)
        count = connect(host, port, packet)

        result.append(str(count))
        if count == -1 or count == -2:
            break
    return result


def start_isi2p_1(host, port):
    logger.info("connect " + host + " " + str(port))

    byteNumSinglePacket = packet_generate()
    # elapsed_time = 0
    result = test(byteNumSinglePacket, host, port)
    logger_result.info(":".join(result))
    return is_i2p(result)


def start_isi2p_2(host, port):
    byteNumSinglePacket = packet2_generate()
    result = test(byteNumSinglePacket, host, port)
    logger_result2.info(":".join(result))
    return is_i2p2(result)


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
        while True:
            try:
                client_socket.settimeout(socket_second)  # 发送数据包之后等的时间
                if len(packetbyte) > count:
                    client_socket.sendall(packetbyte[count])
                else:
                    break

            except Exception as e:
                # 发送错误，对方连接关闭
                logger.warn(f"send出错:{e}")
                break
            count += 1
            try:
                data = client_socket.recv(1024)
                if not data:
                    # 接收连接出错，对方连接关闭
                    logger.warn(
                        host
                        + " "
                        + str(port)
                        + " "
                        + "read接收到not data,可能是对方断开了连接"
                    )
                    break
                else:
                    # 能够接收到数据，不符合obfs4，obfs4应该接收不到数据
                    logger.warn(f"能够接收到返回消息:{data},不符合I2P协议特征")
                    count = -2
                    break
            except socket.timeout:
                # 正常收不到数据，超时2秒
                logger.debug(host + " " + str(port) + " " + "收不到数据")
                pass
            except Exception as e:
                # 接收连接出错，对方连接关闭？
                logger.info(host + " " + str(port) + " " + f"read出错:{e}")
                break

        return count
