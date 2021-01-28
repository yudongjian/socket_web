import socket
from urllib import parse
import format_html
import sql
import traceback
import json
import time
# 用户信息


# 登录界面
def login(new_socket, msg):
    new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
    login_data = format_html.login_format('./html/login.html', msg)
    new_socket.send(login_data)
    new_socket.close()



def server_clint(new_socket):
    # 获取到浏览器传来的所有数据 注意 此处数据均为二进制
    url_userinfo = new_socket.recv(1024).decode('utf-8')
    msg = '欢迎访问本网站！'
    print(url_userinfo)
    # 用户信息
    user_tuple = sql.operational_data("find", 'select name,password from user')
    user_dict = dict(user_tuple)

    if 'favicon.ico' in url_userinfo:
        new_socket.send(bytes('HTTP/1.1 404 not found\r\n\r\n', 'utf-8'))
        new_socket.close()

    # 登录 进入主菜单
    if url_userinfo.startswith('POST /menu'):
        url_userinfo = url_userinfo.split('\r\n')[-1]
        params = parse.parse_qs(url_userinfo)

        username = params.get('username')[0]
        password = params.get('password')[0]

        # 登录进入主菜单查询数据界面
        pwd = user_dict.get(username)
        if pwd:
            if pwd == password:
                print('账号密码正确, 正在登录.....')
                new_socket.send(bytes("HTTP/1.1 201 OK\r\n", "utf-8"))
                new_socket.send(bytes('Set-Cookie: sessionid={}\r\n\r\n'.format(username), 'utf-8'))
                # todo cookie
                data = sql.operational_data("find", 'select date, consume from log where name = \'%s\''%username)
                # 保存查询文件
                format_html.down_load(data)
                menu_data = format_html.menu_format('./html/menu.html', data, username)
                new_socket.sendall(menu_data)
                new_socket.close()
            else:
                msg = "密码错误！"
                login(new_socket, msg)
        else:
            msg = "用户名不存在！"
            login(new_socket, msg)
    # 直接访问主菜单
    elif url_userinfo.startswith('GET /menu'):
        print(' 直接访问主菜单')
        url_userinfo = url_userinfo.split('\r\n')[-3]
        params = parse.parse_qs(url_userinfo)
        if params.get('Cookie: sessionid'):
            username = params.get('Cookie: sessionid')[0]
            find_sql = 'select date, consume from log where name = \'%s\'' % username
            print(find_sql)
            data = sql.operational_data("find", find_sql)
            # 保存查询文件
            format_html.down_load(data)
            new_socket.send(bytes('HTTP/1.1 201 OK\r\n\r\n', 'utf-8'))
            menu_data = format_html.menu_format('./html/menu.html', data, username)
            new_socket.sendall(menu_data)
            new_socket.close()
        else:
            login(new_socket, '欢迎访问本网站')

    # 进入设置界面
    elif url_userinfo.startswith('GET /set'):
        msg = '正在修改密码...'
        url_userinfo = url_userinfo.split('\r\n')[-3]
        params = parse.parse_qs(url_userinfo)
        if params.get('Cookie: sessionid'):
            username = params.get('Cookie: sessionid')[0]
            print('个人设置-------')
            print('username', username)
            set_data = format_html.set_format('./html/set.html', msg, username)
            new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
            new_socket.send(set_data)
            new_socket.close()
        else:
            login(new_socket, '欢迎访问本网站')

    # 提交设置
    elif url_userinfo.startswith('POST /set'):
        url_userinfo = url_userinfo.split('\r\n')[-1]
        params = parse.parse_qs(url_userinfo)
        username = params.get('username')[0]
        old_password = params.get('old_password')[0]
        first_new_password = params.get('first_new_password')[0]
        second_new_password = params.get('second_new_password')[0]
        msg = '正在修改密码...'
        if old_password != user_dict.get(username):
            msg = '原密码输入错误，请重新输入......'
        elif first_new_password != second_new_password:
            msg = '两次密码不一致，请重新输入...'
        elif old_password == first_new_password:
            msg = '原密码和新密码一致，请重新输入...'
        else:
            result = sql.operational_data('update',
                                          'UPDATE user set password =\'%s\' where name = \'%s\' and password = \'%s\' ' % (first_new_password, username, old_password))
            if result:
                msg = '密码修改成功...'

            else:
                msg = '密码修改失败...'

        print('---正在进入个人设置----')
        new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
        set_data = format_html.set_format('./html/set.html', msg, username)
        new_socket.sendall(set_data)
        new_socket.close()

    #  进入下载模块
    elif url_userinfo.startswith('GET /down'):
        print('正在下载....')
        with open('./down/download.txt', "rb") as f:
            file_content = f.read()
            new_socket.send(b"HTTP/1.1 200 OK\r\n")
            new_socket.send(b"Content-Disposition: attachment\r\n\r\n")
            new_socket.sendall(file_content)
            new_socket.close()

    # 查询指定日期数据
    elif "startTime" in url_userinfo and "stopTime" in url_userinfo:
        print('查询指定日期的数据....')
        # 获取用户名
        params = parse.parse_qs(url_userinfo)
        username = params.get(' sessionid')[0].strip()
        # 获取日期
        url_userinfo = url_userinfo.replace('GET /menu?', '').split('\r\n')[0].split(' ')[0]
        print(url_userinfo)
        params = parse.parse_qs(url_userinfo)
        startTime = params.get('startTime')[0]
        stopTime = params.get('stopTime')[0]

        new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
        find_date_sql = 'select date, consume from log where name = \'%s\' and date between \'%s\' and \'%s\''%(username, startTime, stopTime)
        data = sql.operational_data("find", find_date_sql)

        # 保存查询文件
        format_html.down_load(data)

        menu_data = format_html.menu_format('./html/menu.html', data, username)
        new_socket.sendall(menu_data)
        new_socket.close()

    #    注册模块  
    elif url_userinfo.startswith('GET /register'):
        print('正在注册')
        msg = '正在注册用户...'
        new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
        register_data = format_html.register_format('./html/register.html', msg)
        new_socket.sendall(register_data)
        new_socket.close()

    elif url_userinfo.startswith('POST /register'):
        print('正在注册')
        msg = '正在注册用户...'
        url_userinfo = url_userinfo.split('\r\n')[-1]
        params = parse.parse_qs(url_userinfo)
        print('params:', params)

        # 获取账户名和密码
        born_username = params.get('born_username')[0]
        born_password = params.get('born_password')[0]
        if born_username and born_password:
            if sql.operational_data('find', 'select * from user where name = \'%s\''%born_username):
                msg = '用户已经存在，请重新注册...'
                new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
                register_data = format_html.register_format('./html/register.html', msg)

            else:
                sql.operational_data('insert', 'insert into user(name, password)  values (\'%s\', \'%s\')'%(born_username, born_password))
                msg = '用户注册成功,请登录...'
                new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
                register_data = format_html.login_format('./html/login.html', msg)
        new_socket.sendall(register_data)
        new_socket.close()

    # 登出界面
    elif url_userinfo.startswith('GET /logout'):
        new_socket.send(bytes("HTTP/1.1 201 OK\r\n", "utf-8"))
        new_socket.send(bytes('Set-Cookie: sessionid={}\r\n\r\n'.format('******'), 'utf-8'))
        login_data = format_html.login_format('./html/login.html', msg)
        new_socket.send(login_data)
        new_socket.close()

    else:
        login(new_socket, '欢迎访问本网站')


def main():
    HOST = '180.3.15.63'
    PORT = 8080
    # 1:网络协议 tcp络模型  2:释放端口   3:绑定信息 4:最大待连接数
    tcp_server_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_con.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_server_con.bind((HOST, PORT))
    tcp_server_con.listen(5)

    while True:
        print('一次连接******')
        new_socket, client_add = tcp_server_con.accept()
        try:
            server_clint(new_socket)
        except Exception as f:
            print(f)
            new_socket.close()


if __name__ == '__main__':
    main()


