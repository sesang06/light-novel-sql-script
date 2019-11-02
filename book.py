import urllib3
import re
from bs4 import BeautifulSoup 
import time
import ssl
import requests

def get_parent_series_id(book_id):
    time.sleep(1)
    response = requests.get(
        "http://www.aladin.co.kr/shop/wproduct.aspx?ItemId={}".format(book_id),
        verify=False
    ).text
    #파싱한다.
    print('book+id')
    print(book_id)
    soup = BeautifulSoup(response, 'html.parser')
    el = soup.find("div",{"id":"divProductBook"})
    if el == None :
        return 0
    #series 아이디
    series_id = None
    reg = re.compile(r'/shop/common/wbookitem.aspx\?bookid=([0-9]+)')
    for atag in el.find_all("a"):
        href = atag.attrs['href']
        m = reg.match(href)
        if m is not None:
            series_id = m.group(1)
            break
    return series_id
