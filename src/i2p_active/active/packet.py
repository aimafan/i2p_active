import secrets


def random_create(length: int):
    """
    生成一个指定长度的随机字节序列
    """
    random_bytes = secrets.token_bytes(length)
    return random_bytes


def generate_consecutive_packets(packet_size: int, pre_packet=b'0', packet_count=10):
    """
    生成一系列大小相同的随机数据包。

    每个数据包由随机字节组成，并且所有数据包的大小相同。

    Args:
        packet_size (int): 每个数据包的大小（以字节为单位）。
        packet_count (int): 要生成的数据包数量。

    Returns:
        list of bytes: 包含随机数据包的列表，每个数据包都是一个字节序列。

    """
    a = []
    if pre_packet != b'0':
        a.append(pre_packet + random_create(packet_size - 8))
    for i in range(1, packet_count):
        data = random_create(packet_size)
        a.append(data)
    return a

def detectReplayAttackPacket(packet_size: int, packet_count=10):
    """
    数据包大小测试和重放中断测试
    """
    a = []
    prebyte = random_create(8)
    a.append(prebyte + random_create(packet_size - 8))
    for i in range(1, packet_count - 1):
        data = random_create(packet_size)
        a.append(data)
    return a, prebyte

def customized_packet(packet_size: int, pre_size: int, packet_count=10):
    a = []
    a.append(random_create(pre_size))
    for i in range(1, packet_count - 1):
        data = random_create(packet_size)
        a.append(data)
    return a

# 进行多次连接中包的生成
def packet_generate():
    packet_dic = {0: [], 1: [], 2: [], 3: [], 4: [], 5: []}
    packet_dic[0] = generate_consecutive_packets(1)
    packet_dic[1], pre = detectReplayAttackPacket(32)
    packet_dic[2] = generate_consecutive_packets(32, pre)
    packet_dic[3] = customized_packet(129, 63)
    packet_dic[4] = generate_consecutive_packets(1, 1)
    packet_dic[5] = generate_consecutive_packets(1)

    return packet_dic