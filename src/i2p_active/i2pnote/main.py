from .crawl_netdb import run_crawl
from .crawl_version import get_versions
from .mysql import MySQLPusher
from concurrent.futures import ThreadPoolExecutor
import threading
import time
from utils import getconfig, getlog

config = getconfig.config
logger = getlog.setup_logging("i2pnote")

def get_url():
    base_url = config["crawl"]["base_url"]
    urls = []
    version_url = config["crawl"]["version_url"]
    versions = get_versions(version_url)

    for version in versions.keys():
        url = f"{base_url}?pg=1&ps={versions[version] + 50}&v={version}"
        urls.append(url)
    return urls



def run():
    pusher = MySQLPusher(
        config['mysql']['host'],
        int(config['mysql']['port']),
        config['mysql']['user'],
        config['mysql']['password'],
        config['mysql']['database']
    )
    logger.info(f"{config['mysql']['host']}:{config['mysql']['port']} 数据库连接成功")

    urls = get_url()
    # TODO：加多线程爬虫
    max_threads = int(config['crawl']['threads_num'])  # 最多开7个线程
    semaphore = threading.Semaphore(max_threads)
    threads = []

    def process_url(url, pusher):
        with semaphore:
            netdb = run_crawl(url)
            pusher.push_mysql(netdb)
            logger.info(f"成功将数据插入数据库中，此次共插入数据{str(len(netdb))}条")

    for url in urls:
        thread = threading.Thread(target=process_url, args=(url, pusher))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()


if __name__ == "__main__":
    i = 0
    while(True):
        i += 1
        logger.info(f"开始第 {i} 次爬虫")
        start_time = time.time()
        run()
        end_time = time.time()
        logger.info(f"爬虫结束，本次爬虫用时 {int(end_time - start_time)} 秒，{config['crawl']['sleep_time']} 秒后开启下一次爬虫")
        time.sleep(int(config["crawl"]["sleep_time"]))