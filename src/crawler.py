from selenium import webdriver
from datetime import date, timedelta, datetime
from bs4 import BeautifulSoup
from apscheduler.schedulers.blocking import BlockingScheduler
import pandas as pd
import os

url = 'https://www.indieartcinema.com/theater?cinemacd=000056'
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TXT_PATH = os.path.join(BASE_DIR, "texts", "movie.txt")
PICKLE_PATH = os.path.join(BASE_DIR, "df_mov.pkl")


# Extract plain text from tag list
def extract_text_from_tag(tag_list, class_name):
    result = []
    for tag in tag_list:
        text = str(tag).replace(f'<p class="{class_name}">', '').replace('</p>', '')
        result.append(text)
    return result


# Generate header based on date information
def get_date_header(date_info):
    today = date.today()
    tomorrow = today + timedelta(1)
    if '오늘' in date_info:
        return f"오늘 {today.strftime('%Y-%m-%d')}의 시간표입니다.\n\n"
    elif '내일' in date_info:
        return f"내일 {tomorrow.strftime('%Y-%m-%d')}의 시간표입니다.\n\n"
    return ""


# Save text to file
def save_to_file(text, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


# Main crawler function
def crawler():
    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(60)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    titles = extract_text_from_tag(soup.find_all('p', class_='mv_tit'), 'mv_tit')
    starts = extract_text_from_tag(soup.find_all('p', class_='stime'), 'stime')
    ends = extract_text_from_tag(soup.find_all('p', class_='etime'), 'etime')
    date_info = str(soup.find_all('strong', class_='on'))

    header = get_date_header(date_info)
    if not titles:
        text = "현재 상영 중인 영화가 없습니다."
    else:
        text = header
        for title, start, end in zip(titles, starts, ends):
            text += f"제목 : {title.center(20)}\n시작 : {start.center(20)}\n종료 : {end.center(20)}\n\n"

    save_to_file(text, TXT_PATH)

    driver.quit()


# Update poster data
def pickle_url():
    url = 'https://www.indieartcinema.com/movie'

    driver = webdriver.Chrome()
    driver.get(url)
    driver.implicitly_wait(30)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    pic_tag = soup.find_all('div', class_='img')
    tit_tag = soup.find_all('div', class_='subj')

    pic_list = [str(i)[27:110] for i in pic_tag]
    tit_list = [i.text.strip() for i in tit_tag]

    df = pd.DataFrame(data=list(zip(pic_list, tit_list)), columns=['url', 'title'])
    df.to_pickle(PICKLE_PATH)

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
