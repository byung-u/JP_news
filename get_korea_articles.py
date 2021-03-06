#!/usr/bin/env python3
# import datetime
import newspaper
import os
import re

from bs4 import BeautifulSoup
from collections import Counter
from datetime import datetime
# from datetime import datetime, timedelta
from newspaper import Article
from itertools import count
from random import choice
from requests import get, codes
from selenium import webdriver

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


def get_news_article_info(url):
    article = Article(url)
    article.download()
    try:
        article.parse()
    except newspaper.article.ArticleException:
        return None
    except UnicodeEncodeError:
        return None
    article.nlp()
    return article.keywords, article.title, article.summary


def check_valid_string(text):
    text = text.strip()
    text = text.replace("'", "").replace('"', '').replace('·', ',')
    return text


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


def realestate_molit(keywords_list):
    cnt = 0
    r = request_and_get('http://www.molit.go.kr/USR/NEWS/m_71/lst.jsp')
    if r is None:
        return
    today = '%4d-%02d-%02d' % (now.year, now.month, now.day)
    soup = BeautifulSoup(r.text, 'html.parser')
    for tbody in soup.find_all('tbody'):
        for tr in tbody.find_all('tr'):
            for idx, td in enumerate(tr.find_all('td')):
                if idx == 3:
                    article_date = td.text
                    break
            try:
                tr.a['href']
            except TypeError:
                continue

            if not article_date.startswith(today):
                continue
            if cnt == 0:
                print('\n📰 국토교통부 보도자료')
            cnt += 1
            href = 'http://www.molit.go.kr/USR/NEWS/m_71/%s' % tr.a['href']
            print(tr.a.text.strip())
            print(href)
            keywords = get_news_article_info(href)
            keywords_list.extend(keywords)


def realestate_gyunghyang(keywords_list):
    cnt = 0
    r = request_and_get('http://biz.khan.co.kr/khan_art_list.html?category=realty')
    if r is None:
        return
    today = '%4d. %02d. %02d' % (now.year, now.month, now.day)

    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
    for news_list in soup.find_all(match_soup_class(['news_list'])):
        for li in news_list.find_all('li'):
            try:
                article_date = li.find('em', attrs={'class': 'letter'}).text
                if not article_date.startswith(today):
                    continue
                if cnt == 0:
                    print('\n📰 경향신문')
                cnt += 1
                title = li.find('strong', attrs={'class': 'hd_title'})
                print(title.text)
                print(title.a['href'])
                keywords = get_news_article_info(title.a['href'])
                keywords_list.extend(keywords)
            except TypeError:
                continue


def realestate_kookmin(keywords_list):
    cnt = 0
    r = request_and_get('http://news.kmib.co.kr/article/list.asp?sid1=eco')
    if r is None:
        return
    today = '%4d-%02d-%02d' % (now.year, now.month, now.day)

    base_url = 'http://news.kmib.co.kr/article'
    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
    cnt = 0
    for nws_list in soup.find_all(match_soup_class(['nws_list'])):
        for dl in nws_list.find_all('dl'):
            article_date = dl.find('dd', attrs={'class': 'date'}).text
            if not article_date.startswith(today):
                continue
            if dl.text == '등록된 기사가 없습니다.':
                return
            dt = dl.find('dt')
            href = '%s/%s' % (base_url, dt.a['href'])
            title = check_valid_string(dt.a.text)
            if (title.find('아파트') != -1 or
               title.find('국토부') != -1 or title.find('국토교통부') != -1 or
               title.find('전세') != -1 or title.find('전월세') != -1 or
               title.find('청약') != -1 or title.find('분양') != -1 or
               title.find('부동산') != -1):

                if cnt == 0:
                    print('\n📰 국민일보')
                print(title)
                print(href)
                keywords = get_news_article_info(href)
                keywords_list.extend(keywords)
                cnt += 1


def realestate_nocut(keywords_list):
    cnt = 0
    r = request_and_get('http://www.nocutnews.co.kr/news/list?c1=203&c2=204&ltype=1')
    if r is None:
        return
    today = '%4d-%02d-%02d' % (now.year, now.month, now.day)

    base_url = 'http://www.nocutnews.co.kr'
    soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
    news = soup.find(match_soup_class(['newslist']))
    for dl in news.find_all('dl'):
        dt = dl.find('dt')
        href = '%s%s' % (base_url, dt.a['href'])
        title = check_valid_string(dt.text)
        temp = (dl.find('dd', attrs={'class': 'txt'}).text).split(' ')
        article_date = ''.join(temp[-3:])
        if not article_date.startswith(today):
            continue
        if cnt == 0:
            print('\n📰 노컷뉴스')
        cnt += 1
        print(title)
        print(href)
        keywords = get_news_article_info(href)
        keywords_list.extend(keywords)
    return


