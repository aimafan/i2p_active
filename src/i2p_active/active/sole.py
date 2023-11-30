import time
from connection import connect
from packet import generate_consecutive_packets
from utils import getlog, getconfig

logger = getlog.setup_logging()
config = getconfig.config

def sole_run():
    timegap = int(config['sole']['timegap'])
    host = config['sole']['host']
    port = int(config['sole']['port'])
    packet_size = int(config['sole']['packet_size'])

    while(True):

        start_time = time.time()
        packet_list = generate_consecutive_packets(packet_size)
        count = connect(host, port, packet_list)
        # 结束计时
        end_time = time.time()

        # 计算并打印运行时间
        elapsed_time = end_time - start_time
        logger.info(f"花费的时间: {elapsed_time}")
        logger.info(f"发送数据包的个数：{count}")
        time.sleep(timegap)

if __name__ == "__main__":
    sole_run()