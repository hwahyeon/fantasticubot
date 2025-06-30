from bot import bot, handle
from crawler import schedul

bot.message_loop(handle)
schedul()

while True:
    pass