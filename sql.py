import pymysql

# 设计一个全局的配置文件
# config = config.sql_config

config = {
    'user': 'root',
    'password': '123456',
    'host': '180.3.15.63',
    'database': "shanghai",
}


def operational_data(fun, sql):
        db = pymysql.connect(**config)
        cursor = db.cursor()

        if fun == 'find':
                cursor.execute(sql)
                data = cursor.fetchall()
                for i in data:
                        # print(i[0])
                        # print(i[1])
                        pass
                db.close()
                return data

        elif fun == 'insert':
                try:
                        cursor.execute(sql)
                        print('lll')
                        db.commit()
                        flag = True
                except:
                        db.rollback()
                        flag = False
                db.close()
                return flag
        elif fun == 'update':
                try:
                        cursor.execute(sql)
                        db.commit()
                        flag = True
                except:
                        db.rollback()
                        flag = False
                # 关闭数据库连接
                db.close()
                return flag



#
# def insert():
#         print("插入数据")
#
# def select():
#         print("查询数据")
#
# opt = {
#         'insert': insert,
#         'select': select,
# }
#
# def opt_choice(func):
#         opt.get(func)()
#
# if __name__ == '__main__':
#     opt_choice('insert')