from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data import config

bot = Bot(token='7117799165:AAEpdkUvrofCYOoA0G2hoX4WfaiYA-FPN2k', parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=MemoryStorage())

