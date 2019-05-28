#  python3 -m pip install PyMySQL
import configparser
import pymysql.cursors
import datetime
# Connect to the database
config = configparser.ConfigParser()
config.read('config.ini')
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
                    VALUES (%s, '', %s, now(), now(), %s, %s, ''); """
                    cursor.execute(sql, (data['title'], data['publication_date'], author_id, pubisher_id))
                    connection.commit()



    print(get_publisher_id("노블엔진"))

    print(get_publisher_id("노블엔진3"))
    # data = {'title': '터무니없는 스킬로 이세계 방랑 밥 5 - S Novel+', 'author_name': '에구치 렌', 'publisher_name': '소미미디어'}
    # insert_light_novel(data)
    #
    # # connection is not autocommit by default. So you must commit to save
    # # your changes.
    # connection.commit()
    #
    # with connection.cursor() as cursor:
    #     # Read a single record
    #     sql = "SELECT `id`, `password` FROM `users` WHERE `email`=%s"
    #     cursor.execute(sql, ('webmaster@python.org',))
    #     result = cursor.fetchone()
    #     print(result)
    with open('./text.txt', 'r', encoding='UTF8') as infile:
        while True:
            lines = []
            line = infile.readline()
            if not line:
                break
            lines.append(line)
            line = infile.readline()
            if not line:
                break
            lines.append(line)
            line = infile.readline()
            if not line:
                break
            lines.append(line)
            print(lines)
            name = lines[1][:-4]
            [author, publisher, publication_date] = lines[2][:-1].split(" | ")
            print(name)
            print(author)
            print(publisher)
            print(publication_date)
            publication_datetime = datetime.datetime.strptime(publication_date, "%Y년 %m월")
            data = {'title': name, 'author_name': author, 'publisher_name': publisher, 'publication_date': publication_datetime}
            insert_light_novel(data)
            print(publication_datetime)
finally:
    connection.close()