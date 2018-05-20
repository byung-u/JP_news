#!/usr/bin/env python3
import asyncio
import json
import newspaper

from datetime import datetime, timedelta
from newspaper import Article
from bs4 import BeautifulSoup
from collections import Counter
from random import choice
from requests import get, codes
from selenium import webdriver
from seleniumrequests import Chrome

USER_AGENTS = ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10.7; rv:11.0) Gecko/20100101 Firefox/11.0',
               'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:22.0) Gecko/20100 101 Firefox/22.0',
               'Mozilla/5.0 (Windows NT 6.1; rv:11.0) Gecko/20100101 Firefox/11.0',
               ('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) AppleWebKit/536.5 (KHTML, like Gecko  ) '
                'Chrome/19.0.1084.46 Safari/536.5'),
               ('Mozilla/5.0 (Windows; Windows NT 6.1) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/  19.0.1084.46'
                'Safari/536.5'), )

now = datetime.now()
now = datetime.now() - timedelta(days=2)

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
                    print('[경향신문 부동산]')
                print(li.img['alt'])
                print(li.a['href'])
                keywords = get_news_article_info(li.a['href'])
                keywords_list.extend(keywords)
                cnt += 1
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
                    print('[국민일보 부동산]')
                print(title)
                print(href)
                keywords = get_news_article_info(href)
                keywords_list.extend(keywords)
                cnt += 1


def realestate_nocut(keywords_list):
    cnt = 0
    r = request_and_get('http://www.nocutnews.co.kr/news/list?c1=203&c2=204&ltype=1')
    if r is None:
        result = '%s<br>No article.' % result
        return result
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
            print('[노컷뉴스 부동산]')
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
            print('[동아일보 부동산]')
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
                print('[매일경제 부동산]')
            print(title)
            print(href)
            cnt += 1
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
            print('[문화일보 부동산]')
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
                print('[세계일보 부동산]')
            cnt += 1
            print(title)
            print(href)
            keywords = get_news_article_info(href)
            keywords_list.extend(keywords)

def realestate_joins(keywords_list):
    cnt = 0
    r = request_and_get('http://realestate.joins.com/?cloc=joongang|section|subsection')
    if r is None:
        return
    today = '%4d.%02d.%02d' % (now.year, now.month, now.day)

    base_url = 'http://news.joins.com'
    soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
    for f in soup.find_all(match_soup_class(['bd'])):
        for li in f.find_all('li'):
            try:
                title = li.a['title']
            except KeyError:
                title = check_valid_string(' '.join(li.text.strip().split()[1:-2]))
            try:
                href = '%s%s' % (base_url, li.a['href'])
            except TypeError:
                continue
            temp = li.find('span', attrs={'class': 'date'})
            try:
                article_date = temp.text
            except AttributeError:
                continue

            if not article_date.startswith(today):
                continue
            if cnt == 0:
                print('[중앙일보 부동산]')
            cnt += 1
            print(title)
            print(href)
            # 중앙일보 not working
            # keywords = get_news_article_info(href)
            # keywords_list.extend(keywords)

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
                print('[조선일보 부동산]')
            cnt += 1
            print(title)
            print(href)
            keywords = get_news_article_info(href)
            keywords_list.extend(keywords)

def realestate_hani(keywords_list):
    r = request_and_get(' http://www.hani.co.kr/arti/economy/property/home01.html')
    if r is None:
        return

    base_url = 'http://www.hani.co.kr'
    soup = BeautifulSoup(r.content.decode('utf-8', 'replace'), 'html.parser')
    for article in soup.find_all(match_soup_class(['article-area'])):
        print(article)
        continue
        href = '%s%s' % (base_url, article.a['href'])
        article = article.text.strip().split('\n')
        title = check_valid_string(article[0])
        # print(title, href)
        keywords = get_news_article_info(href)
        keywords_list.extend(keywords)
    return

def realestate_hankyung(self,  keywords_list):
    result = '<hr class="noprint" style="width: 96ex;" align="left"/><a name="t0011" id="t0011" href="#t0011" class="invisible"> </a><font color="blue">[한국경제 부동산 뉴스]</font><br>'
    r = request_and_get('http://land.hankyung.com/')
    if r is None:
        result = '%s<br>No article.' % result
        return result

    soup = BeautifulSoup(r.content.decode('euc-kr', 'replace'), 'html.parser')
    sessions = soup.select('div > h2 > a')
    for s in sessions:
        if s['href'] == 'http://www.hankyung.com/news/kisarank/':
            continue
        href = s['href']
        title = check_valid_string(s.text)
        keywords = get_news_article_info(href)
        keywords_list.extend(keywords)
        result = '%s<br><a href="%s" target="_blank">%s</a>' % (result, href, title)
    return result

