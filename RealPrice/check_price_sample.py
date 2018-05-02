#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import re
import os

from bs4 import BeautifulSoup
from datetime import datetime


def realstate_trade():
    now = datetime.now()
    # time_str = '%4d%02d' % (now.year, now.month)
    time_str = '%4d%02d' % (now.year, now.month - 1)
    apt_trade_url = os.environ.get('DATA_APT_TRADE_URL')
    data_svc_key = os.environ.get('DATA_APT_API_KEY')

    apt_district_code = {
                          11110:  '종로구', 11140:  '중구', 11170:  '용산구',
                          11200:  '성동구', 11215:  '광진구', 11230:  '동대문구',
                          11260:  '중랑구', 11290:  '성북구', 11305:  '강북구',
                          11380:  '은평구', 11410:  '서대문구', 11440:  '마포구',
                          11470:  '양천구', 11500:  '강서구', 11530:  '구로구',
                          11545:  '금천구', 11560:  '영등포구', 11590:  '동작구',
                          11620:  '관악구', 11650:  '서초구', 11680:  '강남구',
                          11710:  '송파구', 11740:  '강동구', 41290:  '과천시',
                          41461:  '용인처인구', 41463:  '용인기흥구',
                          41465:  '용인수지구', 41131:  '성남수정구',
                          41133:  '성남중원구', 41135:  '성남분당구', }

    apt_district_code = {
                          11200:  '성동구',
                          }

    for district_code, district in apt_district_code.items():
        request_url = '%s?LAWD_CD=%s&DEAL_YMD=%s&serviceKey=%s' % (
                      apt_trade_url, district_code, time_str, data_svc_key)
        request_realstate_trade(request_url, district)


def request_realstate_trade(request_url, district):
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

        # try:
        #     apt_size = float(infos[8])
        # except ValueError:
        #     print(district, infos)
        #     continue

        price = int(infos[1].strip().replace(',', ''))
        ret_msg = '%s %s %s %s층(%sm²) %s만원\t\t[준공]%s년[거래]%s년%s월%s' % (
                  district, infos[4], infos[5], infos[11], infos[8],
                  price,
                  infos[2],
                  infos[3], infos[6], infos[7])
        print(ret_msg)

#        if 50.0 < apt_size < 90.0:  # 59 ~ 85
#            price = int(infos[1].strip().replace(',', ''))
#            if price > 99999:  # 10억 이상
#                ret_msg = '%s %s %s %s층(%sm²) %s만원\t\t[준공]%s년[거래]%s년%s월%s' % (
#                          district, infos[4], infos[5], infos[11], infos[8],
#                          price,
#                          infos[2],
#                          infos[3], infos[6], infos[7])
#            else:
#                ret_msg = '%s %s %s %s층(%sm²) %s만원\t\t[준공]%s년[거래]%s년%s월%s' % (
#                          district, infos[4], infos[5], infos[11], infos[8],
#                          price,
#                          infos[2],
#                          infos[3], infos[6], infos[7])
#            print(ret_msg)


if __name__ == '__main__':
    realstate_trade()
'''
         ['',
        1 '    83,000',
        2'2005'
        3, '2018'
        4, ' 상암동'
        5, '상암월드컵파크6단지'
        6, '1'
        7, '11~20'
        8, '104.32'
        9, '1689'
        10 , '11440'
        11 , '6']
'''
