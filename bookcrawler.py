# $ pip install urllib3
import urllib3
import json
import configparser
import pymysql.cursors
import datetime
config = configparser.ConfigParser()
config.read('config.ini')
http = urllib3.PoolManager()

for i in range(1,20):
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

    total_results = result['totalResults']
    items = result['item']

    connection = pymysql.connect(host=config['DATABASE']['HOST'],
                                 user=config['DATABASE']['USER'],
                                 password=config['DATABASE']['PASSWORD'],
                                 db=config['DATABASE']['DB'],
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)

    try:

        def get_publisher_id(publisher_name):
            with connection.cursor() as cursor:
                sql = "SELECT `id` FROM publisher WHERE `name`=%s;"
                cursor.execute(sql, publisher_name)
                result = cursor.fetchone()
                if result is not None:
                    return int(result['id'])
                with connection.cursor() as cursor:
                    sql = "INSERT INTO publisher (`name`, `created_at`, `updated_at`) VALUES (%s, now(), now());"
                    cursor.execute(sql, publisher_name)
                    connection.commit()
                    return int(cursor.lastrowid)
        def get_author_id(author_name):
            with connection.cursor() as cursor:
                sql = "SELECT `id` FROM author WHERE `name`=%s;"
                cursor.execute(sql, author_name)
                result = cursor.fetchone()
                if result is not None:
                    return int(result['id'])
                with connection.cursor() as cursor:
                    sql = "INSERT INTO author (`name`, `created_at`, `updated_at`) VALUES (%s, now(), now());"
                    cursor.execute(sql, author_name)
                    connection.commit()
                    return int(cursor.lastrowid)

        def insert_light_novel(data):
            with connection.cursor() as cursor:
                sql = "SELECT `id` FROM light_novel WHERE `title`=%s;"
                cursor.execute(sql, data['title'])
                result = cursor.fetchone()
                if result is None:
                    with connection.cursor() as cursor:
                        author_id = get_author_id(data['author_name'])
                        pubisher_id = get_publisher_id(data['publisher_name'])
                        print(author_id)
                        print(pubisher_id)
                        sql = """INSERT
                        INTO
                        light_novel(title, description, publication_date, created_at, updated_at, author_id, publisher_id, thumbnail)
                        VALUES (%s, %s, %s, now(), now(), %s, %s, %s); """
                        cursor.execute(sql, (data['title'], data['description'], data['publication_date'], author_id, pubisher_id, data['thumbnail']))
                        connection.commit()


        for item in items:
            data = {}
            data['title'] = item['title']
            data['description'] = item['description']
            data['publication_date'] = item['pubDate']
            data['author_name'] = item['author']
            data['publisher_name'] = item['publisher']
            data['thumbnail'] = item['cover']
            insert_light_novel(data)
    finally:
        connection.close()
