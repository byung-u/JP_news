#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import urllib.request
import re
import os
import sqlite3

from bs4 import BeautifulSoup
from datetime import datetime
# from define import d_code


def jp_sqlite3_init(conn, cursor):
    cursor.execute('''CREATE TABLE IF NOT EXISTS realestate (district text, dong text, apt_name text, apt_built_year text, apt_size text, apt_floor text, trade_date text, trade_price text)''')
    conn.commit()
    return


def jp_sqlite3_insert(conn, c, query):
    c.execute(query)
    conn.commit()


# 10년치는 max 8개 (6월부터니까 다 하고나서 6월부터 다시 받도록)
def realstate_trade(conn, cursor):
    d_code = {
    #      '41461': '용인처인구',
    #      '41463': '용인기흥구',
    #      '41465': '용인수지구',
    #      '41480': '파주시',
    #      '41500': '이천시',
    #      '41550': '안성시',
    #      '41570': '김포시',
    #      '41590': '화성시',
          }
    #      '41610': '광주시',
    #      '41630': '양주시',
    #      '41650': '포천시',
    #      '41670': '여주시',
    #      '41800': '연천군',
    #      '41820': '가평군',
    #      '41830': '양평군',
    #      '42110': '춘천시',
    #      '42130': '원주시',
    #      '42150': '강릉시',
    #      '42170': '동해시',
    #      '42190': '태백시',
    #      '42210': '속초시',
    #      '42230': '삼척시',
    #      '42720': '홍천군',
    #      '42730': '횡성군',
    #      '42750': '영월군',
    #      '42760': '평창군',
    #      '42770': '정선군',
    #      '42780': '철원군',
    #      '42790': '화천군',
    #      '42800': '양구군',
    #      '50110': '제주시',
    #      '50130': '서귀포시',
    #      '42810': '인제군',
    #      '42820': '고성군',
    #      '42830': '양양군',
    #      '26230': '부산진구',
    #      '26260': '동래구',
    #      '26290': '남구',
    #      '26320': '북구',
    #      '26350': '해운대구',
    #      '26380': '사하구',
    #      '26410': '금정구',
    #      '26440': '강서구',
    #      '26470': '연제구',
    #      '26500': '수영구',
    #      '26530': '사상구',
    #      '26710': '기장군',
    #      '27110': '중구',
    #      '27140': '동구',
    #      '27170': '서구',
    #      '27200': '남구',
    #      '27230': '북구',
    #      '27260': '수성구',
    #      '27290': '달서구',
    #      '27710': '달성군',
    #      '28110': '중구',
    #      '28140': '동구',
    #      '28170': '남구',
    #      '28185': '연수구',
    #      '28200': '남동구',
    #      '28237': '부평구',
    #      '28245': '계양구',
    #      '28260': '서구',
    #      '28710': '강화군',
    #      '28720': '옹진군',
    #      '29110': '동구',
    #      '29140': '서구',
    #      '29155': '남구',
    #      '29170': '북구',
    #      '29200': '광산구',
    #      '30110': '동구',
    #      '30140': '중구',
    #      '30170': '서구',
    #      '30200': '유성구',
    #      '30230': '대덕구',
    #      '31110': '중구',
    #      '31140': '남구',
    #      '31170': '동구',
    #      '31200': '북구',
    #      '31710': '울주군',
    #      '36110': '세종특별자치시',
    #      '41111': '수원장안구',
    #      '41113': '수원권선구',
    #      '41115': '수원팔달구',
    #      '41117': '수원영통구',
    #      '41131': '성남수정구',
    #      '41133': '성남중원구',
    #      '41135': '성남분당구',
    #      '41150': '의정부시',
    #      '41171': '안양만안구',
    #      '41173': '안양동안구',
    #      '41195': '부천원미구',
    #      '41197': '부천소사구',
    #      '41199': '부천오정구',
    #      '43111': '청주상당구',
    #      '43112': '청주서원구',
    #      '43113': '청주흥덕구',
    #      '43114': '청주청원구',
    #      '43130': '충주시',
    #      '43150': '제천시',
    #      '43720': '보은군',
    #      '43730': '옥천군',
    #      '43740': '영동군',
    #      '43745': '증평군',
    #      '43750': '진천군',
    #      '43760': '괴산군',
    #      '43770': '음성군',
    #      '43800': '단양군',
    #      '44131': '천안동남구',
    #      '44133': '천안서북구',
    #      '44150': '공주시',
    #      '44180': '보령시',
    #      '44200': '아산시',
    #      '44210': '서산시',
    #      '44230': '논산시',
    #      '44250': '계룡시',
    #      '44270': '당진시',
    #      '44710': '금산군',
    #      '44760': '부여군',
    #      '44770': '서천군',
    #      '44790': '청양군',
    #      '44800': '홍성군',
    #      '44810': '예산군',
    #      '44825': '태안군',
    #      '45111': '전주완산구',
    #      '45113': '전주덕진구',
    #      '45130': '군산시',
    #      '45140': '익산시',
    #      '45180': '정읍시',
    #      '45190': '남원시',
    #      '45210': '김제시',
    #      '45710': '완주군',
    #      '45720': '진안군',
    #      '45730': '무주군',
    #      '45740': '장수군',
    #      '45750': '임실군',
    #      '45770': '순창군',
    #      '45790': '고창군',
    #      '45800': '부안군',
    #      '46110': '목포시',
    #      '46130': '여수시',
    #      '46150': '순천시',
    #      '46170': '나주시',
    #      '46230': '광양시',
    #      '46710': '담양군',
    #      '46720': '곡성군',
    #      '46730': '구례군',
    #      '46770': '고흥군',
    #      '46780': '보성군',
    #      '46790': '화순군',
    #      '46800': '장흥군',
    #      '46810': '강진군',
    #      '46820': '해남군',
    #      '46830': '영암군',
    #      '46840': '무안군',
    #      '46860': '함평군',
    #      '46870': '영광군',
    #      '46880': '장성군',
    #      '46890': '완도군',
    #      '46900': '진도군',
    #      '46910': '신안군',
    #      '47111': '포항남구',
    #      '47113': '포항북구',
    #      '47130': '경주시',
    #      '47150': '김천시',
    #      '47170': '안동시',
    #      '47190': '구미시',
    #      '47210': '영주시',
    #      '47230': '영천시',
    #      '47250': '상주시',
    #      '47280': '문경시',
    #      '47290': '경산시',
    #      '47720': '군위군',
    #      '47730': '의성군',
    #      '47750': '청송군',
    #      '47760': '영양군',
    #      '47770': '영덕군',
    #      '47820': '청도군',
    #      '47830': '고령군',
    #      '47840': '성주군',
    #      '47850': '칠곡군',
    #      '47900': '예천군',
    #      '47920': '봉화군',
    #      '47930': '울진군',
    #      '47940': '울릉군',
    #      '48121': '창원의창구',
    #      '48123': '창원성산구',
    #      '48125': '창원마산합포구',
    #      '48127': '창원마산회원구',
    #      '48129': '창원진해구',
    #      '48170': '진주시',
    #      '48220': '통영시',
    #      '48240': '사천시',
    #      '48250': '김해시',
    #      '48270': '밀양시',
    #      '48310': '거제시',
    #      '48330': '양산시',
    #      '48720': '의령군',
    #      '48730': '함안군',
    #      '48740': '창녕군',
    #      '48820': '고성군',
    #      '48840': '남해군',
    #      '48850': '하동군',
    #      '48860': '산청군',
    #      '48870': '함양군',
    #      '48880': '거창군',
    #      '48890': '합천군',
    now = datetime.now()
    # time_str = '%4d%02d' % (now.year, now.month)
    time_str = '%4d%02d' % (now.year, now.month - 1)
    for i in range(0, 10):
        for j in range(1, 13):
            if i == 0:
                if j > now.month:
                    break
            time_str = '%4d%02d' % (now.year - i, j)
            apt_trade_url = os.environ.get('DATA_APT_TRADE_URL')
            data_svc_key = os.environ.get('DATA_APT_API_KEY')

            # apt_district_code

            for district_code, district in d_code.items():
                request_url = '%s?LAWD_CD=%s&DEAL_YMD=%s&serviceKey=%s' % (
                              apt_trade_url, district_code, time_str, data_svc_key)
                request_realstate_trade(request_url, district, conn, cursor)


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
        trade_date = '%s-%02d-%s' % (apt_trade_year, int(apt_trade_month), apt_trade_day)
        query = '''INSERT OR REPLACE INTO realestate VALUES
                   ("%s", "%s", "%s", "%s", "%s", "%s", "%s", "%s")''' % (
                district, dong, apt_name,
                apt_built_year, apt_size, apt_floor,
                trade_date, trade_price)
        jp_sqlite3_insert(conn, cursor, query)
    return


'''
종로구 ['   130,000', '2008', '2018', ' 무악동', '인왕산아이파크', '1', '21~31', '157.289', '60', '11110', '11']
'''
if __name__ == '__main__':
    conn = sqlite3.connect('jp_korea.db')
    cursor = conn.cursor()
    jp_sqlite3_init(conn, cursor)
    realstate_trade(conn, cursor)
    conn.close()
