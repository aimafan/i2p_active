from scapy.all import IP, TCP, send, sr1
from active.connection import connect, start_isi2p_1, logger

def establish_tcp_connection(src_ip, dst_ip, src_port, dst_port):
    # 构造SYN数据包，发起TCP连接
    syn_packet = IP(src=src_ip, dst=dst_ip) / TCP(sport=src_port, dport=dst_port, flags='S')
    syn_ack = sr1(syn_packet, verbose=False)
    logger.info(syn_ack)

    # 提取确认号
    ack_num = syn_ack.seq + 1

    # 构造ACK数据包，确认连接
    ack_packet = IP(src=src_ip, dst=dst_ip) / TCP(sport=src_port, dport=dst_port, flags='A', seq=1, ack=1)
    logger.info(ack_packet)
    # aaa = sr1(ack_packet, verbose=False)
    logger.info(aaa)

    return ack_num

def send_empty_packets(src_ip, dst_ip, src_port, dst_port, num_packets):
    # 建立TCP连接并获取确认号
    ack_num = establish_tcp_connection(src_ip, dst_ip, src_port, dst_port)

    # # 发送5个空白数据包
    # for i in range(num_packets):
    #     ip = IP(src=src_ip, dst=dst_ip)
    #     tcp = TCP(sport=src_port, dport=dst_port, seq=ack_num, ack=0, flags='A')
    #     packet = ip / tcp
    #     send(packet, verbose=False)
    #     logger.info(f"发送空白数据包 {i+1}")

if __name__ == '__main__':
    src_ip = "142.171.227.116"
    dst_ip = "74.48.140.28"
    src_port = 12345
    dst_port = 13758
    num_packets = 5

    send_empty_packets(src_ip, dst_ip, src_port, dst_port, num_packets)