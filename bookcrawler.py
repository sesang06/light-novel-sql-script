# $ pip install urllib3
import urllib3
import json
import configparser
import pymysql.cursors
import pprint
import book
import series
import description
import time as t
import os
base_path = os.path.dirname(os.path.realpath(__file__))
config = configparser.ConfigParser()
config.read(os.path.join(base_path, 'config.ini'))
http = urllib3.PoolManager()

connection = pymysql.connect(host=config['DATABASE']['HOST'],
                             user=config['DATABASE']['USER'],
                             password=config['DATABASE']['PASSWORD'],
                             db=config['DATABASE']['DB'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()


def is_light_novel_in_database(item_id):
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
    if 'bestRank' in item:
        data['hit_rank'] = item['bestRank']
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
        if 'hit_rank' in data:
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
                                 data['hit_rank'],
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
        else:
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
            VALUES (%s, %s, %s, now(), now(), %s, %s, %s, 0, %s, %s, %s, %s, %s, %s, %s, %s, '', ''); """

            cursor.execute(sql, (data['title'],
                                 data['description'],
                                 data['publication_date'],
                                 author_id,
                                 pubisher_id,
                                 data['thumbnail'],
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
        if 'hit_rank' in data:
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
            hit_rank = %s,
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
                                 data['hit_rank'],
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
        else:
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

def get_now():
    sql = "SELECT NOW();"
    cursor.execute(sql)
    result = cursor.fetchone()
    return result['NOW()']

def reset_hit_rank(time):
    sql = """UPDATE light_novel
            SET 
            hit_rank = 0
            WHERE updated_at < %s
            """
    cursor.execute(sql, time)
    connection.commit()

def insert_light_novel_series(series_object):
    sql = "SELECT `id` FROM light_novel_series WHERE `aladin_id`=%s;"
    cursor.execute(sql, series_object['aladin_id'])
    result = cursor.fetchone()
    if result is None:
        sql = """INSERT
            INTO
            light_novel_series(
            title,
            created_at,
            updated_at,
            aladin_id)
            VALUES
            (%s, now(), now(), %s);"""
        cursor.execute(sql, (series_object['title_text'],
                             series_object['aladin_id']
                             )
                       )
        connection.commit()
def update_light_novel_series_id(series_object):
    item_ids = series_object['item_ids']
    format_strings = ','.join(['%s'] * len(item_ids))
    update_caluse = """
            UPDATE light_novel
            SET 
            updated_at = now(),
            series_aladin_id = %s"""
    where_caluse = """
            WHERE aladin_id IN (%s);
            """ % format_strings
    sql = update_caluse+where_caluse

    cursor.execute(sql, ([series_object['aladin_id']] + item_ids
                       )
                   )
    connection.commit()

def get_light_novel_info(data):
    sql = "SELECT * FROM light_novel WHERE `aladin_id`=%s;"
    cursor.execute(sql, data['aladin_id'])
    result = cursor.fetchone()
    return result
def update_series_info(data):
    if data['series_aladin_id'] == 0 and data['adult'] == 0:
        t.sleep(1)
        series_id = book.get_parent_series_id(data['aladin_id'])
        if series_id != 0:
            t.sleep(1)
            series_object = series.get_series(series_id)
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(series_object)
            insert_light_novel_series(series_object)
            update_light_novel_series_id(series_object)

def update_light_novel_description(description_object):
    sql = """
    UPDATE light_novel
    SET 
    updated_at = now(),
    index_description = %s,
    publisher_description = %s
    WHERE aladin_id = %s
    """
    cursor.execute(sql,
                   (description_object['index_description'],
                    description_object['publisher_description'],
                    description_object['aladin_id']
                    ))
    connection.commit()

def update_description_info(data):
    if data['publisher_description'] == "" or data['index_description'] == "":
        t.sleep(1)
        description_object = description.get_description(data['aladin_id'])
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(description_object)
        update_light_novel_description(description_object)
time = get_now()

for i in range(1,21):
    r = http.request(
        'GET',
        'http://www.aladin.co.kr/ttb/api/ItemList.aspx',
        fields={'ttbkey': config['ALADIN']['ttbkey'],
                'QueryType': 'Bestseller',
                'MaxResults': '100',
                'Start': i,
                'SearchTarget': 'BOOK',
                'Version': '20131101',
                'output': 'js',
                'categoryid': '50927'})
    result = json.loads(r.data.decode('utf-8'))

    iteminfos = result['item']
    datas = list(map(lambda x: convert_item_to_data(x), iteminfos))
    t.sleep(1)
    for data in datas:
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(data)
        insert_light_novel(data)
        new_data = get_light_novel_info(data)
        update_series_info(new_data)
        update_description_info(new_data)

for i in range(1,21):
    r = http.request(
        'GET',
        'http://www.aladin.co.kr/ttb/api/ItemList.aspx',
        fields={'ttbkey': config['ALADIN']['ttbkey'],
                'QueryType': 'ItemNewAll',
                'MaxResults': '100',
                'Start': i,
                'SearchTarget': 'BOOK',
                'Version': '20131101',
                'output': 'js',
                'categoryid': '50927'})
    result = json.loads(r.data.decode('utf-8'))

    iteminfos = result['item']
    datas = list(map(lambda x: convert_item_to_data(x), iteminfos))

    for data in datas:
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(data)
        insert_light_novel(data)
        new_data = get_light_novel_info(data)
        update_series_info(new_data)
        update_description_info(new_data)


reset_hit_rank(time)
