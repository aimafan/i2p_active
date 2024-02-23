# 从特定url中获得i2p的所有版本和对应的数量
# url：http://127.0.0.1:7657/netdb
import requests
from bs4 import BeautifulSoup


def parse_html(content):
    # 找到包含版本号和数量的表格
    soup = BeautifulSoup(content, "html.parser")
    version_table = soup.find("table", id="netdbversions")

    # 创建一个字典来存储版本号和数量
    version_dict = {}
    # 遍历表格中的所有行，提取版本号和数量
    for row in version_table.find_all("tr")[1:]:  # 跳过表头 # type: ignore
        columns = row.find_all("td")
        version = columns[0].text.strip()
        count = int(columns[1].text.strip())
        version_dict[version] = count

    return version_dict


def get_versions(url):
    response = requests.get(url)
    return parse_html(response.text)


if __name__ == "__main__":
    url = "http://127.0.0.1:7657/netdb"
    # 这里versions是一个字典，包括版本和对应的数字
    versions = get_versions(url)
    print(versions)