def realestate_donga(keywords_list):
    cnt = 0
    r = request_and_get('http://news.donga.com/List/Economy/RE')
    if r is None:
        return
    today = '%4d%02d%02d' % (now.year, now.month, now.day)

    soup = BeautifulSoup(r.text, 'html.parser')
    for alist in soup.find_all(match_soup_class(['articleList'])):
        tit = alist.find('span', attrs={'class': 'tit'})
        title = check_valid_string(tit.text)
        temp = (alist.a['href']).split('/')
        article_date = temp[-3]
        if not article_date.startswith(today):
            continue
        if cnt == 0:
            print('\n📰 동아일보')
        print(title)
        print(alist.a['href'])
        keywords = get_news_article_info(alist.a['href'])
        keywords_list.extend(keywords)
        cnt += 1


def realestate_mbn(keywords_list):
    cnt = 0
    r = request_and_get('http://news.mk.co.kr/newsList.php?sc=30000020')
    if r is None:
        return
    today = '%4d.%02d.%02d' % (now.year, now.month, now.day)

    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
    for list_area in soup.find_all(match_soup_class(['list_area'])):
        for dl in list_area.find_all('dl'):
            dt = dl.find('dt')
            href = dt.a['href']
            title = check_valid_string(dt.text)
            article_date = dl.find('span', attrs={'class': 'date'}).text
            if not article_date.startswith(today):
                continue
            if cnt == 0:
                print('\n📰 매일경제')
            print(title)
            print(href)
            cnt += 1
            keywords = get_news_article_info(href)
            try:
                keywords_list.extend(keywords)
            except TypeError:
                continue


def realestate_yonhapnews(keywords_list):
    cnt = 0
    r = request_and_get('http://www.yonhapnews.co.kr/economy/0304000001.html')
    if r is None:
        return
    today = '%4d/%02d/%02d' % (now.year, now.month, now.day)

    soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
    for sect02 in soup.find_all(match_soup_class(['section02'])):
        for div in sect02.find_all('div'):
            href = div.a['href']
            urls = div.a['href'].split('/')
            article_date = '/'.join(urls[4:7])
            if not article_date.startswith(today):
                continue
            if cnt == 0:
                print('\n📰 연합뉴스')
            cnt += 1
            print(div.a.text)
            print(href)
            keywords = get_news_article_info(href)
            keywords_list.extend(keywords)


def realestate_cnews(keywords_list):
    base_url = 'http://www.cnews.co.kr/uhtml/read.jsp?idxno='
    today = '%4d%02d%02d' % (now.year, now.month, now.day)
    cnt = 0
    urls = ['http://www.cnews.co.kr/uhtml/autosec/S1N1_S2N12_1.html',  # 분양
            'http://www.cnews.co.kr/uhtml/autosec/S1N1_S2N13_1.html',  # 도시정비
            'http://www.cnews.co.kr/uhtml/autosec/S1N1_S2N14_1.html',  # 개발
            'http://www.cnews.co.kr/uhtml/autosec/S1N1_S2N15_1.html',  # 재태크
            'http://www.cnews.co.kr/uhtml/autosec/S1N1_S2N16_1.html',  # 부동산시장
            ]
    for url in urls:
        r = request_and_get(url)
        soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
        for sub_list in soup.find_all(match_soup_class(['sub_main_news_list_2'])):
            for li in sub_list.find_all('li'):
                title = li.find('div', {'class': 'title'})
                article_date = li.a['href'].split("'")[1]
                if not article_date.startswith(today):
                    continue
                if cnt == 0:
                    print('\n📰 건설경제')
                cnt += 1
                href = '%s%s' % (base_url, article_date)
                print(title.text)
                print(href)
                keywords = get_news_article_info(href)
                keywords_list.extend(keywords)


