import emoji
from aiogram import types

admin_btns = [
    [types.KeyboardButton(text="пoказать всех")]
]

user_btns = [
    [types.KeyboardButton(text=emoji.emojize(':gem_stone:')+" Ассортимент "+emoji.emojize(':gem_stone:'))],
    [types.KeyboardButton(text=emoji.emojize(':blue_book:')+" Информация")]
]

