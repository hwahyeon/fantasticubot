from selenium import webdriver
from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
import re
import pandas as pd
import os

url = 'https://www.indieartcinema.com/theater?cinemacd=000056'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TXT_PATH = os.path.join(BASE_DIR, "texts", "movie.txt")
PICKLE_PATH = os.path.join(BASE_DIR, "df_mov.pkl")

# ---------------------------crawler----------------------------
def crawler():
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(60)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    mv_tit = soup.find_all('p', class_='mv_tit')        # 이름 가져오기
    stime = soup.find_all('p', class_='stime')          # 시작시간 가져오기
    etime = soup.find_all('p', class_='etime')          # 종료시간 가져오기
    mdate = str(soup.find_all('strong', class_='on'))   # 현재 페이지 최신날짜

    # 불용어처리 및 BS4클래스 리스트화
    list_tit = []
    list_st = []
    list_et = []

    for i in mv_tit:
        i = str(i)
        i = i.replace('<p class="mv_tit">', '')
        i = i.replace('</p>', '')
        list_tit.append(i)

    for i in stime:
        i = str(i)
        i = i.replace('<p class="stime">', '')
        i = i.replace('</p>', '')
        list_st.append(i)

    for i in etime:
        i = str(i)
        i = i.replace('<p class="etime">', '')
        i = i.replace('</p>', '')
        list_et.append(i)

    list_len = len(list_tit)

    # 날짜
    # 가져온 태그에 '오늘'이 존재하면 현재 시간 출력, '내일'이 존재하면 내일 시간 출력
    today = date.today()
    tomorrow = date.today() + timedelta(1)

    # 크롤링해온 데이터 임시 저장
    # 날짜 저장
    str_date = ''
    if '오늘' in mdate:
        str_date = str('오늘 ' + today.strftime('%Y-%m-%d') + '의 시간표입니다.'+'\n'+'\n')
    elif '내일' in mdate:
        str_date = str('내일 ' + tomorrow.strftime('%Y-%m-%d') + '의 시간표입니다.'+'\n'+'\n')

    # 제목 시작 종료 메세지 저장
    str_msg = ''
    if list_len == 0:
        str_msg = ('현재 상영 중인 영화가 없습니다.')
    else:
        for i in range(list_len):
            str_msg += ('제목 : '.center(5) + list_tit[i].center(20) +'\n'
                  +'시작 : '.center(5) + list_st[i].center(20) +'\n'
                  +'종료 : '.center(5) + list_et[i].center(20) +'\n'+'\n')

    # 저장값 txt파일로 저장
    tit_txt = open("movie.txt", 'w')
    tit_txt.write(str_date)
    tit_txt.write(str_msg)
    tit_txt.close()

    driver.quit()

#-------------------url of image to pickle----------------

def pickle_url():
    url = 'https://www.indieartcinema.com/movie'

    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(60)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    pic_tag = soup.find_all('div', class_='img')
    tit_tag = soup.find_all('div', class_='subj')

    # --------------가져온 그림, 영화 제목 url tag 처리-------------
    pic_list = []
    tit_list = []

    for i in pic_tag:
        i = str(i)
        i = i[27:110]
        pic_list.append(i)

    for i in tit_tag:
        i = str(i)
        i = re.search('">(.*)</div>', i).group(1)
        tit_list.append(i)

    # -------리스트 -> dic -> df -> pickle -----------
    df = pd.DataFrame(data = list(zip(pic_list, tit_list)), columns=['url', 'title'])
    df.to_pickle("df_mov.pkl")

    driver.quit()

# Scheduler intervals (unit: minutes, hours)
CRAWLER_INTERVAL_MINUTES = 70
PICKLE_UPDATE_HOURS = 12

# Start the job scheduler
def scheduler():
    sched = BlockingScheduler()
    sched.add_job(crawler, 'interval', minutes=CRAWLER_INTERVAL_MINUTES, next_run_time=datetime.now())
    sched.add_job(pickle_url, 'interval', hours=PICKLE_UPDATE_HOURS, next_run_time=datetime.now())
    sched.start()