def realestate_sedaily(keywords_list):
    urls = ['http://www.sedaily.com/NewsList/GB01',   # 정책, 제도
            'http://www.sedaily.com/NewsList/GB02',   # 분양, 청약
            'http://www.sedaily.com/NewsList/GB03',   # 아파트, 주택
            'http://www.sedaily.com/NewsList/GB04',   # 오피스, 상가, 토지
            'http://www.sedaily.com/NewsList/GB05',   # 건설업계
            'http://www.sedaily.com/NewsList/GB06',   # 간접투자
            'http://www.sedaily.com/NewsList/GB07',   # 기획연재
            ]

    base_url = 'http://www.sedaily.com'
    today = '%4d-%02d-%02d' % (now.year, now.month, now.day)
    cnt = 0
    for url in urls:
        r = request_and_get(url)
        soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
        for news_list in soup.find_all(match_soup_class(['news_list'])):
            for li in news_list.find_all('li'):
                dt = li.find('dt')
                href = '%s%s' % (base_url, dt.a['href'])
                dd = li.find('dd')
                article_date = dd.find('span', attrs={'class': 'letter'}).text
                if not article_date.startswith(today):
                    continue
                if cnt == 0:
                    print('\n📰 서울경제')
                cnt += 1
                print(dt.text)
                print(href)
                keywords = get_news_article_info(href)
                keywords_list.extend(keywords)


def realestate_moonhwa(keywords_list):
    cnt = 0
    r = request_and_get('http://www.munhwa.com/news/section_list.html?sec=economy&class=5')
    if r is None:
        return
    today = '%4d.%02d.%02d' % (now.year, now.month, now.day)
    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
    for td in soup.find_all('td', attrs={'style': 'padding:4 0 0 3'}):
        articles = td.text.split()
        article_date = articles[-1].replace(']', '').replace('[', '')
        if not article_date.startswith(today):
            continue
        if cnt == 0:
            print('\n📰 문화일보')
        cnt += 1
        print(td.a['href'])
        print(' '.join(articles[:-1]))
        keywords = get_news_article_info(td.a['href'])
        keywords_list.extend(keywords)


def realestate_segye(keywords_list):
    cnt = 0
    r = request_and_get('http://www.segye.com/newsList/0101030700000')
    if r is None:
        return
    today = '%4d%02d%02d' % (now.year, now.month, now.day)
    base_url = 'http://www.segye.com'
    soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
    for r_txt in soup.find_all(match_soup_class(['r_txt'])):
        for dt in r_txt.find_all('dt'):
            href = '%s%s' % (base_url, dt.a['href'])
            title = dt.text
            article_date = dt.a['href'].split('/')[-1]
            if not article_date.startswith(today):
                continue
            if cnt == 0:
                print('\n📰 세계일보')
            cnt += 1
            print(title)
            print(href)
            keywords = get_news_article_info(href)
            keywords_list.extend(keywords)


def realestate_joins(keywords_list):
    cnt = 0
    r = request_and_get('http://realestate.joins.com/article/')
    if r is None:
        return
    today = '%4d.%02d.%02d' % (now.year, now.month, now.day)

    base_url = 'http://realestate.joins.com'
    soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
    for list_basic in soup.find_all(match_soup_class(['list_basic'])):
        for ul in list_basic.find_all('ul'):
            for li in ul.find_all('li'):
                title = li.find('span', attrs={'class': 'thumb'})
                try:
                    temp_date = li.find('span', attrs={'class': 'byline'})
                    temp_date = temp_date.find_all('em')
                    article_date = temp_date[1].text.split()[0]
                    if article_date != today:
                        continue
                except AttributeError:
                    continue
                try:
                    title = title.img['alt']
                except AttributeError:
                    continue
                try:
                    temp = li.a['href']
                except KeyError:
                    continue
                href = '%s%s' % (base_url, temp)
                if cnt == 0:
                    print('\n📰 중앙일보')
                cnt += 1
                print(title)
                print(href)
                keywords = get_news_article_info(href)
                keywords_list.extend(keywords)


def realestate_chosun(keywords_list):
    cnt = 0
    r = request_and_get('http://biz.chosun.com/svc/list_in/list.html?catid=4&gnb_global')
    if r is None:
        return
    today = '%4d%02d%02d' % (now.year, now.month, now.day)

    base_url = 'http://biz.chosun.com'
    soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
    for f in soup.find_all(match_soup_class(['list_vt'])):
        for li in f.find_all('li'):
            dt = li.find('dt')
            href = '%s%s' % (base_url, li.a['href'])
            title = check_valid_string(dt.a.text)
            article_date = li.a['href'].split('/')[-1]
            if not article_date.startswith(today):
                continue
            if cnt == 0:
                print('\n📰 조선일보')
            cnt += 1
            print(title)
            print(href)
            keywords = get_news_article_info(href)
            keywords_list.extend(keywords)


