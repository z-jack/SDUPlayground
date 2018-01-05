# -*- coding: utf-8 -*-
import requests
import hashlib
from pyquery import PyQuery as pq
from datetime import datetime, timedelta, time, date
from icalendar import Calendar, Event, vText

TimeTable = {
    'summer': [
        time(8, 0, 0),
        time(10, 10, 0),
        time(14, 0, 0),
        time(16, 0, 0),
        time(19, 00, 0)
    ],
    'winter': [
        time(8, 0, 0),
        time(10, 10, 0),
        time(13, 30, 0),
        time(15, 30, 0),
        time(18, 30, 0)
    ]
}


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
    print("Input the first day of term (Format: Year-Month-Day)")
    year, month, day = list(map(lambda x: int(x), input().split('-')))
    fday = datetime.now()
    fday = fday.replace(year=year, month=month, day=day, hour=0, minute=0, second=0, microsecond=0)
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

    response = requests.request("POST", "http://bkjws.sdu.edu.cn/f/xk/xs/bxqkb", headers=headers)

    html = pq(response.text)
    table = html('table#ysjddDataTableId')
    # 记得改作息
    c = Calendar()
    for i, tr in enumerate(table.items('tr')):
        if not i:
            continue
        td = tr.children('td')
        name = td.eq(2).text()
        week = td.eq(8).text()
        week = list(map(lambda x: x, week.split('周上')[0].split('-')))
        day = int(td.eq(9).text())
        cls = int(td.eq(10).text())
        loc = td.eq(11).text()
        print(name, week, day, cls, loc)
        if len(week) == 1:
            week = str(week[0])
            counter = -1
            for wk in range(len(week)):
                if wk <= counter or week[wk] == '0':
                    continue
                counter = wk
                delta = timedelta(days=7 * wk) + timedelta(days=((day - fday.isoweekday()) + 7) % 7)
                nowday = fday + delta
                t = time()
                if 5 <= nowday.month < 10:
                    nowday = nowday.combine(nowday.date(), TimeTable['summer'][cls - 1])
                else:
                    nowday = nowday.combine(nowday.date(), TimeTable['winter'][cls - 1])
                total = 1
                tmpwk = wk
                while tmpwk + 1 < len(week) and week[tmpwk + 1] == '1':
                    tmpday = fday + timedelta(days=7 * (tmpwk + 1)) + timedelta(
                        days=((day - fday.isoweekday()) + 7) % 7)
                    if nowday.month < 5 <= tmpday.month or nowday.month < 10 <= tmpday.month or 5 <= tmpday.month < 10 <= tmpday.month:
                        break
                    total += 1
                    tmpwk += 1
                counter = tmpwk
                e = Event()
                e.add("summary", name)
                e.add("uid", "Event" + name + nowday.strftime("%Y%m%d%H%M%S") + "@JackZ.cn")
                e.add('location', vText(loc))
                e.add("dtstart", nowday)
                e.add("dtend", nowday + timedelta(hours=1, minutes=50))
                e.add('rrule', {'freq': 'weekly', 'interval': '1', 'count': str(total)})
                c.add_component(e)
        else:
            counter = -1
            for wk in range(int(week[0]) - 1, int(week[1])):
                if wk <= counter:
                    continue
                counter = wk
                delta = timedelta(days=7 * wk) + timedelta(days=((day - fday.isoweekday()) + 7) % 7)
                nowday = fday + delta
                t = time()
                if 5 <= nowday.month < 10:
                    nowday = nowday.combine(nowday.date(), TimeTable['summer'][cls - 1])
                else:
                    nowday = nowday.combine(nowday.date(), TimeTable['winter'][cls - 1])
                total = 1
                tmpwk = wk
                while tmpwk + 1 < int(week[1]):
                    tmpday = fday + timedelta(days=7 * (tmpwk + 1)) + timedelta(
                        days=((day - fday.isoweekday()) + 7) % 7)
                    if nowday.month < 5 <= tmpday.month or nowday.month < 10 <= tmpday.month or 5 <= tmpday.month < 10 <= tmpday.month:
                        break
                    total += 1
                    tmpwk += 1
                counter = tmpwk
                e = Event()
                e.add("summary", name)
                e.add("uid", "Event" + name + nowday.strftime("%Y%m%d%H%M%S") + "@JackZ.cn")
                e.add('location', vText(loc))
                e.add("dtstart", nowday)
                e.add("dtend", nowday + timedelta(hours=1, minutes=50))
                e.add('rrule', {'freq': 'weekly', 'interval': '1', 'count': str(total)})
                c.add_component(e)
    print(c.to_ical())
    with open('output.ics', 'wb') as f:
        f.write(c.to_ical())


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

    res = requests.request("POST", "http://bkjws.sdu.edu.cn/b/ajaxLogin", headers=headers,
                           data={'j_username': un, 'j_password': hashlib.md5(bytearray(pw.encode('utf8'))).hexdigest()})

    print(res.content)


if __name__ == '__main__':
    main()
