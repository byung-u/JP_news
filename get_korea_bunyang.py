#!/usr/bin/env python3
import os

from bs4 import BeautifulSoup
from datetime import datetime
# from datetime import datetime, timedelta
from random import choice
from requests import get, codes

USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
               'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
               ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko  ) '
                'Chrome/19.0.1084.46 Safari/536.5'),
               ('Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/  19.0.1084.46'
                'Safari/536.5'), )
chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')
now = datetime.now()
# now = datetime.now() - timedelta(days=1)


def match_soup_class(target, mode='class'):
    def do_match(tag):
        classes = tag.get(mode, [])
        return all(c in classes for c in target)
    return do_match


def request_and_get(url):
    try:
        r = get(url, headers={'User-Agent': choice(USER_AGENTS)})
        if r.status_code != codes.ok:
            print('[%s] request error, code=%d', url, r.status_code)
            return False
        return r
    except TypeError:
        print('[%s] connect fail', url)
        return False


def realestate_kb_bunyang():
    reserve, result = [], []
    url = 'http://nland.kbstar.com/quics?page=B046971'
    r = request_and_get(url)
    if r is None:
        return
    today = 'd%4d%02d%02d' % (now.year, now.month, now.day)
    soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
    for cal_daily in soup.find_all(match_soup_class(['cal_daily'])):
        for dl in cal_daily.find_all('dl'):
            if dl['id'] != today:
                continue
            for dd in dl.find_all('dd'):
                for li in dd.find_all('li'):
                    ret = li.find('span', attrs={'class': 'red'})
                    if ret is None:
                        ret = li.find('span', attrs={'class': 'dblue'})
                        if ret is None:
                            continue
                        msg = '- %s' % (li.text.strip()[3:])
                        result.append(msg)
                    else:
                        msg = '- %s' % (li.text.strip()[2:])
                        reserve.append(msg)
    print('\n🌇  KB 분양캘린더\n', url, '\n[접수]')
    print('\n'.join(reserve))
    print('[발표]')
    print('\n'.join(result))
    return


def realestate_dapt_bunyang():
    url = 'http://www.drapt.com/e_sale/index.htm?page_name=cal&menu_key=0'
    r = request_and_get(url)
    if r is None:
        return
    print('\n\n🌇  닥터아파트 분양캘린더\n', url)
    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
    for esale_cal_topbox in soup.find_all(match_soup_class(['esale_cal_topbox'])):
        for li in esale_cal_topbox.find_all('li'):
            if li.text == '당첨자발표':
                print('➡️ 당첨자발표')
            elif li.text == '당첨자계약':
                print('➡️ 당첨자계약')
            elif li.text == '입주자 모집공고':
                print('➡️ 입주자 모집공고')
            elif li.text == '청약접수':
                print('➡️ 청약접수')
            elif li.text == '모델하우스 오픈':
                print('➡️ 모델하우스 오픈')
            else:
                print(li.text)


def main():
    today = '%4d-%02d-%02d' % (now.year, now.month, now.day)
    print('(JP)')
    print([today], '부동산 분양 캘린더 모음\n')

    realestate_kb_bunyang()                 # KB 분양
    realestate_dapt_bunyang()               # 닥터아파트 분양


if __name__ == '__main__':
    main()