def realestate_hani(keywords_list):
    cnt = 0
    r = request_and_get(' http://www.hani.co.kr/arti/economy/property/home01.html')
    if r is None:
        return
    today = '%4d-%02d-%02d' % (now.year, now.month, now.day)

    base_url = 'http://www.hani.co.kr'
    soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
    for article in soup.find_all(match_soup_class(['article-area'])):
        article_date = article.find('span', attrs={'class': 'date'}).text
        href = '%s%s' % (base_url, article.a['href'])
        article = article.text.strip().split('\n')
        title = check_valid_string(article[0])
        if not article_date.startswith(today):
            continue
        if cnt == 0:
            print('\n📰 한겨례신문')
        cnt += 1
        print(title)
        print(href)
        keywords = get_news_article_info(href)
        keywords_list.extend(keywords)
    return


def realestate_hankyung(keywords_list):
    cnt = 0
    r = request_and_get('http://land.hankyung.com/')
    if r is None:
        return
    today = '%4d%02d%02d' % (now.year, now.month, now.day)
    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
    sessions = soup.select('div > h2 > a')
    for s in sessions:
        if s['href'] == 'http://www.hankyung.com/news/kisarank/':
            continue
        href = s['href']
        title = check_valid_string(s.text)
        article_date = href.split('/')[-1]
        if not article_date.startswith(today):
            continue
        if cnt == 0:
            print('\n📰 한국경제')
        cnt += 1
        print(title)
        print(href)
        keywords = get_news_article_info(href)
        keywords_list.extend(keywords)


def realestate_naver(keywords_list):
    r = request_and_get('http://land.naver.com/news/headline.nhn')
    if r is None:
        return
    print('\n📰 NAVER')

    base_url = 'http://land.naver.com'
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('div > div > div > div > div > dl > dt > a')
    for s in sessions:
        href = '%s%s' % (base_url, s['href'])
        title = check_valid_string(s.text)
        keywords = get_news_article_info(href)
        keywords_list.extend(keywords)
        print(title)
        print(href)

    sessions = soup.select('div > ul > li > dl > dt > a')
    for s in sessions:
        if len(s.text) == 0:
            continue
        href = '%s%s' % (base_url, s['href'])
        title = check_valid_string(s.text)
        print(title)
        print(href)
        keywords = get_news_article_info(href)
        keywords_list.extend(keywords)
    return


def realestate_daum(keywords_list):
    print('\n📰 DAUM')
    r = request_and_get('http://realestate.daum.net/news')
    soup = BeautifulSoup(r.text, 'html.parser')
    for f in soup.find_all(match_soup_class(['link_news'])):
        try:
            href = f['href']
        except TypeError:
            continue
        title = check_valid_string(f.text)
        keywords = get_news_article_info(href)
        keywords_list.extend(keywords)
        print(title)
        print(href)


def realestate_thebell(keywords_list):
    driver = webdriver.Chrome(chromedriver_path)
    base_url = 'https://www.thebell.co.kr/free/content'
    cnt = 0
    today = '%4d-%02d-%02d' % (now.year, now.month, now.day)
    for i in count(1):
        driver.implicitly_wait(3)
        url = 'https://www.thebell.co.kr/free/content/article.asp?page=%d&svccode=00' % i
        driver.get(url)
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        for list_box in soup.find_all(match_soup_class(['listBox'])):
            for dl in list_box.find_all('dl'):
                for idx, dd in enumerate(dl.find_all('dd')):
                    if idx == 1:
                        article_date = dd.find('span', attrs={'class': 'date'}).text
                        break
                if article_date is None:
                    continue
                if not article_date.startswith(today):
                    driver.quit()
                    return
                dt = dl.find('dt')
                title = dt.text
                if (title.find('부동산') == -1 and
                   title.find('청약') == -1 and
                   title.find('재건축') == -1 and
                   title.find('집값') == -1 and
                   title.find('신한알파리츠') == -1 and
                   title.find('아파트') == -1):
                    # ignore not realestate title
                    continue
                if cnt == 0:
                    print('\n📰 the bell')
                cnt += 1
                href = '%s/%s' % (base_url, dl.a['href'])
                print(title)
                print(href)
                keywords = get_news_article_info(href)
                keywords_list.extend(keywords)
    driver.quit()
    return


