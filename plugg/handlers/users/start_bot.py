import asyncio
import random
import time

import emoji
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import CommandStart

from aiogram.utils.exceptions import BotBlocked

from data.config import ADMINS_ID, OFFICERS
from handlers.admin.mail import send_help_message
from handlers.users.keyboards import user_btns, admin_btns
from states import Name, Admin
from loader import dp, bot
from utils.datbase import set_officerDB, db_check, getNameById, getIdByName, del_officerDB, get_users
from utils.schemas import User
from utils.sql_commands import register_user, register_ban_user

APROOVS = []
JOINS = []
BANS = {}
kb_info = InlineKeyboardMarkup(row_width=1)
kb_info.add(types.InlineKeyboardButton(
    text=emoji.emojize(':thought_balloon:') + " vape.plugg " + emoji.emojize(':dashing_away:'),
    url="https://t.me/+aVje6lH_n7U1YmQy")
)

kb_sorts = InlineKeyboardMarkup(row_width=1)
kb_sorts.add(types.InlineKeyboardButton(
    text=emoji.emojize(':red_paper_lantern:') + " Испарители",
    callback_data=f"evaporators~")
)
 kb_sorts.add(types.InlineKeyboardButton(
   text="Жидкости",
  callback_data=f"hookahs~")
 )
 kb_sorts.add(types.InlineKeyboardButton(
       text="Одноразки",
      callback_data=f"other~")
 )
user_btns = types.ReplyKeyboardMarkup(keyboard=user_btns, resize_keyboard=True)

price_list = [
    {
        "text": "Vaparesso xros",
        "price": 12
    },
    {
        "text": "Vaparesso osmall",
        "price": 11
    },
    {
        "text": "Vaparesso barr",
        "price": 11
    },
    {
        "text": "Vaparesso luxe Q",
        "price": 12
    },
    {
        "text": "Voopoo v.thru / vmate",
        "price": 15
    },
    {
        "text": "Voopoo drag nano",
        "price": 11
    },
    {
        "text": "Lost vape ursa baby / nano",
        "price": 12
    },
    {
        "text": "Pasito 1",
        "price": 8
    },
    {
        "text": "Charon baby, Battlestar, Veer",
        "price": 8
    },
    {
        "text": "Charon plus, Smoant santi, Knight 40,
        "price": 10
    },
    {
        "text": "Pasito 2, Knight 80",
        "price": 9
    },
    {
        "text": "Manto aio",
        "price": 9
    },
    {
        "text": "Jellybox nano, Jellybox xs",
        "price": 9
    },
    {
        "text": "Aegis hero, Aegis boost, Aegis boost +, Zeus nano, Zeus nano 2",
        "price": 10
    },
    {
        "text": "Drag baby, Find trio, Vinti, Vinti R, Vinti X, Pnp tank, Drag x, Drag s",
        "price": 10
    }

]


async def kbs(text, message):
    userId = message.from_user.id
    if userId in ADMINS_ID:
        await message.answer(text, reply_markup=admin_btns)
        return
    await message.answer(text, reply_markup=user_btns)


@dp.callback_query_handler(lambda call: call.data.startswith('evaporators'))
async def evaporators(call: types.CallbackQuery):
    kb_evaporators = InlineKeyboardMarkup(row_width=1)
    for eva in price_list:
        random_id = random.randint(1, 1000)
        kb_evaporators.add(
            types.InlineKeyboardButton(text=f'{eva["text"]}', callback_data=f"eva~{random_id}~{eva['price']}"))
    await call.message.answer(emoji.emojize(':red_paper_lantern:') + " Испарители:", reply_markup=kb_evaporators)


@dp.callback_query_handler(lambda call: call.data.startswith('eva'))
async def eva_pricer(call: types.CallbackQuery):
    price = call.data.split("~")[2]
    await call.message.answer(f"Цена за 1 шт. - {price}р")


@dp.callback_query_handler(lambda call: call.data.startswith('other'))
async def other(call: types.CallbackQuery):
    await call.message.answer("Другое")


