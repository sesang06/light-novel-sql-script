import urllib3
from bs4 import BeautifulSoup
import json
import configparser
import pymysql.cursors
import datetime
import pprint

config = configparser.ConfigParser()
config.read('config.ini')

def is_light_novel_in_database(item_id, cursor):
    sql = "SELECT `id` FROM light_novel WHERE `aladin_id`=%s;"
    cursor.execute(sql, item_id)
    result = cursor.fetchone()
    if result is None:
        return False
    else:
        return True

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

def get_publisher_id(publisher_name, cursor, connection):
    sql = "SELECT `id` FROM publisher WHERE `name`=%s;"
    cursor.execute(sql, publisher_name)
    result = cursor.fetchone()
    if result is not None:
        return int(result['id'])
    sql = "INSERT INTO publisher (`name`, `created_at`, `updated_at`) VALUES (%s, now(), now());"
    cursor.execute(sql, publisher_name)
    connection.commit()
    return int(cursor.lastrowid)
def get_author_id(author_name, cursor, connection):
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

def insert_light_novel(data, cursor, connection):

    sql = "SELECT `id` FROM light_novel WHERE `aladin_id`=%s;"
    cursor.execute(sql, data['aladin_id'])
    result = cursor.fetchone()
    if result is None:
        author_id = get_author_id(data['author_name'], cursor, connection)
        pubisher_id = get_publisher_id(data['publisher_name'], cursor, connection)
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
        sales_price,
        index_description,
        publisher_description
        )
        VALUES (%s, %s, %s, now(), now(), %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, '', ''); """
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
        author_id = get_author_id(data['author_name'], cursor, connection)
        pubisher_id = get_publisher_id(data['publisher_name'], cursor, connection)
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