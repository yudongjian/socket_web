import re


def login_format(html_path, msg=''):
    # 1 读取 2 替换 3 转码
    with open(html_path, 'r', encoding='utf-8') as f:
        html_data = f.read()
    html_data = html_data.format(message=msg)
    html_data = html_data.encode('utf-8')

    return html_data


def menu_format(html_path, data, username):
    with open(html_path, 'r', encoding='utf-8') as f:
        html_data = f.read()
    for item in data:
        html_data = html_data.replace('{{date}}', str(item[0]), 1)
        html_data = html_data.replace('{{consume}}', str(item[1]), 1)
    html_data = html_data.replace("{{username}}", username)
    html_data = html_data.replace("{{date}}", '')
    html_data = html_data.replace("{{consume}}", '')
    html_data = html_data.encode('utf-8')

    return html_data


def set_format(html_path, msg, username):
    with open(html_path, 'r', encoding='utf-8') as f:
        html_data = f.read()

    html_data = html_data.replace('{username}', username)
    html_data = html_data.replace('{message}', msg)

    html_data = html_data.encode('utf-8')

    return html_data


def register_format(html_path, msg):
    with open(html_path, 'r', encoding='utf-8') as f:
        html_data = f.read()

    html_data = html_data.replace("{{msg}}", msg)
    html_data = html_data.encode('utf-8')

    return html_data


def down_load(data):
    with open('./down/download.txt', 'w') as f:
        f.write('日期' + '  ' + '金额\r\n')
        for i in data:
            f.write(str(i[0]) + '  ' + str(i[1]) + '\r\n')