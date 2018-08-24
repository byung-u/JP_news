#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import MySQLdb
import urllib.request
import re
import os
import sqlite3

from bs4 import BeautifulSoup
from datetime import datetime
from loc_code import LOC_CODE


def jp_sqlite3_init(conn, cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS realestate (district text, dong text, apt_name text, apt_built_year text, apt_size text, apt_floor text, trade_date text, trade_price text)''')
    conn.commit()
    return


def jp_sqlite3_insert(conn, c, query):
    c.execute(query)
    conn.commit()


def jp_sqlite3_select(conn, c, query):
    c.execute(query)
    res = c.fetchone()
    if res is None:
        return False
    return True

# 10년치는 max 8개 (6월부터니까 다 하고나서 6월부터 다시 받도록)
# 파주시 아동동 실패남
def is_exist_trade(district, dong, apt_name,
                   apt_built_year, apt_size, apt_floor, apt_trade_year,
                   apt_trade_month, apt_trade_day, trade_price):
    query = '''SELECT * FROM realestate WHERE \
               district="%s" AND dong="%s" AND apt_name="%s" AND \
               apt_built_year="%s" AND apt_size="%s" AND apt_floor="%s" AND \
               trade_year="%s" AND trade_month="%s" AND trade_day="%s" AND
               trade_price="%s"
    ''' % (district, dong, apt_name, apt_built_year, apt_size, apt_floor,
           apt_trade_year, apt_trade_month, apt_trade_day, trade_price)
    return jp_sqlite3_select(conn, cursor, query)


def request_realstate_trade(request_url, district, conn, cursor):
    req = urllib.request.Request(request_url)
    try:
        res = urllib.request.urlopen(req)
    except UnicodeEncodeError:
        print('[OpenAPI] UnicodeEncodeError')
        return

    data = res.read().decode('utf-8')
    soup = BeautifulSoup(data, 'html.parser')
    if (soup.resultcode.string != '00'):
        print('[OpenAPI] ',  soup.resultmsg.string)
        return
    items = soup.findAll('item')
    for item in items:
        try:
            infos = re.split('<.*?>', item.text)
        except TypeError:
            continue

        try:
            apt_size = float(infos[8])
        except ValueError:
            print(district, infos)
            continue
        trade_infos = infos[1:]
        for idx, info in enumerate(trade_infos):
            if idx == 0:
                trade_price = info.strip().replace(',', '')
            elif idx == 1:
                apt_built_year = info
            elif idx == 2:
                apt_trade_year = info
            elif idx == 3:
                dong = info
            elif idx == 4:
                apt_name = info
            elif idx == 5:
                apt_trade_month = info
            elif idx == 6:
                apt_trade_day = info
            elif idx == 7:
                apt_size = info
            elif idx == 10:
                apt_floor = info
        # trade_date = '%s-%02d-%s' % (apt_trade_year, int(apt_trade_month), apt_trade_day)
        if is_exist_trade(district, dong, apt_name,
                          apt_built_year, apt_size, apt_floor, apt_trade_year,
                          apt_trade_month, apt_trade_day, trade_price) is True:
            continue
        # msg = "%s %s %s, %s/%s층 %s" % (
        #       district, dong, apt_name, apt_size, apt_floor, trade_price)
        # print(msg)
        query = ''' INSERT INTO realestate ( \
                        district, dong, apt_name, apt_built_year, \
                        apt_size, apt_floor, trade_year, \
                        trade_month, trade_day, \
                        trade_price, rent_price, monthly_rent_price) \
                    VALUES ("%s", "%s", "%s", "%s", "%s", "%s",\
                            "%s", "%s", "%s", "%s", "%s", "%s") \
                    ON DUPLICATE KEY UPDATE \
                        district="%s", dong="%s", apt_name="%s", apt_built_year="%s", \
                        apt_size="%s", apt_floor="%s", trade_year="%s", \
                        trade_month="%s", trade_day="%s", \
                        trade_price="%s", rent_price="%s", monthly_rent_price="%s"''' % (
                district, dong, apt_name,
                apt_built_year, apt_size, apt_floor,
                apt_trade_year, apt_trade_month, apt_trade_day, trade_price, "", "",
                district, dong, apt_name,
                apt_built_year, apt_size, apt_floor,
                apt_trade_year, apt_trade_month, apt_trade_day, trade_price, "", "")
        cursor.execute(query)
    conn.commit()
    return


def request_realstate_rent(request_url, district, conn, cursor):
    req = urllib.request.Request(request_url)
    try:
        res = urllib.request.urlopen(req)
    except UnicodeEncodeError:
        print('[OpenAPI] UnicodeEncodeError')
        return

    data = res.read().decode('utf-8')
    soup = BeautifulSoup(data, 'html.parser')
    if (soup.resultcode.string != '00'):
        print('[OpenAPI] ',  soup.resultmsg.string)
        return
    items = soup.findAll('item')
    for item in items:
        try:
            infos = re.split('<.*?>', item.text)
        except TypeError:
            continue
        print(infos)
        import sys
        sys.exit(1)
        try:
            apt_size = float(infos[8])
        except ValueError:
            print(district, infos)
            continue
        trade_infos = infos[1:]
        for idx, info in enumerate(trade_infos):
            if idx == 0:
                trade_price = info.strip().replace(',', '')
            elif idx == 1:
                apt_built_year = info
            elif idx == 2:
                apt_trade_year = info
            elif idx == 3:
                dong = info
            elif idx == 4:
                apt_name = info
            elif idx == 5:
                apt_trade_month = info
            elif idx == 6:
                apt_trade_day = info
            elif idx == 7:
                apt_size = info
            elif idx == 10:
                apt_floor = info
        # trade_date = '%s-%02d-%s' % (apt_trade_year, int(apt_trade_month), apt_trade_day)
        if is_exist_trade(district, dong, apt_name,
                          apt_built_year, apt_size, apt_floor, apt_trade_year,
                          apt_trade_month, apt_trade_day, trade_price) is True:
            continue
        # msg = "%s %s %s, %s/%s층 %s" % (
        #       district, dong, apt_name, apt_size, apt_floor, trade_price)
        # print(msg)
        query = ''' INSERT INTO realestate ( \
                        district, dong, apt_name, apt_built_year, \
                        apt_size, apt_floor, trade_year, \
                        trade_month, trade_day, \
                        trade_price, rent_price, monthly_rent_price) \
                    VALUES ("%s", "%s", "%s", "%s", "%s", "%s",\
                            "%s", "%s", "%s", "%s", "%s", "%s") \
                    ON DUPLICATE KEY UPDATE \
                        district="%s", dong="%s", apt_name="%s", apt_built_year="%s", \
                        apt_size="%s", apt_floor="%s", trade_year="%s", \
                        trade_month="%s", trade_day="%s", \
                        trade_price="%s", rent_price="%s", monthly_rent_price="%s"''' % (
                district, dong, apt_name,
                apt_built_year, apt_size, apt_floor,
                apt_trade_year, apt_trade_month, apt_trade_day, trade_price, "", "",
                district, dong, apt_name,
                apt_built_year, apt_size, apt_floor,
                apt_trade_year, apt_trade_month, apt_trade_day, trade_price, "", "")
        cursor.execute(query)
    conn.commit()
    return


def realstate_trade(conn, cursor):
    now = datetime.now()
    # time_str = '%4d%02d' % (now.year, now.month)
    time_str = '%4d07' % (now.year)
    apt_trade_url = os.environ.get('DATA_APT_TRADE_URL')
    apt_rent_url = os.environ.get('DATA_APT_RENT_URL')
    data_svc_key = os.environ.get('DATA_APT_API_KEY')

    get_rent_price(data_svc_key, apt_rent_url, time_str, conn, cursor)
    return
    get_trade_price(data_svc_key, apt_trade_url, time_str, conn, cursor)


def get_trade_price(data_svc_key, apt_trade_url, time_str, conn, cursor):
    for district_code, district in LOC_CODE.items():
        request_url = '%s?LAWD_CD=%s&DEAL_YMD=%s&serviceKey=%s' % (
                      apt_trade_url, district_code, time_str, data_svc_key)
        request_realstate_trade(request_url, district, conn, cursor)

def get_rent_price(data_svc_key, apt_rent_url, time_str, conn, cursor):
    for district_code, district in LOC_CODE.items():
        request_url = '%s?LAWD_CD=%s&DEAL_YMD=%s&serviceKey=%s' % (
                      apt_rent_url, district_code, time_str, data_svc_key)
        request_realstate_rent(request_url, district, conn, cursor)

'''
Trade
종로구 ['   130,000', '2008', '2018', ' 무악동', '인왕산아이파크', '1', '21~31', '157.289', '60', '11110', '11']
'''
if __name__ == '__main__':
    conn = MySQLdb.connect(user='root', db="andre")
    cursor = conn.cursor()
    realstate_trade(conn, cursor)
    db.close()
