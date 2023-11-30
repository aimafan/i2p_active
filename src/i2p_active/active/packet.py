import secrets


def random_create(length: int):
    """
    生成一个指定长度的随机字节序列
    """
    random_bytes = secrets.token_bytes(length)
    return random_bytes


def generate_consecutive_packets(packet_size: int, packet_count=10):
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
    for i in range(1, packet_count):
        data = random_create(packet_size)
        a.append(data)
    return a