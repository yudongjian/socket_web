import socket
from urllib import parse
import format_html
import sql
import traceback


def server_clint(new_socket):

    # 获取到浏览器传来的所有数据 注意 此处数据均为二进制
    resquest_data = new_socket.recv(1024)
    url_userinfo = resquest_data.split()[1]
    print('截取字符串数据:', url_userinfo)

    url_userinfo = url_userinfo.decode('utf-8')
    msg = '欢迎访问本网站！'

    # 用户信息
    user_tuple = sql.operational_data("find", 'select name,password from user')
    user_dict = dict(user_tuple)

    # 判断用户和密码
    if url_userinfo.startswith('/?') and "username" in url_userinfo and "password" in url_userinfo:

        params = parse.parse_qs(url_userinfo[2:])
        # 获取账户名和密码
        username = params.get('username', [""])[0]
        password = params.get('password', [""])[0]
        flag = params.get('flag', [""])[0]

        #  todo 下载模块
        if flag == 'down':
            print('正在下载....')

        # 进入个人设置界面
        if flag == 'set':
            print('---正在进入个人设置----')
            new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
            set_data = format_html.set_format('./html/set.html', '正在修改密码...', username)
            new_socket.sendall(set_data)
            new_socket.close()

        # 进入主菜单查询数据界面
        pwd = user_dict.get(username)
        if pwd:
            if pwd == password:
                print('账号密码正确, 正在登录.....')
                new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
                data = sql.operational_data("find", 'select * from log')
                menu_data = format_html.menu_format('./html/menu.html', data, username)
                new_socket.sendall(menu_data)
                new_socket.close()
            else:
                msg = "密码错误！"
        else:
            msg = "用户名不存在！"

    # 查询指定日期数据
    if url_userinfo.startswith("/?") and "startTime" in url_userinfo and "stopTime" in url_userinfo:
        # 获取到url中的所有参数
        params = parse.parse_qs(url_userinfo[2:])
        startTime = params.get('startTime', [""])[0]
        stopTime = params.get('stopTime', [""])[0]

        new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
        data = sql.operational_data("find", 'select * from log where date between \'%s\' and \'%s\''%(startTime, stopTime))
        menu_data = format_html.menu_format('./html/menu.html', data, 'username')
        new_socket.sendall(menu_data)
        new_socket.close()

    # 更改密码
    if url_userinfo.startswith("/?") and "username" in url_userinfo and "old_password" in url_userinfo:
        # 获取到url中的所有参数
        params = parse.parse_qs(url_userinfo[2:])
        print('params:', params)

        # 获取账户名和密码
        username = params.get('username', [""])[0]
        old_password = params.get('old_password', [""])[0]
        new_password = params.get('new_password', [""])[0]
        result = sql.operational_data('update', 'UPDATE user set password =\'%s\' where name = \'%s\' and password = \'%s\' '%(new_password, username))
        if result:
            msg = '密码已修改，重新登录...'
        else:
            msg = '密码修改失败，请重新登录...'

    #   注册模块
    if url_userinfo.startswith('/register'):
        print('正在注册')
        msg = '正在注册用户...'
        url_userinfo = url_userinfo.replace('/register', '')
        params = parse.parse_qs(url_userinfo[2:])
        print('params:', params)

        # 获取账户名和密码
        born_username = params.get('born_username', [""])[0]
        born_password = params.get('born_password', [""])[0]
        print(born_password)
        print(born_username)
        if born_username and born_password:
            if sql.operational_data('find', 'select * from user where name = \'%s\''%born_username):
                msg = '用户已经存在，请重新注册...'
            else:
                sql.operational_data('insert', 'insert into user(name, password)  values (\'%s\', \'%s\')'%(born_username, born_password))
                msg = '用户注册成功...'
        new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
        register_data = format_html.register_format('./html/register.html', msg)
        new_socket.sendall(register_data)
        new_socket.close()

    # 登录界面
    new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
    login_data = format_html.login_format('./html/login.html', msg)
    new_socket.send(login_data)
    new_socket.close()


def main():
    # 1:网络协议 tcp络模型  2:释放端口   3:绑定信息 4:最大待连接数
    tcp_server_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_con.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 0)
    tcp_server_con.bind(('', 8080))
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





