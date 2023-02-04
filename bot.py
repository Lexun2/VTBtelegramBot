from datetime import datetime
from aiogram import Bot, Dispatcher, types, executor
import asyncio
import config
from loguru import logger
from googlesheet_table import GoogleTable

logger.add(
    config.settings["LOG_FILE"],
    format="{time} {level} {message}",
    level="DEBUG",
    rotation="1 week",
    compression="zip",
)

class TelegramBot(Bot):
    def __init__(
        self,
        token,
        parse_mode,
        google_table=None,
    ):
        super().__init__(token, parse_mode=parse_mode)
        self._google_table: GoogleTable = google_table

bot = TelegramBot(
    token=config.settings["TOKEN"],
    parse_mode=types.ParseMode.HTML,
    google_table=GoogleTable(config.settings["CREDS_FILE"], config.settings["URL_GOOGLE_TABLE"]))
dp = Dispatcher(bot)

@dp.message_handler(commands=['start','старт'])
async def om_message(message: types.Message):
    msg = await bot.send_message(message.from_user.id,f"Привет {message.from_user.first_name} {message.from_user.last_name}, я бот. Начинаю оповещать группу о задачах.")

    while True:
        date=datetime.now().strftime('%d.%m.%Y')
        time=datetime.now().strftime('%H:%M')

        result: list = bot._google_table.search_task_by_time(date,time)
        if result == -1 or result==None:
            pass
        else:
          for values in result:
            row: int = values[0]
            task_col: str = values[1]
            executor_col: str = values[2]
            deadline_time_col: str ="Время сдачи: "+values[3] if values[3] != "" else ""
            task_type: int = values[4]
            if task_type == 1:
                text_message:  str = f'{executor_col}\nНеобходимо: {task_col}\n{deadline_time_col}'
            else:
                text_message:  str = f'{executor_col}\nНапоминаю: {task_col}\n{deadline_time_col}'

            try:
                msg = await bot.send_message(-892844494, text_message)
                bot._google_table.update_id_message(row, msg.message_id)

            except Exception as send_error:
                  logger.debug(f"{send_error}")
                  return
        await asyncio.sleep(5)

@dp.message_handler()
async def reply_message(message: types.Message):
    if message.reply_to_message:  # Если полученное сообщение является реплаем
       values_row = bot._google_table.find_task_by_id(message.reply_to_message.message_id)
       if values_row != -1 and message.text.lower().replace("!","").replace(".","").strip() == "готово" or \
       ("выполн" in message.text.lower().replace("!","").replace(".","").strip()    and \
        "не " not in message.text.lower().replace("!","").replace(".","").strip()       and \
        "нев" not in message.text.lower().replace("!","").replace(".","").strip()):
           row_task = values_row[0]
           execut = values_row[1]
           task = values_row[2]
           deadline = values_row[3]
           # await bot.send_message(-892844494, f"Молодцы, задача:\n{row_task},\nгде исполнитель: {execut}\nВыполнена!")
           await bot.send_message(-892844494, f"Молодец {message.from_user.first_name}\nЗадача: {task},\nвыполнена!")
           bot._google_table.update_status_task(row_task)

if __name__ == "__main__" :
    executor.start_polling(dp,skip_updates=True)

 # try:
 #      await message_from.reply(message)
 #  except Exception as send_error:
 #      logger.debug(f"{send_error.message}: Trouble id: {user_id}")
 #      return


