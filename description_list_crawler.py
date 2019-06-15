import configparser
import pymysql.cursors
import description
import pprint
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
    (SELECT `index_description`, `publisher_description`, `aladin_id` FROM `light_novel` LIMIT %s, %s) `light_novel`
    WHERE (`light_novel`.`index_description` = "" AND `light_novel`.`publisher_description` =  "");
    """
    # sql = """
    #     SELECT `aladin_id` FROM
    #     (SELECT `index_description`, `publisher_description`, `aladin_id` FROM `light_novel` LIMIT %s, %s) `light_novel`;
    # """
    cursor.execute(sql, (page*row, row))
    result = cursor.fetchall()
    if result is None:
        return []
    else:
        return list(map(lambda x: x['aladin_id'], result))

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

total_count = get_light_novel_count()
row = 100
total_page = int(total_count / row)
if total_count % row > 0:
    total_page = total_page + 1

for page in range(0, total_page):
    print(page)
    aladin_ids = get_light_novel_aladin_id(page, row)
    description_object_list = list(map(lambda x: description.get_description(x), aladin_ids))
    for description_object in description_object_list:
        pp = pprint.PrettyPrinter(indent=4)
        pp.pprint(description_object)
        update_light_novel_description(description_object)
