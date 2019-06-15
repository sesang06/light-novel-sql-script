import configparser
import pymysql.cursors
import datetime
import series
import book
config = configparser.ConfigParser()
config.read('config.ini')

connection = pymysql.connect(host=config['DATABASE']['HOST'],
                             user=config['DATABASE']['USER'],
                             password=config['DATABASE']['PASSWORD'],
                             db=config['DATABASE']['DB'],
                             charset='utf8mb4',
                             cursorclass=pymysql.cursors.DictCursor)

cursor = connection.cursor()

def get_light_novel_aladin_id():
    sql = "SELECT `aladin_id` FROM light_novel WHERE `series_aladin_id`=0 LIMIT 10;"
    cursor.execute(sql)
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
    print(sql)

    cursor.execute(sql, ([series_object['aladin_id']] + item_ids
                       )
                   )
    connection.commit()
aladin_ids = get_light_novel_aladin_id()
series_id_lists = list(map(lambda x: book.get_parent_series_id(x), aladin_ids))
series_filtered_id_lists = list(filter(lambda x: x != 0, series_id_lists))
series_object_list = list(map(lambda x: series.get_series(x), series_filtered_id_lists))

for series_object in series_object_list:
    insert_light_novel_series(series_object)
    update_light_novel_series_id(series_object)