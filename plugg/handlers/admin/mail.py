from asyncio import sleep

from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.utils.exceptions import BotBlocked
from data.config import ADMINS_ID, OFFICERS
from loader import dp
from states import Mail
from utils.datbase import getNameById
from utils.schemas import User
from utils.sql_commands import select_users, delete_from_base

textMailingDone = '<b> рассылка завершена!</b>\n\n'\
                    '<b> mailing completed!</b>'


async def send_help_message(message, name, text):
    for user in select_users():
        if user.name == name:
            print("has been sent")
        else:
            try:
                await dp.bot.send_message(
                    chat_id=user.user_id,
                    text=text)
                await sleep(0.2)
            except BotBlocked:
                print(f"user {user.name} block bot")
                delete_from_base(user.user_id, User)


@dp.message_handler(text='рассылка')
async def mail(message: types.Message, state: FSMContext):
    if message.from_user.id in OFFICERS:
        await state.update_data(name=getNameById(message.from_user.id))
        await message.answer(
            'отправь сообщение'
            )
        await Mail.mail.set()


@dp.message_handler(state=Mail.mail, content_types=types.ContentType.ANY)
async def mail_on(message: types.Message, state: FSMContext):
    await state.reset_state(with_data=False)
    data = await state.get_data()
    if types.ContentType.TEXT == message.content_type:
        for user in select_users():
            if user.name == data['name']:
                print("has been sent")
            else:
                try:
                    await dp.bot.send_message(
                        chat_id=user.user_id,
                        text=message.html_text
                    )
                    await sleep(0.33)
                except BotBlocked:
                    print(f"user {user.name} block bot")
                    delete_from_base(user.user_id, User)
        else:
            await message.answer(
                textMailingDone
            )

    elif types.ContentType.PHOTO == message.content_type:
        for user in select_users():
            if user.name == data['name']:
                print("has been sent")
            else:
                try:
                    await dp.bot.send_photo(
                        chat_id=user.user_id,
                        photo=message.photo[-1].file_id,
                        caption=message.html_text if message.caption else None
                    )
                    await sleep(0.33)
                except Exception:
                    pass
        else:
            await message.answer(
                textMailingDone
            )

    elif types.ContentType.VIDEO == message.content_type:
        for user in select_users():
            if user.name == data['name']:
                print("has been sent")
            else:
                try:
                    await dp.bot.send_video(
                        chat_id=user.user_id,
                        video=message.video.file_id,
                        caption=message.html_text if message.caption else None
                    )
                    await sleep(0.33)
                except Exception:
                    pass
        else:
            await message.answer(
                textMailingDone
            )

    elif types.ContentType.ANIMATION == message.content_type:
        for user in select_users():
            if user.name == data['name']:
                print("has been sent")
            else:
                try:
                    await dp.bot.send_animation(
                        chat_id=user.user_id,
                        animation=message.animation.file_id,
                        caption=message.html_text if message.caption else None
                    )
                    await sleep(0.33)
                except Exception:
                    pass
        else:
            await message.answer(
                textMailingDone
            )

    else:
        await message.answer(
            '<b>данный формат контента не поддерживается для рассылки!</b>\n\n'\
            "<b>wrong format</b>"
        )
