import requests
from bs4 import BeautifulSoup
import re

def is_ip(address):
    """
    判断是ipv4还是ipv6
    0 不是ip地址
    4 ipv4
    6 ipv6
    """
    ipv4_pattern = re.compile(r"^\d{1,3}(\.\d{1,3}){3}$")
    ipv6_pattern = re.compile(r"^([0-9a-fA-F]{1,4}:){7}[0-9a-fA-F]{1,4}$")
    if ipv4_pattern.match(address):
        return 4
    elif ipv6_pattern.match(address):
        return 6
    else:
        return 0




def get_transport(tr_list):
    transport = {}
    NTCP_count = 0
    SSU_count = 0
    for transport_data in tr_list[4].find_all("td")[1].find_all("b"):
        transport_type = transport_data.get_text(strip=True).rstrip(':')
        
        # 检查键是否已存在并添加递增的数字后缀
        if transport_type == "NTCP2":
            NTCP_count += 1
            unique_transport_type = f"{transport_type}_{NTCP_count}"
        elif transport_type == "SSU2":
            SSU_count += 1
            unique_transport_type = f"{transport_type}_{SSU_count}"
        else:
            unique_transport_type = f"{transport_type}"

        span_siblings = transport_data.find_next_siblings('span', class_='nowrap')

        transport_data = {}
        for span in span_siblings:
            name_tag = span.find('span', class_='netdb_name')
            info_tag = span.find('span', class_='netdb_info')

            if name_tag and info_tag:
                name = name_tag.get_text(strip=True).rstrip(':')
                info = info_tag.get_text(strip=True)
                transport_data[name] = info

        # 添加独特的传输类型键和对应的数据
        transport[unique_transport_type] = transport_data
    return transport, NTCP_count, SSU_count

def handle_transport(transport, NTCP_count, SSU_count):
    ntcp2_ipv4 = ""
    ntcp2_port4 = 0
    ntcp2_ipv6 = ""
    ntcp2_port6 = 0
    ssu2_port6 = 0
    ssu2_port4 = 0
    i = ""
    s = ""
    for count1 in range(NTCP_count):
        content = transport[f"NTCP2_{count1 + 1}"]
        if "s" in content:
            s = content["s"]
        if "i" in content:
            i = content["i"]
        if "主机" in content:
            host = content["主机"]
            cc = is_ip(host)
            if cc == 4:
                ntcp2_ipv4 = host
                if "端口" in content:
                    ntcp2_port4 = int(content["端口"])
            elif cc == 6:
                ntcp2_ipv6 = host
                if "端口" in content:
                    ntcp2_port6 = int(content["端口"])
    for count2 in range(SSU_count):
        content = transport[f"SSU2_{count2 + 1}"]
        if "端口" in content:
            ssu2_port6 = int(content["端口"])
            ssu2_port4 = int(content["端口"])
    return ntcp2_ipv4, ntcp2_port4, ntcp2_ipv6, ntcp2_port6, ssu2_port6, ssu2_port4, i, s

def handle_floodfill_version(content):
     # 查找<code>标签
    code_tag = content.find('code')

    # 提取文本并分割成行
    lines = code_tag.get_text().split('\n')

    # 初始化变量
    caps = ""
    router_version = ""

    # 在每行中查找caps和router.version
    for line in lines:
        if 'caps =' in line:
            caps = line.split('=')[1].strip()
        elif 'router.version =' in line:
            router_version = line.split('=')[1].strip()
    if 'f' in caps:
        is_floodfill = 1
    else:
        is_floodfill = 0
    return router_version, is_floodfill


def getnetdb(table):
    entry = {}
    tr_list = table.find_all('tr')
    entry['hash'] = tr_list[0].find("th").find("code").get_text()
    entry['id'] = tr_list[0]['id']
    try:
        entry["country"] = tr_list[0].find_all("th")[1].find("img")['title']
    except TypeError:
        entry["country"] = "未知"
    entry["public_time"] = tr_list[1].find_all("td")[1].find("span").get_text()

    transport, NTCP_count, SSU_count = get_transport(tr_list)
    entry['ntcp2_ipv4'], entry['ntcp2_ipv4_port'], entry['ntcp2_ipv6'], entry['ntcp2_ipv6_port'], entry['ssu_port4'], entry['ssu_port4'], entry['ntcp2_identity'], entry["ntcp2_static"] = handle_transport(transport, NTCP_count, SSU_count)

    entry['version'], entry['isfloodfill'] = handle_floodfill_version(tr_list[5])
    

    return entry

def parse_html(html):
    """ 解析HTML，提取所需数据 """
    soup = BeautifulSoup(html, 'html.parser')
    netdb = []

    # 查找所有带有特定类名的表格
    netdb_tables = soup.find_all('table', class_='netdbentry')

    for table in netdb_tables:
        netdb.append(getnetdb(table))



    return netdb

def run_crawl(url):
    """ 获取给定URL的HTML内容 """
    response = requests.get(url)
    return parse_html(response.text)

if __name__ == "__main__":
    url = 'http://127.0.0.1:7657/netdb?pg=3&ps=500&v=0.9.60'  # 替换为你要爬取的页面的URL
    netdb = run_crawl(url)

