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
    google_table=GoogleTable("creds.json", "https://docs.google.com/spreadsheets/d/1eFdCh0JD9BZNnAUTcz3HMosJFUIONj85gg8kO83Hvgc"),  )
dp = Dispatcher(bot)

@dp.message_handler(commands=['start','старт'])
async def om_message(message: types.Message):
    await bot.send_message(message.from_user.id,f"Привет {message.from_user.first_name} {message.from_user.last_name}, я бот. Начинаю оповещать группу о задачах.")

    while True:
        date=datetime.now().strftime('%d.%m.%Y')
        time=datetime.now().strftime('%H:%M')

        result: list = bot._google_table.search_task_by_time(date,time)
        if result == -1 or result==None:
            pass
        else:
          for values in result:
            task_col: str =values[0]
            executor_col: str =values[1]
            deadline_time_col: str ="Время сдачи: "+values[2] if values[2] != "" else ""
            task_type: int = values[3]
            if task_type == 1:
                message:  str = f'{executor_col}\nНеобходимо: {task_col}\n{deadline_time_col}'
            else:
                message:  str = f'{executor_col}\nНапоминаю: {task_col}\n{deadline_time_col}'

            try:
                await bot.send_message(-892844494, message)

            except Exception as send_error:
                  logger.debug(f"{message.text}: Trouble id: {message.from_user.id}")
                  return
        await asyncio.sleep(5)


if __name__ == "__main__" :
    executor.start_polling(dp,skip_updates=True)

 # try:
 #      await message_from.reply(message)
 #  except Exception as send_error:
 #      logger.debug(f"{send_error.message}: Trouble id: {user_id}")
 #      return


