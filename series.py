import urllib3
import re
import time
import requests
from bs4 import BeautifulSoup

def get_series(series_id):
    book_id_list = []
    #https://www.aladin.co.kr/shop/common/wbookitem.aspx?bookid=31774725
    urllib3.disable_warnings()
    time.sleep(10)
    http = urllib3.PoolManager()
    response = requests.get(
        "https://www.aladin.co.kr/shop/common/wbookitem.aspx",
        params={'bookid': series_id,
                'ViewRowsCount': 100
                },
        verify=False
    )
    soup = BeautifulSoup(response.text, 'html.parser')
    divs = soup.find_all("div", class_="ss_book_box")
    print('series_idi')
    print(series_id)
    item_ids = list(map(lambda x: x.get("itemid"), divs))
    print(item_ids)
    title_text = soup.find('a', {'href' : '/shop/common/wbookitem.aspx?bookid={}'.format(series_id) }).contents
    return {'aladin_id': series_id,
            'item_ids': item_ids,
            'title_text': title_text}
