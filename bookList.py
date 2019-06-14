import urllib3
from bs4 import BeautifulSoup

url = "https://www.aladin.co.kr/shop/wbrowse.aspx?SortOrder=2&page=1&CID=50927&ViewRowsCount=25"
http = urllib3.PoolManager()

r = http.request(
    'GET',
    url)
# print(r.data)
# htmltext = response.data.decode('euc-kr')
# 파싱한다.

soup = BeautifulSoup(r.data, 'html.parser')


divs = soup.find_all("div", class_="ss_book_box")
itemIds = list(map(lambda x: x.get("itemid"), divs))
print(itemIds)