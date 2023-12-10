import pymysql
from datetime import datetime, timedelta
import re

class MySQLPusher:
    def __init__(self, host, port, user, password, database):
        self.mysql_config = {
            "host": host,
            "port": port,
            "user": user,
            "password": password,
            "database": database
        }

    def handle_public_time(self, delta_time):
        now = datetime.now()
        delta_time = re.sub(r'\s+', '', delta_time, flags=re.UNICODE)
        if "分" in delta_time:
            num = int(delta_time.split("分")[0])
        else:
            num = 1
        return (now - timedelta(minutes=num)).strftime("%Y-%m-%d %H:%M:%S")

    def push_mysql(self, netdb):
        connection = pymysql.connect(**self.mysql_config)
        cursor = connection.cursor()

        # 检查表是否存在，如果不存在则创建
        cursor.execute("""
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
        """)

        # 插入数据的SQL语句
        sql = """
        INSERT INTO i2p (id, hash, appear_time, public_time, version, isfloodfill, ntcp2_ipv4, ntcp2_ipv4_port, 
        ntcp2_ipv6, ntcp2_ipv6_port, ntcp2_identity, ntcp2_static, ssu_port4, ssu_port6, country)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE appear_time = VALUES(appear_time), public_time = VALUES(public_time)
        """

        for item in netdb:
            public_time = self.handle_public_time(item['public_time'])

            data = (
                item['id'], item['hash'], datetime.now(), public_time, item['version'], item['isfloodfill'],
                item['ntcp2_ipv4'], item['ntcp2_ipv4_port'], item['ntcp2_ipv6'], item['ntcp2_ipv6_port'],
                item['ntcp2_identity'], item['ntcp2_static'], item['ssu_port4'], 0, item['country']
            )

            cursor.execute(sql, data)

        connection.commit()
        cursor.close()
        connection.close()