def realestate_naver(self,  keywords_list):
    result = '<hr class="noprint" style="width: 96ex;" align="left"/><a name="t0013" id="t0013" href="#t0013" class="invisible"> </a><font color="blue">[Naver 부동산 뉴스]</font><br>'
    r = request_and_get('http://land.naver.com/news/headline.nhn')
    if r is None:
        result = '%s<br>No article.' % result
        return result

    base_url = 'http://land.naver.com'
    soup = BeautifulSoup(r.text, 'html.parser')
    sessions = soup.select('div > div > div > div > div > dl > dt > a')
    for s in sessions:
        href = '%s%s' % (base_url, s['href'])
        title = check_valid_string(s.text)
        keywords = get_news_article_info(href)
        result = '%s<br><a href="%s" target="_blank">%s</a>' % (result, href, title)

    sessions = soup.select('div > ul > li > dl > dt > a')
    for s in sessions:
        if len(s.text) == 0:
            continue
        href = '%s%s' % (base_url, s['href'])
        title = check_valid_string(s.text)
        keywords = get_news_article_info(href)
        keywords_list.extend(keywords)
        result = '%s<br><a href="%s" target="_blank">%s</a>' % (result, href, title)
    return result

def realestate_nate(self,  keywords_list):
    result = '<hr class="noprint" style="width: 96ex;" align="left"/><a name="t0014" id="t0014" href="#t0014" class="invisible"> </a><font color="blue">[네이트 부동산 뉴스]</font><br>'
    url = 'http://news.nate.com/subsection?cate=eco03&mid=n0303&type=c&date=%s&page=1' % today
    r = request_and_get(url)
    if r is None:
        result = '%s<br>No article.' % result
        return result

    soup = BeautifulSoup(r.text, 'html.parser')
    for news in soup.find_all(match_soup_class(['mlt01'])):
        span = news.find('span', attrs={'class': 'tb'})
        tit = span.find('strong', attrs={'class': 'tit'})
        title = check_valid_string(tit.text)
        keywords = get_news_article_info(news.a['href'])
        keywords_list.extend(keywords)
        result = '%s<br><a href="%s" target="_blank">%s</a>' % (result, news.a['href'], title)
    return result

def realestate_daum(self,  keywords_list):
    result = '<hr class="noprint" style="width: 96ex;" align="left"/><a name="t0015" id="t0015" href="#t0015" class="invisible"> </a><font color="blue">[Daum 부동산 뉴스]</font><br>'
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
        result = '%s<br><a href="%s" target="_blank">%s</a>' % (result, href, title)
    return result

def realestate_news(self,  press, keywords_list):
    return
    #elif press == '한겨례':
    #    return self.realestate_hani( keywords_list)
    #elif press == '한국경제':
    #    return self.realestate_hankyung( keywords_list)
    #elif press == '네이버':
    #    return self.realestate_naver( keywords_list)
    #elif press == '네이트':
    #    return self.realestate_nate( keywords_list)
    #elif press == '다음':
    #    return self.realestate_daum( keywords_list)
    #else:
    #    result = '[' + press + '] No article.'
    #    return result

async def fetch(self, subject, loop,  keywords_list, category):
    if category == 'realestate':
        result = await loop.run_in_executor(None, self.realestate_news,  subject, keywords_list)

def get_keywords(self, keywords_list):
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

async def post_realestate(self, loop):
    press_list = ['경향신문', '국민일보', '노컷뉴스', '동아일보', '매일경제',
                  '문화일보', '세계신문', '중앙일보', '조선일보', '한겨례',
                  '한국경제', '한국일보', '네이버', '네이트', '다음']
    keywords_list = []
    futures = [asyncio.ensure_future(self.fetch(press, loop,  keywords_list, 'realestate')) for press in press_list]
    result = await asyncio.gather(*futures)  # 결과를 한꺼번에 가져옴

    keywords = self.get_keywords(keywords_list)
    counter = Counter(keywords)
    common_keywords = [c[0] for c in counter.most_common(5)]
    content = '''<strong>언론사 목록</strong><br>
<a href="#t0001">경향신문, </a> <a href="#t0002">국민일보, </a> <a href="#t0003">노컷뉴스, </a><br>
<a href="#t0004">동아일보, </a> <a href="#t0005">매일경제, </a> <a href="#t0006">문화일보, </a><br>
<a href="#t0007">세계신문, </a> <a href="#t0008">중앙일보, </a> <a href="#t0009">조선일보, </a><br>
<a href="#t0010">한겨례, </a> <a href="#t0011">한국경제, </a> <a href="#t0012">한국일보, </a><br>
<strong>포털사이트</strong><br>
<a href="#t0013">Naver, </a> <a href="#t0014">Nate, </a> <a href="#t0015">Daum</a><br><br>
<strong>오늘의 주요 키워드</strong><br>
%s<br>
    ''' % (', '.join(common_keywords))
    for r in result:
        content = '%s<br>%s<br><br>' % (content, r)
    title = '[%s] 국내 주요언론사 부동산 뉴스 헤드라인(ㄱ, ㄴ순)' % today
    tistory_post('scrapnpost', title, content, '765348')
    naver_post(title, content)


def main():
    keywords_list = []
    # realestate_mbn(keywords_list)
    # realestate_chosun(keywords_list)

    # realestate_gyunghyang(keywords_list)
    # realestate_kookmin(keywords_list)
    # realestate_nocut(keywords_list)
    # realestate_donga(keywords_list)
    # realestate_moonhwa(keywords_list)
    # realestate_segye(keywords_list)
    # realestate_joins(keywords_list)
    realestate_hani(keywords_list)


if __name__ == '__main__':
    main()
