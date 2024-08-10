from decouple import config
from asgiref.sync import sync_to_async
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    CommandHandler, Application, ContextTypes, CallbackQueryHandler,
    PreCheckoutQueryHandler, MessageHandler, filters
)
from payment.views import (
    payment, pay_via_stripe, pay_via_manager, precheckout_callback,
    successful_payment, handle_photo
)
from course.views import agree, choice_course
from .models import SubscriptionOptions

# Кэшируем идентификаторы курсов для использования в регулярном выражении
def get_course_ids():
    return [str(i.id) for i in SubscriptionOptions.objects.all()]

course_ids_str = get_course_ids()
course_pattern = f"^(course_({'|'.join(course_ids_str)}))$"

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
    await update.message.reply_text("Выберите подписку", reply_markup=reply_markup)

async def selection_of_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    selected_option = query.data

    # Сохраняем идентификаторы сообщения и чата в контексте
    context.user_data['chat_id'] = query.message.chat_id
    context.user_data['message_id'] = query.message.message_id

    option = await sync_to_async(SubscriptionOptions.objects.get)(slug=selected_option)
    await query.edit_message_text(text=f'{option.description} - {option.price} сомов.')

    context.user_data['selection_data'] = option
    keyboard = [
        [InlineKeyboardButton('Продолжить', callback_data="continue"),
         InlineKeyboardButton('Изменить', callback_data="change")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.message.reply_text("Выберите действие:", reply_markup=reply_markup)
    
async def change_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    chat_id = context.user_data.get('chat_id')
    message_id = context.user_data.get('message_id')

    if chat_id is None or message_id is None:
        await query.message.reply_text("Данные о чате или сообщении отсутствуют.")
        return

    if query.data == "change":
        reply_markup = InlineKeyboardMarkup(option_keyboard)
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)  # Удаляем старое сообщение
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        await context.bot.send_message(chat_id=chat_id, text='Измените тип подписки:', reply_markup=reply_markup)
    elif query.data == "continue":
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)  # Удаляем старое сообщение
        await context.bot.delete_message(chat_id=query.message.chat_id, message_id=query.message.message_id)
        await payment(update, context)

    # Очистка данных после использования
    context.user_data.pop('chat_id', None)
    context.user_data.pop('message_id', None)

def main() -> None:
    application = Application.builder().token(config('TOKEN_BOT')).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(selection_of_subscriptions, pattern='^(standard|pro|vip)$'))
    application.add_handler(CallbackQueryHandler(change_subscriptions, pattern="^(change|continue)$"))
    application.add_handler(CallbackQueryHandler(pay_via_stripe, pattern="^(stripe)$"))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    application.add_handler(CallbackQueryHandler(pay_via_manager, pattern="^(manager)$"))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(CallbackQueryHandler(agree, pattern="^(agree)$"))
    application.add_handler(CallbackQueryHandler(choice_course, pattern=course_pattern))

    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