if __name__ == "__main__":
    pusher = MySQLPusher("10.112.58.202", 7658, "root", "darknet@iie", "darknet")
    data_list = [{'hash': 'ayMA0SJ-NJ1Im2ASOWf22~Ky64uePdulK010-gWyY8Y=', 'id': 'ayMA0S', 'country': '德国', 'public_time': '33\xa0分 前', 'ntcp2_ipv4': '89.116.243.65', 'ntcp2_ipv4_port': 23692, 'ntcp2_ipv6': '', 'ntcp2_ipv6_port': 0, 'ssu_port4': 23692, 'ntcp2_identity': '8Me7hx9QCTrFc7a~Nllw0vMB2E2yQW-pPoiuUTBdDzg=', 'ntcp2_static': 'ZuracKT-LUdeI-~51iVwrjR6BgtuioNUTCvuHY3okSc=', 'version': '0.9.60', 'isfloodfill': 0}, {'hash': 'V~74McJM-dImhmwkvsQxXSjuIrmje7HEpKwnulL4t0Q=', 'id': 'V~74Mc', 'country': '中国', 'public_time': '2\xa0分 前', 'ntcp2_ipv4': '', 'ntcp2_ipv4_port': 0, 'ntcp2_ipv6': '', 'ntcp2_ipv6_port': 0, 'ssu_port4': 0, 'ntcp2_identity': 'h2UCUdM9hsFpoSzCoTYjFakHMW9954GKtdcpjroFRds=', 'ntcp2_static': 'Blif68eMmDcCpKeQK5DDyjCOjV5Zn9Sxgv6janBicyc=', 'version': '0.9.60', 'isfloodfill': 0}, {'hash': 'tj1iUgNPxFSPFItlJ6KsNTxGpL5bwue1dh1Dk1q6FGY=', 'id': 'tj1iUg', 'country': '未知', 'public_time': '29\xa0分 前', 'ntcp2_ipv4': '', 'ntcp2_ipv4_port': 0, 'ntcp2_ipv6': '', 'ntcp2_ipv6_port': 0, 'ssu_port4': 0, 'ntcp2_identity': 'ksoWE9faKtrgZKjpVWApfh7HKjvCVfeFNsMNVpiL2g0=', 'ntcp2_static': 'moAjqR0IUBdVjWrTpPr0KWPiGyGxU~W0LEpdYoSY7x0=', 'version': '0.9.60', 'isfloodfill': 0}, {'hash': 'ZXiTNUSQ2JpoSZu1EqHH8z0sdFqFXHGWv4fx3anEIZs=', 'id': 'ZXiTNU', 'country': '美国', 'public_time': '14\xa0分 前', 'ntcp2_ipv4': '155.186.90.241', 'ntcp2_ipv4_port': 42578, 'ntcp2_ipv6': '', 'ntcp2_ipv6_port': 0, 'ssu_port4': 42578, 'ntcp2_identity': 'rmXQOS8Xvaf51x9nPxBJdyP6wnzytwvovKSvrKvgdxI=', 'ntcp2_static': 'SizY7p0LTRyRrYaZ5U4fzyV5AazGnYjw8wtSHvzVZ1w=', 'version': '0.9.60', 'isfloodfill': 0}, {'hash': '1ZagS~NXiW1SzHr4ivLbbJVc9~MLqtIQ9Ixl237qUB0=', 'id': '1ZagS~', 'country': '法国', 'public_time': '27\xa0分 前', 'ntcp2_ipv4': '', 'ntcp2_ipv4_port': 0, 'ntcp2_ipv6': '', 'ntcp2_ipv6_port': 0, 'ssu_port4': 0, 'ntcp2_identity': 'HMUNCjBJzOhYFVLIPurosLcznKegBhri46VQ62R1zRU=', 'ntcp2_static': '86yfZrpjtLSN-UIWqII34WCH12i~11lrRePbi0eLDWU=', 'version': '0.9.60', 'isfloodfill': 0}, {'hash': 'VRbpjYOwtSWiXX4ZyXYP6bbVeoZcrin-U2XG~y4Vva8=', 'id': 'VRbpjY', 'country': '德国', 'public_time': '33\xa0分 前', 'ntcp2_ipv4': '87.184.175.20', 'ntcp2_ipv4_port': 12646, 'ntcp2_ipv6': '', 'ntcp2_ipv6_port': 0, 'ssu_port4': 12646, 'ntcp2_identity': 'XLckb6d0-BvYlcfXr~malO1nwKtTfh0lDv56bFRz7II=', 'ntcp2_static': '6jVxPWw4Nndx9Vt5WKlDwn8bCFPvuuMKgxMe1NK2kEk=', 'version': '0.9.60', 'isfloodfill': 1}, {'hash': '15ivKYMq4LY52LP7lRjyGL~NaoRO~avYGUsw15jC6Ug=', 'id': '15ivKY', 'country': '未知', 'public_time': '42\xa0分 前', 'ntcp2_ipv4': '', 'ntcp2_ipv4_port': 0, 'ntcp2_ipv6': '', 'ntcp2_ipv6_port': 0, 'ssu_port4': 0, 'ntcp2_identity': '7DJRIyjh-qOgaP-TXRl5jZtOatLaBKuhO7Ut1mE5lSw=', 'ntcp2_static': 'OJfv4Vjcr0egGtZIr4SuGxLGnwZUtHFXpgx9i4FDDG4=', 'version': '0.9.60', 'isfloodfill': 0}, {'hash': 'nglxSZZVGdhWv8BMPNMb1w4HFYYa3Zj31MB8ofxotbk=', 'id': 'nglxSZ', 'country': '未知', 'public_time': '11\xa0分 前', 'ntcp2_ipv4': '', 'ntcp2_ipv4_port': 0, 'ntcp2_ipv6': '', 'ntcp2_ipv6_port': 0, 'ssu_port4': 0, 'ntcp2_identity': 'DECz1DcGbJV6fRQmnJXKorb~4Ag4A5xXjSgePbWFksw=', 'ntcp2_static': 'Z~PRkq~wzAvE2AYp4g81BX-DZ3CfK2BLj2773mrguCg=', 'version': '0.9.60', 'isfloodfill': 0}, {'hash': '5uXFQkq3r9n7AqWYQjflvZ52J7KXsiZ9RBbkNqOwwwk=', 'id': '5uXFQk', 'country': '未知', 'public_time': '26\xa0分 前', 'ntcp2_ipv4': '', 'ntcp2_ipv4_port': 0, 'ntcp2_ipv6': '', 'ntcp2_ipv6_port': 0, 'ssu_port4': 0, 'ntcp2_identity': 'R9gnJMBTrwnF9KoDeIYvkQII6dh9-Au9glZCRwroiqI=', 'ntcp2_static': 'R2cvzU~a9wEE7Fa21nSdRmjogoJYiW-eOnqC9Nt~5GQ=', 'version': '0.9.60', 'isfloodfill': 0}, {'hash': 'RRfBr~HQuIOmWRGA-TVT51-EM~k50x4xWG5rLd4u9SY=', 'id': 'RRfBr~', 'country': '未知', 'public_time': '37\xa0分 前', 'ntcp2_ipv4': '', 'ntcp2_ipv4_port': 0, 'ntcp2_ipv6': '', 'ntcp2_ipv6_port': 0, 'ssu_port4': 0, 'ntcp2_identity': 'ig~7sash4dfC9sJwevGtLwa2bbtZS8IMv9g5pIN1gbs=', 'ntcp2_static': 'Q-ax7tPDKWTGWS3AsLyimMe-GGk4isPBxDeYmX3eBWc=', 'version': '0.9.60', 'isfloodfill': 0}, {'hash': 'ug1Qdg22FzBaR2wfvQY0UqvbIsSjObdxnKe2PvqBpHs=', 'id': 'ug1Qdg', 'country': '未知', 'public_time': '33\xa0分 前', 'ntcp2_ipv4': '', 'ntcp2_ipv4_port': 0, 'ntcp2_ipv6': '', 'ntcp2_ipv6_port': 0, 'ssu_port4': 0, 'ntcp2_identity': '6VnfRoTwc7zuPvuqvvInI7VuMK7dWF-Um6LCOqFUiXY=', 'ntcp2_static': 'Hwblz1UpikpSYh4eowgf9~wc30Sz9qbw6xrRiC20g0Y=', 'version': '0.9.60', 'isfloodfill': 0}, {'hash': 'cNqPa49v8gypgCF7xAlacXJrTbiTcvpd5YJjkfQG2xo=', 'id': 'nglxSZ', 'country': '伊朗', 'public_time': '6\xa0分 前', 'ntcp2_ipv4': '', 'ntcp2_ipv4_port': 0, 'ntcp2_ipv6': '', 'ntcp2_ipv6_port': 0, 'ssu_port4': 0, 'ntcp2_identity': '66PZYjdXqq33s0cF7m-qn6tIKXfJppz~2itWmoZuu2Y=', 'ntcp2_static': 'HCWU4~-3iz3bhYQLgCIP-7wtkGfPchSfZDx0ZIijpF4=', 'version': '0.9.60', 'isfloodfill': 0}]
    pusher.push_mysql(data_list)  # netdb 是要插入的数据列表
