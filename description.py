import urllib3
import re
from bs4 import BeautifulSoup
def get_publisher_description(item_id):
    http = urllib3.PoolManager()
    response = http.request(
        'GET',
        "https://www.aladin.co.kr/shop/product/getContents.aspx",
        fields={'itemid': item_id,
                'name': 'PublisherDesc'
                },
        headers={
            'referer':'https://www.aladin.co.kr/shop/wproduct.aspx?ItemId={}'.format(item_id),
            'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'}
    )
    soup = BeautifulSoup(response.data, 'html.parser')
    desc = soup.find(id='div_PublisherDesc_All')
    if desc is None:
        # desc = soup.find(id='')
        # print(soup)
        desc = soup.find_all("div", class_="Ere_prod_mconts_R")
        if desc is None or len(desc) == 0 or len(desc) == 1:
            return ""
        else:
            return desc[1].get_text("\n").strip()
    else:
        return desc.contents[0].get_text("\n").strip()


def get_index_description(item_id):
    http = urllib3.PoolManager()
    response = http.request(
        'GET',
        "https://www.aladin.co.kr/shop/product/getContents.aspx",
        fields={'itemid': item_id,
                'name': 'Introduce'
                },
        headers={
            'referer':'https://www.aladin.co.kr/shop/wproduct.aspx?ItemId={}'.format(item_id),
            'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'}
    )
    soup = BeautifulSoup(response.data, 'html.parser')
    # print(soup)
    desc = soup.find(id='div_TOC_All')
    if desc is None:
        desc = soup.find(id='tocTemplate')
        if desc is None:
            return ""
        else:
            return desc.get_text("\n").strip()
    else:
        desc = desc.get_text()
    return desc.strip()
def get_description(item_id):
    index_description = get_index_description(item_id)
    publisher_description = get_publisher_description(item_id)
    return {'aladin_id': item_id,
            'index_description': index_description,
            'publisher_description': publisher_description}
    # return desc.contents[0].get_text("\n")
# series = get_index_description(193457128)
# print(series)
# series = get_index_description(54259905)
# print(series)
# series = get_index_description(186508733)
# print(series)
#
# series = get_publisher_description(193457128)
# print(series)
# series = get_publisher_description(54259905)
# print(series)
# series = get_publisher_description(186508733)
# print(series)
# series = get_publisher_description(121525740)
#