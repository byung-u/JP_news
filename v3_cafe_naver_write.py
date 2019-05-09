#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import re
import json
import urllib.request
from urllib.parse import urlencode
from selenium import webdriver


def get_naver_token():
    naver_cid = os.environ.get('NAVER_CLIENT_ID')
    naver_csec = os.environ.get('NAVER_CLIENT_SECRET')
    naver_id = os.environ.get('NAVER_ID')
    naver_pw = os.environ.get('NAVER_PAW')
    naver_redirect = os.environ.get('NAVER_BLOG_REDIRECT')
    chromedriver_path = os.environ.get('CHROMEDRIVER_PATH')

    driver = webdriver.Chrome(chromedriver_path)  # driver = webdriver.PhantomJS()
    driver.implicitly_wait(3)
    driver.get('https://nid.naver.com/nidlogin.login')
    driver.find_element_by_xpath('//*[@id="label_ip_on"]').click()
    driver.find_element_by_name('id').send_keys(naver_id)
    driver.find_element_by_name('pw').send_keys(naver_pw)
    driver.find_element_by_xpath('//*[@id="label_login_chk"]').click()
    driver.find_element_by_xpath('//*[@id="frmNIDLogin"]/fieldset/input').click()
    time.sleep(40)

    state = "REWERWERTATE"
    req_url = 'https://nid.naver.com/oauth2.0/authorize?response_type=code&client_id=%s&redirect_uri=%s&state=%s' % (naver_cid, naver_redirect, state)

    driver.get(req_url)
    ##########################
    # XXX: 최초 1회 수행해서 동의 해야함
    # driver.find_element_by_xpath('//*[@id="confirm_terms"]/a[2]').click()
    ##########################
    redirect_url = driver.current_url
    print(redirect_url)
    temp = re.split('code=', redirect_url)
    code = re.split('&state=', temp[1])[0]
    driver.quit()

    url = 'https://nid.naver.com/oauth2.0/token?'
    data = 'grant_type=authorization_code' + '&client_id=' + naver_cid + '&client_secret=' + naver_csec + '&redirect_uri=' + naver_redirect + '&code=' + code + '&state=' + state

    request = urllib.request.Request(url, data=data.encode("utf-8"))
    request.add_header('X-Naver-Client-Id', naver_cid)
    request.add_header('X-Naver-Client-Secret', naver_redirect)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    token = ''
    if rescode == 200:
        response_body = response.read()
        js = json.loads(response_body.decode('utf-8'))
        token = js['access_token']
    else:
        print("Error Code:", rescode)
        return None

    if len(token) == 0:
        return None
    print(token)
    return token


def main():
    content = '''['2019-05-10'] 부동산 분양 캘린더 모음 <br>
<br><br>
🌇  닥터아파트 분양캘린더 <br>
 http://www.drapt.com/e_sale/index.htm?page_name=cal&menu_key=0 <br>
➡️ 모델하우스 오픈 <br>
 [아파트] 경기도 이천시 증포동 이천 증포3지구 대원칸타빌 2차 더테라스 <br>
 [아파트] 경기도 평택시 고덕면 고덕 파라곤 2차 <br>
 [주상복합] 세종특별자치시 어진동 어진동 세종 린스트라우스 <br>
 [아파트] 부산광역시 남구 문현동 부산 오션 파라곤 <br>
 [아파트] 경상남도 양산시 동면 사송 더샵 데시앙(B3블록) <br>
 [아파트] 경상남도 양산시 동면 사송 더샵 데시앙(B4블록) <br>
 [아파트] 경상남도 양산시 동면 사송 더샵 데시앙(C1블록) <br>
 [주상복합] 광주광역시 남구 주월동 봉선 주월 대라수 어썸브릿지 <br>
 [오피스텔] 광주광역시 남구 주월동 봉선 주월 대라수 어썸브릿지(오) <br>
➡️ 청약접수 <br>
 [오피스텔] 광주광역시 남구 주월동 봉선 주월 대라수 어썸브릿지(오) <br>
 [아파트] 경기도 하남시 학암동 위례신도시 우미린 1차 1순위 <br>
 [아파트] 충청남도 천안시 성정동 천안 청당 코오롱하늘채 1순위 <br>
 [아파트] 전라북도 군산시 조촌동 디오션시티 더샵 2순위 <br>
➡️ 당첨자발표 <br>
 [아파트] 서울특별시 강남구 일원동 디에이치 포레센트 <br>
 [아파트] 경기도 하남시 감이동 감일 에코앤 e편한세상(공공분양) <br>
 [도시형생활주택] 전라남도 여수시 웅천동 웅천 골드클래스 테라스힐(도시형) <br>
 [아파트] 전라북도 전주시 송천동2가 에코시티 데시앙 14블록 <br>
 '''
    token = get_naver_token()
    header = "Bearer " + token  # Bearer 다음에 공백 추가
    print(header)
    clubid = "29620580"
    menuid = "17"
    url = "https://openapi.naver.com/v1/cafe/" + clubid + "/menu/" + menuid + "/articles"
    subject = urllib.parse.quote("오늘의 분양 캘린더")
    content = urllib.parse.quote(content)
    data = urlencode({'subject': subject, 'content': content}).encode()
    request = urllib.request.Request(url, data=data)
    # data = "subject=" + subject + "&content=" + content
    # request = urllib.request.Request(url, data=data.encode("utf-8"))
    request.add_header("Authorization", header)
    response = urllib.request.urlopen(request)
    rescode = response.getcode()
    if rescode == 200:
        response_body = response.read()
        print(response_body.decode('utf-8'))
    else:
        print("Error Code:" + rescode)


if __name__ == '__main__':
    main()