def realestate_thescoop(keywords_list):
    cnt = 0
    driver = webdriver.Chrome(chromedriver_path)
    base_url = 'http://www.thescoop.co.kr'
    url = 'http://www.thescoop.co.kr/news/articleList.html?page=1&total=221&sc_section_code=&sc_sub_section_code=S2N74&sc_serial_code=&sc_area=&sc_level=&sc_article_type=&sc_view_level=&sc_sdate=&sc_edate=&sc_serial_number=&sc_word=&view_type=sm'
    driver.implicitly_wait(3)
    driver.get(url)

    today = '%4d-%02d-%02d' % (now.year, now.month, now.day)  
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    for article_list in soup.find_all(match_soup_class(['article-list-content'])):
        for blocks in article_list.find_all(match_soup_class(['list-block'])):
            for dated in blocks.find_all(match_soup_class(['list-dated'])):
                article_date = dated.text.split('|')[2].strip()
                break  # found article date
            if not article_date.startswith(today):
                continue
            for titles in blocks.find_all(match_soup_class(['list-titles'])):
                if cnt == 0:
                    print('\n📰 the scoop')
                cnt += 1
                href = '%s%s' % (base_url, titles.a['href'])
                keywords = get_news_article_info(href)
                keywords_list.extend(keywords)
                print(titles.a.text)
                print(href)
    driver.quit()        
    return


def realestate_cak(keywords_list):
    r = request_and_get('http://www.cak.or.kr/board/boardList.do?boardId=news_builder&menuId=437#')
    soup = BeautifulSoup(r.text, 'html.parser')
    today = '%4d.%02d.%02d' % (now.year, now.month, now.day)
    for tbody in soup.find_all('tbody'):
        for tr in tbody.find_all('tr'):
            for idx, td in enumerate(tr.find_all('td')):
                if idx == 1:
                    temp = str(td.a).split('"')[3]
                    # dataView(35653); -> 35653
                    data_id = re.findall('\(.*?\d\)', temp)[0][1:-1]
                    href = 'http://www.cak.or.kr/board/boardView.do?menuId=437&cms_site_id=&sel_tab=&searchCondition=all&searchKeyword=&sidohp=&subhp=&boardId=news_builder&dataId=%s&pageIndex=1' % data_id
                    title = td.text.strip()
                    continue
                if idx == 2:
                    article_date = td.text.strip()
                    if not article_date.startswith(today):
                        continue
                    print('\n📰 대한건설협회(CAK)')
                    print(title)
                    print(href)


def get_keywords(keywords_list):
    return [val for sublist in keywords_list for val in sublist
            if len(val) > 2 and
            not val.startswith('있') and not val.startswith('것') and
            val != '것이다' and val != '한다' and
            val != '했다' and val != '사설' and
            val != '칼럼' and val != '지난해' and
            val != '한겨레' and val != '네이버' and
            val != '안된다' and val != '부동산' and
            val != '팀장칼럼' and val != '한국의' and
            val != '하지만' and
            val != '기자수첩']


def main():
    keywords_list = []
    today = '%4d-%02d-%02d' % (now.year, now.month, now.day)
    print('(JP) PC 전용')
    print([today], '부동산 기사 모음\n')

    realestate_molit(keywords_list)         # 국토교통부
    realestate_yonhapnews(keywords_list)    # 연합뉴스
    realestate_cnews(keywords_list)     # 건설경제
    realestate_sedaily(keywords_list)   # 서울경제
    realestate_chosun(keywords_list)
    realestate_hankyung(keywords_list)
    realestate_mbn(keywords_list)

    realestate_gyunghyang(keywords_list)
    realestate_kookmin(keywords_list)
    realestate_nocut(keywords_list)
    realestate_donga(keywords_list)
    realestate_moonhwa(keywords_list)
    realestate_segye(keywords_list)      # 세계일보
    realestate_joins(keywords_list)
    realestate_hani(keywords_list)
    realestate_thebell(keywords_list)    # the bell (Gateway to capital market)
    realestate_thescoop(keywords_list)   # the scoop (Special Secret Smart)

    weekday = datetime.today().weekday()
    if weekday != 5 and weekday != 6:
        realestate_naver(keywords_list)
    # realestate_daum(keywords_list)
    # realestate_cak(keywords_list)

    keywords = get_keywords(keywords_list)
    counter = Counter(keywords)
    common_keywords = [c[0] for c in counter.most_common(5)]
    print('\n\n오늘 부동산 뉴스 주요 키워드')
    print(common_keywords)


if __name__ == '__main__':
    main()