@dp.callback_query_handler(lambda call: call.data.startswith('accept'))
async def accepting(call: types.CallbackQuery):
    userId = call.data.split("~")[1]
    name = call.data.split("~")[2]
    APROOVS.append(int(userId))
    register_user(int(userId), name, 'user')
    await bot.send_message(userId, "Ваш запрос принят!\nНапишите /start / Your request was accepted!\nWrite /start",
                           reply_markup=user_btns)
    await call.message.reply("Запрос принят")


@dp.callback_query_handler(lambda call: call.data.startswith('ban'))
async def accept_ban(call: types.CallbackQuery):
    userId = int(call.data.split("~")[1])
    name = call.data.split("~")[2]
    register_ban_user(userId)
    await bot.send_message(userId, "Вам дали бан / you has been banned")
    await call.message.reply("Пользователь забанен")


@dp.message_handler(text='💎 Ассортимент 💎')
async def sorts(message: types.Message):
    await message.answer(emoji.emojize(":sparkles:") + " Выберите категорию", reply_markup=kb_sorts)


@dp.message_handler(text='📘 Информация')
async def sorts(message: types.Message):
    await message.answer(emoji.emojize(":sparkles:") + " Всю основную информацию вы\nсможете найти в нашем канале",
                         reply_markup=kb_info)

@dp.message_handler(commands=['unban'])
async def handle_ban_command(msg: types.Message):
    if msg.from_user.id in OFFICERS:
        if not msg.get_args():
            return await msg.reply("Пример: /unban имя")
        try:
            username = msg.get_args()
        except (ValueError, TypeError):
            return await msg.reply("Укажи ник пользователя / write username")
        abuser_id = getIdByName(username)
        if abuser_id == 0:
            return await msg.reply("Пользователь не найден / User not found")
        BANS.pop(abuser_id)
        await bot.send_message(abuser_id, f"Вас разблокировали / you has been unbanned",
                               reply_markup=types.ReplyKeyboardRemove())
        await msg.reply(f"Пользователь {username} разблокирован")


@dp.message_handler(commands=['ban'])
async def handle_ban_command(msg: types.Message):
    if msg.from_user.id in OFFICERS:
        if "ч" not in msg.get_args():
            return await msg.reply("Пример: /ban 1ч имя")
        try:
            data = msg.get_args().split("ч ")
            username = data[1]
            ban_time = int(data[0])
            if ban_time < 1:
                return await msg.reply("Укажите один или более часов")
        except (ValueError, TypeError):
            return await msg.reply("Укажи ник пользователя / write username")
        abuser_id = getIdByName(username)
        if abuser_id == 0:
            return await msg.reply("Пользователь не найден / User not found")
        # if abuser_id in ADMINS_ID:
        # return await msg.reply("Администратора нельзя забанить! / Administrator can't be banned!")
        BANS[abuser_id] = {"perf": time.perf_counter(), "ban_time": ban_time*3600}
        register_ban_user(abuser_id)
        await bot.send_message(abuser_id, f"Вам дали бан / you has been banned",
                               reply_markup=types.ReplyKeyboardRemove())
        await msg.reply(f"Пользователь {username} заблокирован")


@dp.message_handler(CommandStart(), state='*')
async def start_bot(message: types.Message, state: FSMContext):
    if message.from_user.id in BANS:
        ban_time = int(BANS[message.from_user.id]['ban_time'])-(int(time.perf_counter()) - int(BANS[message.from_user.id]['perf']))
        if ban_time <= 0:
            BANS.pop(message.from_user.id)
            await message.answer("Бан снят!")
            await message.answer(
                emoji.emojize(":high_voltage:"),
                reply_markup=user_btns)
            return
        hours: int = 0
        minutes: int = 0
        if ban_time / 3600 > 1:
            hours = int(ban_time / 3600)
        if ban_time / 60 > 1 > hours:
            minutes = int(ban_time / 60)
        if hours > 0:
            return await message.answer(
                "Вы были забанены!\nДо разбана: " + str(hours)+ " часов")
        if minutes > 0:
            return await message.answer(
                "Вы были забанены!\nДо разбана: " + str(minutes)+ " минут")
        return await message.answer(
            "Вы были забанены!\nДо разбана: " + str(ban_time)+ " секунд")
    await message.answer(
        emoji.emojize(":high_voltage:"),
        reply_markup=user_btns)

# my id 1573373745
