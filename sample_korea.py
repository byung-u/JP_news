#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import MySQLdb
import urllib.request
import re
import os
import pandas as pd

from bs4 import BeautifulSoup
from datetime import datetime
from loc_code import LOC_CODE


# 10년치는 max 8개 (6월부터니까 다 하고나서 6월부터 다시 받도록)
# 파주시 아동동 실패남
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
            elif idx == 8:
                addr_num = info  # 지번
            elif idx == 10:
                apt_floor = info
        query = ''' INSERT INTO realestate_trade ( \
                        district, dong, apt_name, apt_built_year, \
                        apt_size, apt_floor, trade_year, \
                        trade_month, trade_day, \
                        trade_price, addr_num) \
                    VALUES ("%s", "%s", "%s", "%s", "%s", "%s",\
                            "%s", "%s", "%s", "%s", "%s") \
                    ON DUPLICATE KEY UPDATE \
                        district="%s", dong="%s", apt_name="%s", apt_built_year="%s", \
                        apt_size="%s", apt_floor="%s", trade_year="%s", \
                        trade_month="%s", trade_day="%s", \
                        trade_price="%s", addr_num="%s" ''' % (
                district, dong, apt_name,
                apt_built_year, apt_size, apt_floor,
                apt_trade_year, apt_trade_month, apt_trade_day, trade_price,
                addr_num,
                district, dong, apt_name,
                apt_built_year, apt_size, apt_floor,
                apt_trade_year, apt_trade_month, apt_trade_day, trade_price,
                addr_num)
        print(query)
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
        try:
            apt_size = float(infos[9])
        except ValueError:
            print(district, infos)
            continue
        rent_infos = infos[1:]
        for idx, info in enumerate(rent_infos):
            if idx == 0:
                apt_built_year = info
            elif idx == 1:
                apt_rent_year = info
            elif idx == 2:
                dong = info
            elif idx == 3:
                rent_price = info.strip().replace(',', '')
            elif idx == 4:
                apt_name = info
            elif idx == 5:
                apt_rent_month = info
            elif idx == 6:
                monthly_price = info.strip().replace(',', '')
            elif idx == 7:
                apt_rent_day = info
            elif idx == 8:
                apt_size = info
            elif idx == 9:
                addr_num = info  # 지번
            elif idx == 11:
                apt_floor = info
# ['   130,000', '2008', '2018', ' 무악동', '인왕산아이파크', '1', '21~31', '157.289', '60', '11110', '11']
# ['', '2007', '2018', ' 필운동', '    36,000', '신동아블루아광화문의 꿈', '7', '         0', '1~10', '108.95', '254', '11110', '8']
        query = ''' INSERT INTO realestate_rent ( \
                        district, dong, apt_name, apt_built_year, \
                        apt_size, apt_floor, rent_year, \
                        rent_month, rent_day, \
                        rent_price, monthly_price, addr_num) \
                    VALUES ("%s", "%s", "%s", "%s", "%s", "%s",\
                            "%s", "%s", "%s", "%s", "%s", "%s") \
                    ON DUPLICATE KEY UPDATE \
                        district="%s", dong="%s", apt_name="%s", apt_built_year="%s", \
                        apt_size="%s", apt_floor="%s", rent_year="%s", \
                        rent_month="%s", rent_day="%s", \
                        rent_price="%s", monthly_price="%s", \
                        addr_num="%s" ''' % (
                district, dong, apt_name,
                apt_built_year, apt_size, apt_floor,
                apt_rent_year, apt_rent_month, apt_rent_day, rent_price,
                monthly_price, addr_num,
                district, dong, apt_name,
                apt_built_year, apt_size, apt_floor,
                apt_rent_year, apt_rent_month, apt_rent_day, rent_price,
                monthly_price, addr_num)
        print(query)
        cursor.execute(query)
    conn.commit()
    return


def realstate_info(conn, cursor):
    now = datetime.now()
    for i in range(3):
        time_str = '%4d%02d' % (now.year, (now.month - 1))
        apt_trade_url = os.environ.get('DATA_APT_TRADE_URL')
        apt_rent_url = os.environ.get('DATA_APT_RENT_URL')
        data_svc_key = os.environ.get('DATA_APT_API_KEY')

        get_trade_price(data_svc_key, apt_trade_url, time_str, conn, cursor)
        get_rent_price(data_svc_key, apt_rent_url, time_str, conn, cursor)
    return


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


def realstate_merge(conn, cursor):
    copy_table(conn, cursor)
    insert_trade_price(conn, cursor)
    insert_gap_price(conn, cursor)


