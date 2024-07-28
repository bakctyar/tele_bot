from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    CommandHandler,
    Application,
    ContextTypes,
    CallbackQueryHandler,
)
from decouple import config

# from .models import SubscriptionOptions



    
# Определение клавиатуры
option_keyboard = [
    [InlineKeyboardButton("Стандартная подписка", callback_data='standard')],
    [InlineKeyboardButton("Про", callback_data='pro')],
    [InlineKeyboardButton("VIP", callback_data='vip')],
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        f"Привет, {user.first_name}!\n\n"
        "Я бот подписок на курсы. Доступные виды подписок:\n"
        "Чтобы узнать больше о подписках, нажмите на соответствующую кнопку ниже."
    )
    reply_markup = InlineKeyboardMarkup(option_keyboard)
    await update.message.reply_text("выберите подписку", reply_markup=reply_markup)

async def selection_of_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    "обрабатывает нажатую кнопку пользователем"
    query = update.callback_query
    await query.answer()
    selected_option = query.data

    # Сохраняем идентификаторы сообщения и чата в контексте
    context.user_data['chat_id'] = query.message.chat_id
    context.user_data['message_id'] = query.message.message_id

    # option = models.SubscriptionOptions.objects.get(slug=selected_option)
    await query.edit_message_text(text=option.description)
    if selected_option == "standard":
        await query.edit_message_text(text=f"Вы выбрали подписку <<{selected_option}>> стойимость,"
                                           f" которого состовляет 1000 сом")
    if selected_option == "pro":
        await query.edit_message_text(
            text=f"Вы выбрали подписку <<{selected_option }>> стойимость,"
                 f" которого состовляет 2000 сомов и дейтвует на"
                 f" любые курсы пребритаеме вами 15% скидка")
    if selected_option == "vip":
        await query.edit_message_text(
            text=f"Вы выбрали подписку <<{selected_option}>> стойимость, "
                 f"которого состовляет 2500 сомов и дейтвует на любые "
                 f"курсы пребритаемве вами 25% скидка")

    keyboard = [
        [InlineKeyboardButton('продолжить', callback_data="continue"),
         InlineKeyboardButton('изменить', callback_data="change")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text(f"Выберите действие:", reply_markup=reply_markup)

async def change_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    'пользователь меняет свою подписку'
    query = update.callback_query
    await query.answer()

    chat_id_change_subscriptions = query.message.chat_id
    message_id_change_subscriptions = query.message.message_id

    chat_id = context.user_data.get('chat_id')
    message_id = context.user_data.get('message_id')

    if chat_id is None or message_id is None:
        await query.message.reply_text("Данные о чате или сообщении отсутствуют.")
        return

    if query.data == "change":
        reply_markup = InlineKeyboardMarkup(option_keyboard)
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)  # Удаляем старое сообщение
        await context.bot.delete_message(chat_id=chat_id_change_subscriptions, message_id=message_id_change_subscriptions)
        await context.bot.send_message(chat_id=chat_id, text='Измените тип подписки:', reply_markup=reply_markup)
    elif query.data == "continue":
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)  # Удаляем старое сообщение
        await context.bot.delete_message(chat_id=chat_id_change_subscriptions, message_id=message_id_change_subscriptions)
        await context.bot.send_message(chat_id=chat_id, text="Плати")

    # Очистка данных после использования
    context.user_data.pop('chat_id', None)
    context.user_data.pop('message_id', None)

def main() -> None:
    application = Application.builder().token(config('TOKEN_BOT')).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(selection_of_subscriptions, pattern='^(standard|pro|vip)$'))
    application.add_handler(CallbackQueryHandler(change_subscriptions, pattern="^(continue|change)$"))
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
