import socket
from urllib import parse
import format_html
import sql
import traceback


# 用户信息
user_tuple = sql.operational_data("find", 'select name,password from user')
user_dict = dict(user_tuple)
print(user_dict)


def server_clint(new_socket):
    # 获取到浏览器传来的所有数据 注意 此处数据均为二进制
    resquest_data = new_socket.recv(1024)
    url_userinfo = resquest_data.split()[1]
    print('截取字符串数据:', url_userinfo)

    url_userinfo = url_userinfo.decode('utf-8')
    msg = '欢迎访问本网站！'
    # 判断用户和密码
    if url_userinfo.startswith('/?') and "username" in url_userinfo and "password" in url_userinfo:
        print(url_userinfo)
        # 获取到url中的所有参数
        params = parse.parse_qs(url_userinfo[2:])
        print('params:', params)

        # 获取账户名和密码
        username = params.get('username', [""])[0]
        password = params.get('password', [""])[0]
        flag = params.get('flag', [""])[0]

        # 进入个人设置界面
        if flag == 'set':
            print('---正在进入个人设置----')
            new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))  # 响应头
            print('---初始化数据....')
            set_data = format_html.set_format('./html/set.html', '正在修改密码...', username)
            new_socket.sendall(set_data)
            new_socket.close()

        # 进入主菜单查询数据界面
        pwd = user_dict.get(username)
        if pwd:
            if pwd == password:
                print('账号密码正确...')
                new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))  # 响应头

                data = sql.operational_data("find", 'select * from log')
                print(data)
                menu_data = format_html.menu_format('./html/menu.html', data, username)
                new_socket.sendall(menu_data)
                new_socket.close()
            else:
                msg = "密码错误！"
        else:
            msg = "用户名不存在！"

    # 查询指定日期数据
    if url_userinfo.startswith("/?") and "startTime" in url_userinfo and "stopTime" in url_userinfo:
        print(url_userinfo)

        # 获取到url中的所有参数
        params = parse.parse_qs(url_userinfo[2:])
        print('这是1内的内容params:', params)
        startTime = params.get('startTime', [""])[0]
        stopTime = params.get('stopTime', [""])[0]
        print(stopTime)
        print(stopTime)
        new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))  # 响应头

        data = sql.operational_data("find", 'select * from log where date between \'%s\' and \'%s\''%(startTime, stopTime))
        print(data)
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
        print(username)
        print(old_password)
        print(new_password)
        result = sql.operational_data('update', 'UPDATE user set password =\'%s\' where name = \'%s\''%(new_password, username))
        print(result)
        msg = '密码已修改，重新登录...'

    #  todo 注册模块
    #  todo 下载模块

    new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))  # 响应头
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


