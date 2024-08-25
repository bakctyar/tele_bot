from telegram import (
    Update,
    ForceReply
)
from telegram.ext import ContextTypes, ConversationHandler

from .models import DissatisfiedUser
from asgiref.sync import sync_to_async
import re
import os
from .models import TemporaryData

PHONE_REGEX = re.compile(r'^\d{4}[\s-]?\d{2}[\s-]?\d{2}[\s-]?\d{2}$')
EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')

# Определяем состояния

FIRST_STATE = 0

async def manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = None
    if update.message:
        chat_id = update.message.chat_id
    elif update.callback_query:
        chat_id = update.callback_query.message.chat.id

    await context.bot.send_message(chat_id=chat_id,
                                       text='Пожалуйста, опишите подробно, что именно вас '
                                       'не устраивает и какие аспекты вызывают у вас недовольство. '
                                       'Менеджер постарается помочь вам в решении возникших проблем. '
                                  )
    return FIRST_STATE

async def save_dissatisfied_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    data = {
        'user_telegram_id': user.id,
        'user_name': user.first_name,
        'question_user': text
    }
    print('handle_manger')
    await sync_to_async(DissatisfiedUser.objects.create)(**data)
    return ConversationHandler.END


async def handle_privacy_policy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    if query.data == 'not_agree':
        print('not_agree')
        a = await manager(update, context)
        print(a)



async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    last_photo = update.message.photo[-1]
    file = await last_photo.get_file()
    file_path = os.path.join('/home/baktiyar/my_django/tele_bot/media/images/', f'{file.file_unique_id}.jpg')
    await file.download_to_drive(custom_path=file_path)
    try:
        await sync_to_async(TemporaryData.objects.get)(file_unique_id=file.file_unique_id)
        await update.message.reply_text('это фото было уже отправленно')
        return
    except TemporaryData.DoesNotExist:
        obj_temporary_data = TemporaryData(file_unique_id=file.file_unique_id, user_telegram_id=f"{user.id}",
                                           user_name=f"{user.first_name}", image=file_path)
        context.user_data['obj_temporary_data'] = obj_temporary_data
        context.user_data['user_id'] = user.id

    await update.message.reply_text(text=f"Спасибо за фотографии! Менеджер проверит их"
                                          "и даст ответ. Пожалуйста, укажите свой номер"
                                          "телефона или адрес электронной почты, чтобы мы могли "
                                          "сообщить вам результаты после проверки. Номер телефона должен быт указано"
                                          f"так: 0555 55 68 45 или 0555556845 ",
                                    reply_markup=ForceReply(selective=True, input_field_placeholder="Введите...."))


async def handle_number_or_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    number_or_email = update.message.text
    obj_temporary_data = context.user_data.get('obj_temporary_data')
    user_photo_id = context.user_data.get('user_id')

    if user_id == user_photo_id:
        if PHONE_REGEX.match(number_or_email):
            obj_temporary_data.number = number_or_email
            await sync_to_async(obj_temporary_data.save)()
        elif EMAIL_REGEX.match(number_or_email):
            obj_temporary_data.email = number_or_email
            await sync_to_async(obj_temporary_data.save)()

    context.user_data.pop('obj_temporary_data', None)
    context.user_data.pop('user_id', None)
    await update.message.reply_text(text=f'{number_or_email}')




