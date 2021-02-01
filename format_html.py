# 渲染画面


# 渲染画面: 可以渲染  login/set/register/insert/ 界面
def render_html(socket, html_path, username, msg):
    # 1 读取 2 替换 3 转码
    with open(html_path, 'r', encoding='utf-8') as f:
        html_data = f.read()
    html_data = html_data.replace('**username**', username)
    html_data = html_data.replace('**message**', msg)
    html_data = html_data.encode('utf-8')

    socket.send(bytes("HTTP/1.1 201 OK\r\n\r\n", "utf-8"))
    socket.send(html_data)
    socket.close()


# 渲染下载界面: 响应头有所区别
def render_down_html(socket, file_path):
    with open(file_path, "rb") as f:
        file_content = f.read()
        socket.send(b"HTTP/1.1 200 OK\r\n")
        socket.send(b"Content-Disposition: attachment\r\n\r\n")
        socket.sendall(file_content)
        socket.close()


# 制作下载数据文件
def down_load(data):
    with open('./down/download.txt', 'w') as f:
        f.write('日期' + '  ' + '金额\r\n')
        print(data)
        for i in data:
            f.write(str(i[1]) + '  ' + str(i[2]) + '\r\n')


# 渲染主菜单
def menu_format(up_html_path, low_html_path, data, username):
    with open(up_html_path, 'r', encoding='utf-8') as f:
        up_html_data = f.read()

    # 如果有数据
    if len(data):
        for item in data:
            up_html_data = up_html_data + ('<tr><th>' +
                                           str(item[1]) +'</th><th>'+
                                           str(item[2])+ '</th><th>'+
                                           '<a href=\"/delete?id='+str(item[0])+'\">删除</a></th></tr>')
    else:
        up_html_data = up_html_data + ('<tr><th>无数据</th></tr>')

    with open(low_html_path, 'r', encoding='utf-8') as f:
        low_html_data = f.read()

    html_data = up_html_data + low_html_data

    with open('aaa.txt', 'w') as f:
        f.write(html_data)

    html_data = html_data.replace('**username**', username)
    html_data = html_data.encode('utf-8')
    return html_data
