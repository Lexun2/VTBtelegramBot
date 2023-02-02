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
        # await bot.send_message(-892844494, f"{date} {time}")
        if result == -1 or result==None:
            pass
        else:
          for values in result:
            # await bot.send_message(-892844494, f"{values[0]} {values[1]} {values[2]} ")
            task_col: str =values[0]
            executor_col: str =values[1]
            deadline_time_col: str =values[2]
            task_type: int = values[3]
            print(task_type)
            if task_type == 1:
                message:  str = f'{executor_col}\nНеобходимо: {task_col}\nВремя готовности: {deadline_time_col}'
            else:
                message:  str = f'{executor_col}\nНапоминаю: {task_col}\nВремя сдачи: {deadline_time_col}'

            try:
                await bot.send_message(-892844494, message)

            except Exception as send_error:
                  logger.debug(f"{message.text}: Trouble id: {message.from_user.id}")
                  return
        await asyncio.sleep(2)




# @dp.message_handler(filters.Regexp(regexp=r"(((Р|р)асписание)(\s)(взрослые))"))
# async def schedule_adults_handler(message_from: types.Message) -> None:
#   user_id: str = str(message_from.from_id)
#   text_msg: str = message_from.md_text.strip(" @#")
#   command:str = text_msg.lower()
#   print(f"Вход: команда '{command}'")
#   try:
#     with open('res/timetable.jpg', 'rb') as photo:
#         await bot.send_photo(user_id, photo)
#   except Exception as send_error:
#     logger.debug(f"{send_error.message}: Trouble id: {user_id}")
#     return


if __name__ == "__main__" :
    executor.start_polling(dp,skip_updates=True)

 # try:
 #      await message_from.reply(message)
 #  except Exception as send_error:
 #      logger.debug(f"{send_error.message}: Trouble id: {user_id}")
 #      return


