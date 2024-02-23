import pymysql
from datetime import datetime, timedelta
import re
from utils.getconfig import config
from utils.getlog import setup_logging
import os
import csv
from i2p_rabbitmq.rabbitmq_producer import RabbitMQProducer
import time

logger = setup_logging("mysql.log")


class MySQLPusher:
    def __init__(
        self,
        host=config["mysql"]["host"],
        port=int(config["mysql"]["port"]),
        user=config["mysql"]["user"],
        password=config["mysql"]["password"],
        database=config["mysql"]["database"],
    ):
        self.mysql_config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database,
        }

    def handle_public_time(self, delta_time):
        now = datetime.now()
        delta_time = re.sub(r"\s+", "", delta_time, flags=re.UNICODE)
        if "分" in delta_time:
            num = int(delta_time.split("分")[0])
        else:
            num = 1
        return (now - timedelta(minutes=num)).strftime("%Y-%m-%d %H:%M:%S")

    def push_mysql(self, netdb):
        """
        将爬虫的结果push到mysql中
        """
        connection = pymysql.connect(**self.mysql_config)
        cursor = connection.cursor()

        # 检查表是否存在，如果不存在则创建
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS i2p (
                id VARCHAR(255) PRIMARY KEY,
                hash VARCHAR(255),
                appear_time DATETIME,
                public_time VARCHAR(255),
                version VARCHAR(255),
                isfloodfill TINYINT(1),
                ntcp2_ipv4 VARCHAR(255),
                ntcp2_ipv4_port INT,
                ntcp2_ipv6 VARCHAR(255),
                ntcp2_ipv6_port INT,
                ntcp2_identity VARCHAR(255),
                ntcp2_static VARCHAR(255),
                ssu_port4 INT,
                ssu_port6 INT,
                country VARCHAR(255)
            )
        """
        )

        # 插入数据的SQL语句
        sql = """
        INSERT INTO i2p (id, hash, appear_time, public_time, version, isfloodfill, ntcp2_ipv4, ntcp2_ipv4_port, 
        ntcp2_ipv6, ntcp2_ipv6_port, ntcp2_identity, ntcp2_static, ssu_port4, ssu_port6, country)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE appear_time = VALUES(appear_time), public_time = VALUES(public_time)
        """

        for item in netdb:
            public_time = self.handle_public_time(item["public_time"])

            data = (
                item["id"],
                item["hash"],
                datetime.now(),
                public_time,
                item["version"],
                item["isfloodfill"],
                item["ntcp2_ipv4"],
                item["ntcp2_ipv4_port"],
                item["ntcp2_ipv6"],
                item["ntcp2_ipv6_port"],
                item["ntcp2_identity"],
                item["ntcp2_static"],
                item["ssu_port4"],
                0,
                item["country"],
            )

            cursor.execute(sql, data)

        connection.commit()
        cursor.close()
        connection.close()

    def get_i2pnote(self):
        ipv4_file_name = os.path.join(
            *os.path.dirname(os.path.abspath(__file__)).split("/")[:-3]
        )
        ipv4_file_name = os.path.join("/" + ipv4_file_name, "data", "ipv4.txt")

        # 将ntcp2_ipv4地址写入文件
        def write_ipv4_to_file(file_path, ipv4):
            with open(file_path, "a") as file:
                file.write(ipv4 + "\n")

        # 从文件中读取已有的ntcp2_ipv4地址
        def read_ipv4_list(file_path):
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    return [line.split()[0] for line in file if line.strip()]
            return []

        existing_ipv4s = read_ipv4_list(ipv4_file_name)
        while True:
            connection = pymysql.connect(**self.mysql_config)
            with connection.cursor() as cursor:
                flag = 0
                # SQL查询语句
                sql = """
                SELECT hash, ntcp2_ipv4, ntcp2_ipv4_port, ntcp2_identity, ntcp2_static, appear_time
                FROM i2p 
                WHERE hash IS NOT NULL AND 
                    ntcp2_ipv4 IS NOT NULL AND 
                    ntcp2_ipv4_port IS NOT NULL AND 
                    ntcp2_identity IS NOT NULL AND 
                    ntcp2_static IS NOT NULL AND 
                    ntcp2_ipv4 != "" 
                ORDER BY appear_time DESC 
                LIMIT 500
                """

                cursor.execute(sql)
                result_list = cursor.fetchall()

            # 检查是否所有需要的字段都存在
            for result in result_list:
                if not result:
                    logger.warn(f"没有获得查询结果")
                    continue
                if result[1] not in existing_ipv4s:
                    write_ipv4_to_file(
                        ipv4_file_name, result[1] + " " + str(result[-1])
                    )
                    flag = 1
                    break
                else:
                    continue

            if flag == 1:
                break
            else:
                connection.close()
                logger.warn(f"等待数据库更新......")
                time.sleep(10)
        return result


if __name__ == "__main__":
    pusher = MySQLPusher("10.112.58.202", 7658, "root", "darknet@iie", "darknet")
    # pusher.push_mysql(data_list)  # netdb 是要插入的数据列表
    pusher.get_i2pnote()
