import urllib3
import re
from bs4 import BeautifulSoup 
def load_information(series_id):
    book_id_list = []
    #https://www.aladin.co.kr/shop/common/wbookitem.aspx?bookid=31774725
    http = urllib3.PoolManager()
    response = http.request('GET', "https://www.aladin.co.kr/shop/common/wbookitem.aspx?bookid={}".format(series_id),headers={
        'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
    } )
    htmltext = response.data.decode('euc-kr')
    #파싱한다.
    soup = BeautifulSoup(htmltext, 'html.parser')
    reg = re.compile(r'http://www.aladin.co.kr/shop/wproduct.aspx\?ItemId=([0-9]+)')
    for atag in soup.find_all("a", {"class":"bo3"}):
        href = atag.attrs['href']
        m = reg.match(href)
        if m is not None:
            book_id_list.append( m.group(1))
    title = str( soup.find("h1",{"class":"br2010_subt"}).text)
    title = title[:title.rfind(":")].trim()
    
    return {"title":title, "book_ids": book_id_list}
load_information(31774725)