import socket
from urllib import parse
import format_html
import sql
import config
import assist_fun
import traceback
import time


# send information
def server_clint(new_socket):
    # get data from http_head ,note data is byte
    url_info = new_socket.recv(1024).decode('utf-8')
    msg = '欢迎访问本网站！'
    print(url_info)
    # user information
    user_tuple = sql.operational_data("find", 'select name,password from user')
    user_dict = dict(user_tuple)

    # visit favicon
    if 'favicon.ico' in url_info:
        new_socket.send(bytes('HTTP/1.1 404 not found\r\n\r\n', 'utf-8'))
        new_socket.close()

    # login into menu
    if url_info.startswith('POST /menu'):
        assist_fun.post_menu(url_info,user_dict, new_socket)

    # select given date data
    elif url_info.startswith('GET /menu?startTime'):
        assist_fun.get_menu_date(url_info, new_socket)

    # direct into menu
    elif url_info.startswith('GET /menu'):
        assist_fun.get_menu(url_info, new_socket)

    # into set html
    elif url_info.startswith('GET /set'):
        assist_fun.get_set(url_info, new_socket)

    # post set
    elif url_info.startswith('POST /set'):
        assist_fun.post_set(url_info,user_dict,new_socket)

    #  into download html
    elif url_info.startswith('GET /down'):
        print('正在下载')
        format_html.render_down_html(new_socket, config.down_path)

    #  into register html
    elif url_info.startswith('GET /register'):
        print('正在注册用户...')
        format_html.render_html(new_socket, config.register_path, '', '正在注册用户...')

    # get register data
    elif url_info.startswith('POST /register'):
        assist_fun.post_register(url_info, new_socket)

    # into new add html
    elif url_info.startswith('GET /insert'):
        assist_fun.get_insert(url_info, new_socket)

    # new add data
    elif url_info.startswith('POST /insert'):
        assist_fun.post_insert(url_info, new_socket)

    # logout html
    elif url_info.startswith('GET /logout'):
        format_html.render_html(new_socket, config.login_path, '', '欢迎访问本网站!')

    # delete   -->>> into menu: delete data in menu
    elif url_info.startswith('GET /delete'):
        assist_fun.get_delete(url_info, new_socket)

    else:
        format_html.render_html(new_socket, config.login_path, '','欢迎登录本网站！')


def main():
    # 1:network protocal,tcp model
    tcp_server_con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #  2:release port
    tcp_server_con.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # bind information
    tcp_server_con.bind((config.host, config.port))
    # max link number
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
