import urllib3
from bs4 import BeautifulSoup
import json
import configparser
import pymysql.cursors
import datetime
config = configparser.ConfigParser()
config.read('config.ini')

connection = pymysql.connect(host=config['DATABASE']['HOST'],
                             user=config['DATABASE']['USER'],
                             password=config['DATABASE']['PASSWORD'],
                             db=config['DATABASE']['DB'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

cursor = connection.cursor()

def getItemIds(page):
    url = "https://www.aladin.co.kr/shop/wbrowse.aspx"
    http = urllib3.PoolManager()

    r = http.request(
        'GET',
        url,
        fields={'SortOrder': 2,
                'page': page,
                'CID': '50927',
                'ViewRowsCount': '100'
                })
    # print(r.data)
    # htmltext = response.data.decode('euc-kr')
    # 파싱한다.

    soup = BeautifulSoup(r.data, 'html.parser')


    divs = soup.find_all("div", class_="ss_book_box")
    itemIds = list(map(lambda x: x.get("itemid"), divs))
    return itemIds

def getItemInfo(itemId):
    http = urllib3.PoolManager()
    r = http.request(
        'GET',
        'http://www.aladin.co.kr/ttb/api/ItemLookUp.aspx',
        fields={'ttbkey': config['ALADIN']['ttbkey'],
                'ItemId': itemId,
                'Version': '20131101',
                'output': 'js',
                'ItemIdType': 'ItemId'
                })
    result = json.loads(r.data.decode('utf-8'))

    return result['item'][0]


def get_connection():
    connection = pymysql.connect(host=config['DATABASE']['HOST'],
                                 user=config['DATABASE']['USER'],
                                 password=config['DATABASE']['PASSWORD'],
                                 db=config['DATABASE']['DB'],
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

def get_publisher_id(publisher_name):
    sql = "SELECT `id` FROM publisher WHERE `name`=%s;"
    cursor.execute(sql, publisher_name)
    result = cursor.fetchone()
    if result is not None:
        return int(result['id'])
    sql = "INSERT INTO publisher (`name`, `created_at`, `updated_at`) VALUES (%s, now(), now());"
    cursor.execute(sql, publisher_name)
    connection.commit()
    return int(cursor.lastrowid)
def get_author_id(author_name):
    sql = "SELECT `id` FROM author WHERE `name`=%s;"
    cursor.execute(sql, author_name)
    result = cursor.fetchone()
    if result is not None:
        return int(result['id'])
    sql = "INSERT INTO author (`name`, `created_at`, `updated_at`) VALUES (%s, now(), now());"
    cursor.execute(sql, author_name)
    connection.commit()
    return int(cursor.lastrowid)

def convert_item_to_data(item):
    data = {}
    data['title'] = item['title']
    data['description'] = item['description']
    data['publication_date'] = item['pubDate']
    data['author_name'] = item['author']
    data['publisher_name'] = item['publisher']
    data['thumbnail'] = item['cover']
    data['link'] = item['link']
    data['isbn'] = item['isbn']
    data['isbn13'] = item['isbn13']
    data['aladin_id'] = item['itemId']
    data['adult'] = item['adult']
    data['sales_point'] = item['salesPoint']
    data['standard_price'] = item['priceStandard']
    data['sales_price'] = item['priceSales']
    return data

def insert_light_novel(data):

    sql = "SELECT `id` FROM light_novel WHERE `aladin_id`=%s;"
    cursor.execute(sql, data['aladin_id'])
    result = cursor.fetchone()
    if result is None:
        author_id = get_author_id(data['author_name'])
        pubisher_id = get_publisher_id(data['publisher_name'])
        sql = """INSERT
        INTO
        light_novel(
        title,
        description,
        publication_date,
        created_at,
        updated_at,
        author_id,
        publisher_id,
        thumbnail,
        hit_rank,
        link,
        isbn,
        isbn13,
        aladin_id,
        adult,
        sales_point,
        standard_price,
        sales_price
        )
        VALUES (%s, %s, %s, now(), now(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s); """
        cursor.execute(sql, (data['title'],
                             data['description'],
                             data['publication_date'],
                             author_id,
                             pubisher_id,
                             data['thumbnail'],
                             0,
                             data['link'],
                             data['isbn'],
                             data['isbn13'],
                             data['aladin_id'],
                             data['adult'],
                             data['sales_point'],
                             data['standard_price'],
                             data['sales_price']
                             )
                       )
        connection.commit()
    else:
        author_id = get_author_id(data['author_name'])
        pubisher_id = get_publisher_id(data['publisher_name'])
        sql = """
        UPDATE light_novel
        SET 
        title = %s,
        description = %s,
        publication_date = %s,
        updated_at = now(),
        author_id = %s,
        publisher_id = %s,
        thumbnail = %s,
        link = %s,
        isbn = %s,
        isbn13 = %s,
        adult = %s,
        sales_point = %s,
        standard_price = %s,
        sales_price = %s
        WHERE aladin_id = %s;
        """
        cursor.execute(sql, (data['title'],
                             data['description'],
                             data['publication_date'],
                             author_id,
                             pubisher_id,
                             data['thumbnail'],
                             data['link'],
                             data['isbn'],
                             data['isbn13'],
                             data['adult'],
                             data['sales_point'],
                             data['standard_price'],
                             data['sales_price'],
                             data['aladin_id']
                             )
                       )
        connection.commit()

# 현재 페이지 57까지
for page in range(33, 58):
    print("pages" + str(page))
    itemIds = getItemIds(page)
    itemInfos = list(map(lambda x: getItemInfo(x), itemIds))
    datas = list(map(lambda x: convert_item_to_data(x), itemInfos))

    for data in datas:
        insert_light_novel(data)

connection.close()