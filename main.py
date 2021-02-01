import socket
from urllib import parse
import format_html
import sql
import config
import traceback
import time


# 设置cookie
def set_cookie(socket, cookie_value):
    socket.send(bytes("HTTP/1.1 201 OK\r\n", "utf-8"))
    socket.send(bytes('Set-Cookie: sessionid={}\r\n\r\n'.format(cookie_value), 'utf-8'))


# 解析url 获取信息   用户名 和 密码
def get_url_info(url, column1, column2):
    url = url.split('\r\n')[-1]
    params = parse.parse_qs(url)
    return params.get(column1)[0], params.get(column2)[0]


# 解析url 获取cookie
def get_cookie(url):
    params = parse.parse_qs(url.split('\r\n')[-3])
    username = params.get('Cookie: sessionid')
    return username


# 发送信息
def server_clint(new_socket):
    # 获取到浏览器传来的所有数据 注意 此处数据均为二进制
    url_info = new_socket.recv(1024).decode('utf-8')
    msg = '欢迎访问本网站！'
    print(url_info)
    # 用户信息
    user_tuple = sql.operational_data("find", 'select name,password from user')
    user_dict = dict(user_tuple)

    # 访问图标
    if 'favicon.ico' in url_info:
        new_socket.send(bytes('HTTP/1.1 404 not found\r\n\r\n', 'utf-8'))
        new_socket.close()

    # 登录 进入主菜单
    if url_info.startswith('POST /menu'):
        username, password = get_url_info(url_info, 'username', 'password')
        # 登录进入主菜单查询数据界面
        pwd = user_dict.get(username)
        if pwd:
            if pwd == password:
                print('账号密码正确, 正在登录.....')
                # 设置cookie
                set_cookie(new_socket, username)
                data = sql.operational_data("find", 'select id, date, consume from log where name = \'%s\'' % username)
                # 保存查询文件
                format_html.down_load(data)
                menu_data = format_html.menu_format(config.up_menu_path, config.low_menu_path, data, username)
                new_socket.sendall(menu_data)
                new_socket.close()
            else:
                format_html.render_html(new_socket, config.login_path, '', "密码错误！")
        else:
            format_html.render_html(new_socket, config.login_path, '', "用户名不存在！")

    # 查询指定日期数据
    elif url_info.startswith('GET /menu?startTime'):
        print('查询指定日期的数据....')
        # 获取用户名
        username = get_cookie(url_info)[0]
        # 获取日期  查询数据
        url_userinfo = url_info.replace('GET /menu?', '').split('\r\n')[0].split(' ')[0]
        params = parse.parse_qs(url_userinfo)
        startTime = params.get('startTime')[0]
        stopTime = params.get('stopTime')[0]
        find_date_sql = 'select id, date, consume from log where name = \'%s\' and date between \'%s\' and \'%s\'' % (
            username, startTime, stopTime)
        data = sql.operational_data("find", find_date_sql)
        # 保存查询文件
        format_html.down_load(data)
        new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
        menu_data = format_html.menu_format(config.up_menu_path, config.low_menu_path, data, username)
        new_socket.sendall(menu_data)
        new_socket.close()

    # 直接访问主菜单
    elif url_info.startswith('GET /menu'):
        print(' 直接访问主菜单')
        if get_cookie(url_info):
            username = get_cookie(url_info)[0]
            find_sql = 'select id, date, consume from log where name = \'%s\'' % username
            data = sql.operational_data("find", find_sql)
            # 保存查询文件
            format_html.down_load(data)
            new_socket.send(bytes('HTTP/1.1 201 OK\r\n\r\n', 'utf-8'))
            menu_data = format_html.menu_format(config.up_menu_path, config.low_menu_path, data, username)
            new_socket.sendall(menu_data)
            new_socket.close()
        else:
            format_html.render_html(new_socket, config.login_path, '', '欢迎来到本网站！')

    # 进入设置界面
    elif url_info.startswith('GET /set'):
        if get_cookie(url_info):
            username = get_cookie(url_info)[0]
            format_html.render_html(new_socket, config.set_path, username, '正在修改密码...')
        else:
            format_html.render_html(new_socket, config.login_path, '', '欢迎来到本网站！')

    # 提交设置
    elif url_info.startswith('POST /set'):
        if get_cookie(url_info):
            username = get_cookie(url_info)[0]
            old_password, new_password = get_url_info(url_info, 'old_password', 'new_password')
            if old_password != user_dict.get(username):
                format_html.render_html(new_socket, config.set_path, username, '原密码输入错误，请重新输入...')
            else:
                result = sql.operational_data('update',
                                              'UPDATE user set password =\'%s\' where name = \'%s\' and password = \'%s\' ' % (
                                              new_password, username, old_password))
                if result:
                    format_html.render_html(new_socket, config.set_path, username, '密码修改成功...')
                else:
                    format_html.render_html(new_socket, config.set_path, username, '密码修改失败...')
        else:
            format_html.render_html(new_socket, config.login_path, '', '欢迎来到本网站！')
    #  进入下载模块
    elif url_info.startswith('GET /down'):
        print('正在下载')
        format_html.render_down_html(new_socket, config.down_path)

    #  进入注册页面
    elif url_info.startswith('GET /register'):
        print('正在注册用户...')
        format_html.render_html(new_socket, config.register_path, '', '正在注册用户...')

    #  接受注册数据
    elif url_info.startswith('POST /register'):
        print('正在注册')
        born_username, born_password = get_url_info(url_info, 'born_username', 'born_password')
        if born_username and born_password:
            if sql.operational_data('find', 'select * from user where name = \'%s\'' % born_username):
                format_html.render_html(new_socket, config.register_path, '', '用户已经存在，请重新注册...')
            else:
                sql.operational_data('insert', 'insert into user(name, password)  values (\'%s\', \'%s\')' % (
                born_username, born_password))
                format_html.render_html(new_socket, config.login_path, '', '用户注册成功,请登录...')

    # 进入新增数据页面
    elif url_info.startswith('GET /insert'):
        if get_cookie(url_info):
            username = get_cookie(url_info)[0]
            print('进入新增数据页面-------')
            format_html.render_html(new_socket, config.insert_path, username, '正在新增数据...')
        else:
            format_html.render_html(new_socket, config.login_path, '', '欢迎来到本网站！')

    # 新增数据
    elif url_info.startswith('POST /insert'):
        date, money = get_url_info(url_info, 'date', 'money')
        if get_cookie(url_info):
            username = get_cookie(url_info)[0]
            if int(money) != 0:
                insert_sql = 'insert into log (name, date, consume) values(\'%s\',\'%s\',%s);' % (username, date, money)
                sql.operational_data('insert', insert_sql)
                format_html.render_html(new_socket, config.insert_path, username, '已导入成功...')
            else:
                format_html.render_html(new_socket, config.insert_path, username, '正在新增数据...')
        else:
            format_html.render_html(new_socket, config.login_path, '', '欢迎访问本网站!')

    # 登出界面
    elif url_info.startswith('GET /logout'):
        format_html.render_html(new_socket, config.login_path, '', '欢迎访问本网站!')

    # 删除  -->>> 进入主菜单: 在主菜单进行删除操作
    elif url_info.startswith('GET /delete'):
        log_table_id = url_info.replace('GET /delete?id=', '').split(' ')[0]
        delete_sql = 'delete from log where id = %s' % log_table_id
        sql.operational_data('delete', delete_sql)
        # 进入主菜单
        if get_cookie(url_info):
            username = get_cookie(url_info)[0]
            print(username)
            find_sql = 'select id, date, consume from log where name = \'%s\'' % username
            print(find_sql)
            data = sql.operational_data("find", find_sql)
            # 保存查询文件
            format_html.down_load(data)
            new_socket.send(bytes('HTTP/1.1 201 OK\r\n\r\n', 'utf-8'))
            menu_data = format_html.menu_format(config.up_menu_path, config.low_menu_path, data, username)
            new_socket.sendall(menu_data)
            new_socket.close()
        else:
            format_html.render_html(new_socket, config.login_path, '', msg)
            # 查询指定日期数据
    else:
        msg = '欢迎登录本网站！'
        format_html.render_html(new_socket, config.login_path, '', msg)


def main():
    # 1:网络协议 tcp络模型  2:释放端口   3:绑定信息 4:最大待连接数
    tcp_server_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server_con.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    tcp_server_con.bind((config.host, config.port))
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
