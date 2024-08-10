from telegram import (
    LabeledPrice,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import ContextTypes

from buyers.models import SignedPeople
from asgiref.sync import sync_to_async
from decouple import config


PAY_TOKEN = config('PAYMENT_PROVIDER_TOKEN')

option_keyboard = [
    [InlineKeyboardButton("Stripe", callback_data='stripe')],
    [InlineKeyboardButton("Менеджер", callback_data='manager')],
]

option_privacy_policy = [
    [InlineKeyboardButton("Согласен", callback_data='agree')],
    [InlineKeyboardButton("Не согласен", callback_data='not_agree')]
]
async def privacy_policy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = InlineKeyboardMarkup(option_privacy_policy)
    file_path = '/home/baktiyar/my_django/tele_bot/privacy_policy.txt'
    try:
        with open(file_path, 'r') as fp:
            content = fp.read()
            await update.message.reply_text(text=content,
                                            reply_markup=reply_markup)
    except FileNotFoundError:
        await update.message.reply_text(text="Файл политики конфиденциальности не найден.")
    except Exception as e:
        await update.message.reply_text(text=f"Произошла ошибка: {e}")





async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    reply_markup = InlineKeyboardMarkup(option_keyboard)

    if query.message:
        await query.message.reply_text(text='Выберите способ оплаты:', reply_markup=reply_markup)


async def pay_via_stripe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user.id
    # Получаем данные о подписке
    selection_data = context.user_data.get('selection_data')

    if selection_data is None:
        await context.bot.send_message(chat_id=chat_id,
                                       text="Данные о подписке отсутствуют. Пожалуйста, выберите подписку заново.")
        return

    title = selection_data.title
    description = selection_data.description
    payload = f"{selection_data.slug}-user_id-{user}"
    currency = "KGS"
    price = int(selection_data.price)
    prices = [LabeledPrice(title, price * 100)]

    # сохраняем invoice_payload для дольнейщей оброботки
    context.user_data['invoice_payload'] = payload
    await context.bot.send_invoice(
        chat_id, title, description, payload, PAY_TOKEN, currency, prices,

    )


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query
    if query:
        expected_payload = context.user_data.get('invoice_payload')

        if expected_payload is None:
            await query.answer(ok=False, error_message="Ошибка: отсутствует payload.")
            return

        if query.invoice_payload != expected_payload:
            await query.answer(ok=False, error_message="Ошибка в плательщике.")
            return

        user_id = update.effective_user.id

        # Проверяем, есть ли у пользователя активная подписка
        try:
            await sync_to_async(SignedPeople.objects.get)(user_id=user_id, status=True)
            await query.answer(ok=False, error_message="Вы уже являетесь подписчиком. Оплата не требуется.")
            return
        except SignedPeople.DoesNotExist:
            # Подписки нет, подтверждаем платеж
            await query.answer(ok=True)





async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.successful_payment:
        chat_id = update.effective_chat.id
        selection_data = context.user_data.get('selection_data')
        data = {
            'user_id': update.effective_user.id,
            'username': update.effective_user.first_name,
            'subscription': selection_data.slug,
            'status': True
        }
        try:
            await sync_to_async(SignedPeople.objects.get)(user_id=data['user_id'])
            await context.bot.send_message(chat_id=chat_id, text="Вы уже являетесь подписчиком")
            privacy_policy(update, context)
        except SignedPeople.DoesNotExist:
            await sync_to_async(SignedPeople.objects.create)(**data)
            await update.message.reply_text('Вы теперь подписчик!')
            await privacy_policy(update, context)

    context.user_data.pop('invoice_payload')
    context.user_data.pop('selection_data')




async def pay_via_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Дорогой пользователь!Вы можете оплатить курс любым удобным "
                                  "для вас способом. После осуществления платежа, пожалуйста, "
                                  "сделайте фото квитанции и отправьте его в наш бот."
                                  "Наш менеджер проверит зачисление денег на счет и изменит статус"
                                  " вашего доступа к курсу.Для перевода денег, пожалуйста,"
                                  " используйте следующие реквизиты:"
                                  "[СЧЕТ КУДА МОЖНО ОТПРАВИТЬ ДЕНЕГ..........................]"
                                  "Если у вас возникнут вопросы, не стесняйтесь обращаться к нам!"
                                  "Спасибо!")

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):

    await update.message.reply_text(text="Спасибо за фотографии! Менеджер проверит их"
                                          " и даст ответ. Пожалуйста, укажите свой номер"
                                          " телефона или адрес электронной почты, чтобы мы могли "
                                          "сообщить вам результаты после проверки.")
    await privacy_policy(update, context)









