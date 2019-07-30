import configparser
import pymysql.cursors
import datetime
import series
import book
import book_functions
import pprint
import time
config = configparser.ConfigParser()
config.read('config.ini')

connection = pymysql.connect(host=config['DATABASE']['HOST'],
                             user=config['DATABASE']['USER'],
                             password=config['DATABASE']['PASSWORD'],
                             db=config['DATABASE']['DB'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)
cursor = connection.cursor()
def get_light_novel_count():
    sql = """
    SELECT COUNT(*) FROM light_novel;
    """
    cursor.execute(sql)
    result = cursor.fetchone()
    if result is None:
        return 0
    else:
        return result['COUNT(*)']

def get_light_novel_aladin_id(page, row):
    sql = """
    SELECT `aladin_id` FROM 
    (SELECT `adult`, `series_aladin_id`, `aladin_id` FROM `light_novel` LIMIT %s, %s) `light_novel`
    WHERE (`light_novel`.`series_aladin_id` = 0 AND `light_novel`.`adult` = 0);
    """

    cursor.execute(sql, (page*row, row))
    result = cursor.fetchall()
    if result is None:
        return []
    else:
        return list(map(lambda x: x['aladin_id'], result))

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

total_count = get_light_novel_count()
row = 100
total_page = int(total_count / row)
if total_count % row > 0:
    total_page = total_page + 1
pp = pprint.PrettyPrinter(indent=4)

for page in range(40, total_page):
    print(page)
    aladin_ids = get_light_novel_aladin_id(page, row)
    pp.pprint(aladin_ids)
    time.sleep(1)
    series_id_lists = list(map(lambda x: book.get_parent_series_id(x), aladin_ids))
    series_filtered_id_lists = list(filter(lambda x: x != 0, series_id_lists))
    series_object_list = list(map(lambda x: series.get_series(x), series_filtered_id_lists))

    for series_object in series_object_list:
        insert_light_novel_series(series_object)
        pp.pprint(series_object)

        itemIds = series_object['item_ids']
        filtered_item_ids = list(filter(lambda x: not book_functions.is_light_novel_in_database(x, cursor), itemIds))
        print(filtered_item_ids)
        itemInfos = list(map(lambda x: book_functions.getItemInfo(x), filtered_item_ids))
        datas = list(map(lambda x: book_functions.convert_item_to_data(x), itemInfos))

        for data in datas:
            pp = pprint.PrettyPrinter(indent=4)
            pp.pprint(data)
            book_functions.insert_light_novel(data, cursor, connection)

        update_light_novel_series_id(series_object)
