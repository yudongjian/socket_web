import pymysql

config = {
        'user': 'root',
        'password': 'mysql',
        'host': '127.0.0.1',
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

        if fun == 'insert':
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
        if fun == 'update':
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

sql1 = "select * from user"
# data = operational_data("find", 'select * from log')
# print(data)
 # 插入数据
# a = '908'
# b = '908'
# sql2 = "insert into user values(%s, %s)" % (a,b)
# result = operational_data("insert", sq)

# 更新数据
# newPassword = '999'
# username = '908'
# oldPassword = '908'
# sql3 = "update user set password=%s where name=%s and password=%s"%(newPassword, username, oldPassword)
# result = operational_data("update", sql3)
# print(result)