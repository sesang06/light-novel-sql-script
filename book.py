import urllib3
import re
from bs4 import BeautifulSoup 
def load_information(book_id):
    #https://www.aladin.co.kr/shop/wproduct.aspx?ItemId=193457128
    http = urllib3.PoolManager()
    response = http.request('GET', "https://www.aladin.co.kr/shop/wproduct.aspx?ItemId={}".format(book_id),headers={
        'USER-AGENT':'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:67.0) Gecko/20100101 Firefox/67.0'
    } )
    htmltext = response.data.decode('euc-kr')
    #파싱한다.
    soup = BeautifulSoup(htmltext, 'html.parser')
    el = soup.find("div",{"id":"divProductBook"})
    #series 아이디
    series_id = None
    reg = re.compile(r'/shop/common/wbookitem.aspx\?bookid=([0-9]+)')
    for atag in el.find_all("a"):
        href = atag.attrs['href']
        m = reg.match(href)
        if m is not None:
            series_id = m.group(1)
            break
    #책 소개
    #text = None
    #el = soup.find_all("div",{"class":"Ere_prod_mconts_LL"})
    #for divtag in soup.find_all("div",{"class":"Ere_prod_mconts_LL"}):
    #    if divtag.contents[0] == "책소개":
    #        el = divtag.find_next()
    #        text = el.text
    #        break
    #책 목차
    #el = soup.find("div",{"id":"div_TOC_Short"})
    #index_text = el.contents
    title = soup.find("meta", {"property":"og:title"}).attrs("content")
    author = soup.find("meta", {"property":"og:author"}).attrs("content")
    return {"series_id":series_id, "title": title, "author":author}
print(load_information(193457128))