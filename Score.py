# -*- coding: utf-8 -*-
import requests, json, re, base64, hashlib


def main():
    response = requests.request("GET", "http://bkjws.sdu.edu.cn/")
    cookie = ''
    for x in response.headers.get('Set-Cookie', '').strip().split(','):
        cookie += x.split(';')[0] + ';'
    print("Input Username")
    username = input()
    username = username.strip()
    print("Input Password")
    password = input()
    password = password.strip()
    login(username, password, cookie)
    headers = {
        'accept': "*/*",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN,zh;q=0.8",
        'connection': "keep-alive",
        'cookie': "index=1;j_username=%s;j_password=%s;%s" % (username, password, cookie),
        'cache-control': "no-cache",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
    }

    response = requests.request("POST", "http://bkjws.sdu.edu.cn/b/cj/cjcx/xs/list", headers=headers, data={
        'aoData': '[{"name":"sEcho","value":1},{"name":"iColumns","value":8},{"name":"sColumns","value":""},{"name":"iDisplayStart","value":0},{"name":"iDisplayLength","value":-1},{"name":"mDataProp_0","value":"function"},{"name":"mDataProp_1","value":"kch"},{"name":"mDataProp_2","value":"kcm"},{"name":"mDataProp_3","value":"kxh"},{"name":"mDataProp_4","value":"xf"},{"name":"mDataProp_5","value":"kssj"},{"name":"mDataProp_6","value":"kscjView"},{"name":"mDataProp_7","value":"kcsx"},{"name":"iSortingCols","value":0},{"name":"bSortable_0","value":false},{"name":"bSortable_1","value":false},{"name":"bSortable_2","value":false},{"name":"bSortable_3","value":false},{"name":"bSortable_4","value":false},{"name":"bSortable_5","value":false},{"name":"bSortable_6","value":false},{"name":"bSortable_7","value":false}]'})
    js = json.loads(response.text)
    gp = 0
    cred = 0
    if 'result' in js:
        if js['result'] == 'success':
            for x in js['object']['aaData']:
                response = requests.request("POST", "http://bkjws.sdu.edu.cn/f/cj/cjcx/xs/xspm", headers=headers, data={
                    'aoData': '', 'dataTableId_length': -1,
                    'kch_kxh_kssj': '%s_%s_%s' % (x['kch'], x['kxh'], x['kssj'])})
                s = re.split(
                    '<td>%s</td>\s*<td>(\d+)</td>\s*<td>(\d+)</td>\s*<td>(.*)</td>\s*<td>(.*)</td>' % x['kscjView'],
                    response.text)
                ap = '无排名信息'
                if len(s) > 5:
                    ap = '排名：%s/%s' % (s[2], s[1])
                    if s[3] and s[4]:
                        ap += '，最高分：%s，最低分：%s' % (s[3], s[4])
                print(x['kcm'], x['kscjView'], ap)
                sc = float(x['kscjView'].replace(
                    '优秀', '95').replace(
                    '良好', '85').replace(
                    '中等', '75').replace(
                    '不及格', '0').replace(
                    '及格', '65'))
                if sc < 60:
                    sc = 0
                cred += float(x['xf'])
                gp += sc * float(x['xf'])
        else:
            print('Error!\n', js)
        if not cred:
            print('总学分：%.1f，百分制绩点为：%.3f' % (cred, gp / cred))


def login(un, pw, ck):
    headers = {
        'accept': "*/*",
        'accept-encoding': "gzip, deflate",
        'accept-language': "zh-CN,zh;q=0.8",
        'connection': "keep-alive",
        'cookie': "index=1;%s" % ck,
        'cache-control': "no-cache",
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.62 Safari/537.36'
    }

    requests.request("POST", "http://bkjws.sdu.edu.cn/b/ajaxLogin", headers=headers,
                     data={'j_username': un, 'j_password': hashlib.md5(bytearray(pw.encode('utf8'))).hexdigest()})


if __name__ == '__main__':
    main()
