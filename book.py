import urllib3
import re
from bs4 import BeautifulSoup 
def get_parent_series_id(book_id):
    #https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=193457128
    http = urllib3.PoolManager()
    response = http.request('GET', "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId={}".format(book_id),headers={
        'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
    } )
    #파싱한다.
    soup = BeautifulSoup(response.data, 'html.parser')
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
