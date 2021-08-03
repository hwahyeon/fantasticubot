import telepot
import pandas as pd

token = token_number
bot = telepot.Bot(token)
#bot.setWebhook()

#------------------------printer----------------------------

def printer():
    # file load
    tit_txt = open("movie.txt", 'r')
    info = tit_txt.read()
    return info

#------------------------poster---------------------------

def poster(name, id):
    df = pd.read_pickle("df_mov.pkl")
    str_expr ="title.str.contains("+"'"+str(name)+"'"+", case=False)" # False 대소문자 상관없이
    df_q = df.query(str_expr)
    try:
        res_url = df_q["url"].iloc[0]
        bot.sendPhoto(id, photo=str(res_url))
    except:
        bot.sendMessage(id, "다른 검색어를 넣어 보실래요?")

# -------------------------도움말 Markdown ---------------------
text = '''
안녕하세요? 👋 [@Fantasticubot](https://t.me/Fantasticubot)이라고 해요. 
제가 할 수 있는 일은요... ¯\\\_(ツ)\_/¯  
  
📌\[상영표] 
*상영표*라고 입력해보세요.
오늘 상영하는 영화와 시간을 알려줘요.

📌\[연락처]
*주소* 혹은 *연락처*라고 입력해보세요.
판타스틱큐브의 주소와 연락처를 알려줘요.

📌\[포스터]
*영화 제목*을 입력해보세요.
판타스틱큐브에서 상영 중인 영화의 포스터들을 보여줘요. 영화 제목의 일부만 입력해도 찾아줘요. 🤘

'''

#---------------------------텔레그램 메시지 봇----------------------------
def handle(msg):
    if msg['text'] == "/start":
        bot.sendMessage(msg['from']['id'], "안녕하세요? "+
        "독립영화전용관 판타스틱 큐브 봇이에요. /help를 입력하면 도움이 될 거예요!")
    elif msg['text'] == "상영표":
        bot.sendMessage(msg['from']['id'], printer())
    elif msg['text'] == "주소":
        bot.sendMessage(msg['from']['id'], "<경기도 부천시 길주로210, 부천시청 1층 판타스틱큐브> \n 부천시청 안에 위치하고 있어요.")
    elif msg['text'] == "연락처":
        bot.sendMessage(msg['from']['id'], "판타스틱큐브 070-7713-0596")
    elif msg['text'] == "/help":
        bot.sendMessage(msg['from']['id'], text, parse_mode = 'Markdown', disable_web_page_preview=True)
    else:
        id = msg['from']['id']
        name = msg['text']
        poster(name, id)


bot.message_loop(handle)
while True:
    pass
