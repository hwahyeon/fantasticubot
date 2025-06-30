from bot import bot, handle
from crawler import scheduler

bot.message_loop(handle)
scheduler()

while True:
    pass