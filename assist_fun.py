import sql
import format_html
import config
from urllib import parse


# set cookie
def set_cookie(socket, cookie_value):
    print("Hello !")
    print("world!!")
    socket.send(bytes("HTTP/1.1 201 OK\r\n", "utf-8"))
    socket.send(bytes('Set-Cookie: sessionid={}\r\n\r\n'.format(cookie_value), 'utf-8'))


# analysis url, get username and password
def get_url_info(url, column1, column2):
    url = url.split('\r\n')[-1]
    print('hello!')
    params = parse.parse_qs(url)
    return params.get(column1)[0], params.get(column2)[0]


# analysis url, get cookie
def get_cookie(url):
    params = parse.parse_qs(url.split('\r\n')[-3])
    username = params.get('Cookie: sessionid')
    return username


# into menu
def post_menu(url_info, user_dict, new_socket):
    username, password = get_url_info(url_info, 'username', 'password')
    pwd = user_dict.get(username)
    if pwd:
        if pwd == password:
            print('账号密码正确, 正在登录.....')
            # set cookie
            set_cookie(new_socket, username)
            data = sql.operational_data("find", 'select id, date, consume from log where name = \'%s\'' % username)
            # conserve file
            format_html.down_load(data)
            menu_data = format_html.menu_format(config.up_menu_path, config.low_menu_path, data, username)
            new_socket.sendall(menu_data)
            new_socket.close()
        else:
            format_html.render_html(new_socket, config.login_path, '', "密码错误！")
    else:
        format_html.render_html(new_socket, config.login_path, '', "用户名不存在！")


# reset user information
def post_set(url_info, user_dict, new_socket):
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


# delete data
def get_delete(url_info, new_socket):
        log_table_id = url_info.replace('GET /delete?id=', '').split(' ')[0]
        delete_sql = 'delete from log where id = %s' % log_table_id
        sql.operational_data('delete', delete_sql)
        # into menu
        if get_cookie(url_info):
            username = get_cookie(url_info)[0]
            print(username)
            find_sql = 'select id, date, consume from log where name = \'%s\'' % username
            print(find_sql)
            data = sql.operational_data("find", find_sql)
            # conserve file
            format_html.down_load(data)
            new_socket.send(bytes('HTTP/1.1 201 OK\r\n\r\n', 'utf-8'))
            menu_data = format_html.menu_format(config.up_menu_path, config.low_menu_path, data, username)
            new_socket.sendall(menu_data)
            new_socket.close()
        else:
            format_html.render_html(new_socket, config.login_path, '', '欢迎访问本网站!')


# into insert data html
def get_insert(url_info, new_socket):
    if get_cookie(url_info):
        username = get_cookie(url_info)[0]
        print('进入新增数据页面-------')
        format_html.render_html(new_socket, config.insert_path, username, '正在新增数据...')
    else:
        format_html.render_html(new_socket, config.login_path, '', '欢迎来到本网站！')


# post insert data
def post_insert(url_info, new_socket):
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


# post register data
def post_register(url_info, new_socket):
    print('正在注册')
    born_username, born_password = get_url_info(url_info, 'born_username', 'born_password')
    if born_username and born_password:
        if sql.operational_data('find', 'select * from user where name = \'%s\'' % born_username):
            format_html.render_html(new_socket, config.register_path, '', '用户已经存在，请重新注册...')
        else:
            sql.operational_data('insert', 'insert into user(name, password)  values (\'%s\', \'%s\')' % (
                born_username, born_password))
            format_html.render_html(new_socket, config.login_path, '', '用户注册成功,请登录...')

# get given date data
def get_menu_date(url_info, new_socket):
    print('查询指定日期的数据....')
    # 获取用户名
    username = get_cookie(url_info)[0]
    # get date, selete data
    url_userinfo = url_info.replace('GET /menu?', '').split('\r\n')[0].split(' ')[0]
    params = parse.parse_qs(url_userinfo)
    startTime = params.get('startTime')[0]
    stopTime = params.get('stopTime')[0]
    find_date_sql = 'select id, date, consume from log where name = \'%s\' and date between \'%s\' and \'%s\'' % (
        username, startTime, stopTime)
    data = sql.operational_data("find", find_date_sql)
    # conserve select file
    format_html.down_load(data)
    new_socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
    menu_data = format_html.menu_format(config.up_menu_path, config.low_menu_path, data, username)
    new_socket.sendall(menu_data)
    new_socket.close()


# direct into menu
def get_menu(url_info, new_socket):
    print(' 直接访问主菜单')
    if get_cookie(url_info):
        username = get_cookie(url_info)[0]
        find_sql = 'select id, date, consume from log where name = \'%s\'' % username
        data = sql.operational_data("find", find_sql)
        # conserve select file
        format_html.down_load(data)
        new_socket.send(bytes('HTTP/1.1 201 OK\r\n\r\n', 'utf-8'))
        menu_data = format_html.menu_format(config.up_menu_path, config.low_menu_path, data, username)
        new_socket.sendall(menu_data)
        new_socket.close()
    else:
        format_html.render_html(new_socket, config.login_path, '', '欢迎来到本网站！')


# into set html
def get_set(url_info, new_socket):
    if get_cookie(url_info):
        username = get_cookie(url_info)[0]
        format_html.render_html(new_socket, config.set_path, username, '正在修改密码...')
    else:
        format_html.render_html(new_socket, config.login_path, '', '欢迎来到本网站！')
