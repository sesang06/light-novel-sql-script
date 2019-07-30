import urllib3
import re
import time
from bs4 import BeautifulSoup 
def get_series(series_id):
    book_id_list = []
    #https://www.aladin.co.kr/shop/common/wbookitem.aspx?bookid=31774725
    time.sleep(1)
    http = urllib3.PoolManager()
    response = http.request(
        'GET',
        "https://www.aladin.co.kr/shop/common/wbookitem.aspx",
        fields={'bookid': series_id,
                'ViewRowsCount': 100
                },
        headers={
            'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'}
    )
    soup = BeautifulSoup(response.data, 'html.parser')
    divs = soup.find_all("div", class_="ss_book_box")
    print('series_idi')
    print(series_id)
    item_ids = list(map(lambda x: x.get("itemid"), divs))
    print(item_ids)
    title_text = soup.find('a', {'href' : '/shop/common/wbookitem.aspx?bookid={}'.format(series_id) }).contents
    return {'aladin_id': series_id,
            'item_ids': item_ids,
            'title_text': title_text}