def copy_table(conn, cursor):
    cursor.execute('select * from realestate_rent')
    row = cursor.fetchone()
    querys = []
    while row is not None:
        query = ''' INSERT INTO realestate ( \
                        district, dong, apt_name, apt_built_year, \
                        apt_size, apt_floor, r_year, r_month,
                        r_day, rent_price, monthly_price, addr_num) \
                    VALUES ("%s", "%s", "%s", "%s", "%s", "%s",\
                            "%s", "%s", "%s", "%s", "%s", "%s") \
                    ON DUPLICATE KEY UPDATE \
                        district="%s", dong="%s", apt_name="%s", apt_built_year="%s", \
                        apt_size="%s", apt_floor="%s", r_year="%s", \
                        r_month="%s", r_day="%s", \
                        rent_price="%s", monthly_price="%s", \
                        addr_num="%s" ''' % (
                row[0], row[1], row[2], row[3],
                row[4], row[5], row[6], row[7],
                row[8], row[9], row[10], row[11],
                row[0], row[1], row[2], row[3],
                row[4], row[5], row[6], row[7],
                row[8], row[9], row[10], row[11])
        querys.append(query)
        row = cursor.fetchone()

    for query in querys:
        cursor.execute(query)
    conn.commit()
    return


def insert_trade_price(conn, cursor):  # 가장 중요한 부분인데 방법을 어찌 찾을까나
    cursor.execute('select * from realestate_trade')
    row = cursor.fetchone()
    querys = []
    while row is not None:
        # ('서울특별시 종로구', # ' 사직동', # '광화문풍림스페이스본(9-0)',
        # '2008', # '126.34', '14',
        # '2018', '7', '11~20',
        # '119000', '9')
        query = ''' UPDATE realestate SET trade_price="%s" \
                    WHERE district="%s" AND dong="%s" AND apt_name="%s" AND \
                    apt_built_year="%s" AND apt_size="%s" AND  apt_floor="%s" AND \
                    r_year="%s" AND r_month="%s" AND \
                    addr_num="%s" ''' % (
                row[9],
                row[0], row[1], row[2],
                row[3], row[4], row[5],
                row[6], row[7],
                row[10])
        print(query)
        querys.append(query)
        row = cursor.fetchone()

    for query in querys:
        cursor.execute(query)
    conn.commit()
    return


def insert_gap_price(conn, cursor):
    cursor.execute('select * from realestate WHERE trade_price IS NOT NULL AND monthly_price = 0')
    row = cursor.fetchone()
    querys = []
    while row is not None:
        gap_price = int(row[9]) - int(row[10])
        # 0-2 '서울특별시 종로구', ' 숭인동', '종로중흥S클래스',
        # 3-5 '2013', '17.811', '16',
        # 6-8 '2018', '7', '1~10',
        # 9-13 '13900', '12500', '0', None, '202-3')
        query = ''' UPDATE realestate SET gap_price="%d" \
                    WHERE district="%s" AND dong="%s" AND apt_name="%s" AND \
                    apt_built_year="%s" AND apt_size="%s" AND apt_floor="%s" AND \
                    r_year="%s" AND r_month="%s" AND addr_num="%s" AND monthly_price=0 ''' % (
                gap_price,
                row[0], row[1], row[2],
                row[3], row[4], row[5],
                row[6], row[7], row[13])
        querys.append(query)
        row = cursor.fetchone()

    for query in querys:
        cursor.execute(query)
    conn.commit()
    return


def realstate_write_excel(conn):
    now = datetime.now()
    filename = '/Users/byungwoo/git/JP_News/realestate_%04d%02d%02d.xlsx' % (now.year, now.month, now.day)
    rx = pd.ExcelWriter(filename)
    df_mysql = pd.read_sql('SELECT * FROM realestate WHERE trade_price IS NOT NULL AND gap_price IS NOT NULL;', con=conn)
    df_mysql.to_excel(rx, 'total', index=False)
    rx.save()
    filename = '/Users/byungwoo/git/JP_News/realestate_huge_%04d%02d%02d.xlsx' % (now.year, now.month, now.day)
    rx = pd.ExcelWriter(filename)
    df_mysql = pd.read_sql('SELECT * FROM realestate_trade;', con=conn)
    df_mysql.to_excel(rx, 'trade', index=False)
    df_mysql = pd.read_sql('SELECT * FROM realestate_rent;', con=conn)
    df_mysql.to_excel(rx, 'rent', index=False)
    rx.save()


'''
Trade
종로구
['   130,000', '2008', '2018', ' 무악동', '인왕산아이파크', '1', '21~31', '157.289', '60', '11110', '11']
['', '2007', '2018', ' 필운동', '    36,000', '신동아블루아광화문의 꿈', '7', '         0', '1~10', '108.95', '254', '11110', '8']
'''


def main():
    conn = MySQLdb.connect(user='root', password='alsrud2', db="andre")
    cursor = conn.cursor()
    # insert db
    realstate_info(conn, cursor)
    # merge db
    realstate_merge(conn, cursor)
    # write excel
    realstate_write_excel(conn)
    conn.close()


if __name__ == '__main__':
    main()
