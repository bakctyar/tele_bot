from telegram import (
    LabeledPrice,
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,

)
from telegram.ext import ContextTypes

from buyers.models import SignedPeople, OrderCourse
from asgiref.sync import sync_to_async
from decouple import config

from manager.views import manager

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
    except Exception as err:
        await update.message.reply_text(text=f"Произошла ошибка: {err}")





async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    reply_markup = InlineKeyboardMarkup(option_keyboard)
    # context.user_data['payment_message_id'] = query.message.message_id
    # context.user_data['payment_chat_id'] = query.message.chat.id

    if query.message:
        await query.message.reply_text(text='Выберите способ оплаты:', reply_markup=reply_markup)


async def pay_via_stripe(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    user = update.effective_user.id
    # Получаем данные о подписке
    selection_data = context.user_data.get('selection_data')
    name_class = selection_data.__class__.__name__
    if selection_data is None:
        await context.bot.send_message(chat_id=chat_id,
                                       text="Данные о подписке отсутствуют. Пожалуйста, выберите подписку заново.")
        return

    title = selection_data.title
    description = selection_data.description
    payload = f"{name_class}-user_id-{user}"
    currency = "KGS"

    price = int(selection_data.price)
    prices = [LabeledPrice(title, price * 100)]
    # сохраняем invoice_payload для дольнейщей оброботки
    context.user_data['invoice_payload'] = payload

    # Сохраняем идентификаторы сообщения и чата в контексте
    # await context.bot.delete_message(chat_id=context.user_data.get('payment_chat_id'),
    #                                  message_id=context.user_data.get('payment_message_id'))
    await context.bot.send_invoice(
        chat_id, title, description, payload, PAY_TOKEN, currency, prices,

    )

async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.pre_checkout_query
    if query:
        context.user_data['query'] = query
        expected_payload = context.user_data.get('invoice_payload')

        if expected_payload is None:
            await query.answer(ok=False, error_message="Ошибка: отсутствует payload.")
            return

        if query.invoice_payload != expected_payload:
            await query.answer(ok=False, error_message="Ошибка в плательщике.")
            return

        if expected_payload.startswith('SubscriptionOptions-'):
            await precheckout_people(update, context)

        if expected_payload.startswith('Course-'):
            await precheckout_course(update, context)


async def precheckout_people(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = context.user_data.get('query')
    user_id = update.effective_user.id
    # Проверяем, есть ли у пользователя активная подписка
    try:
        await sync_to_async(SignedPeople.objects.get)(user_id=user_id, status=True)
        await query.answer(ok=False, error_message="Вы уже являетесь подписчиком. Оплата не требуется.")
        return
    except SignedPeople.DoesNotExist:
        # Подписки нет, подтверждаем платеж
        await query.answer(ok=True)


async def precheckout_course(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    query = context.user_data.get('query')
    course = context.user_data.get('selection_data')
    try:
        user = await sync_to_async(SignedPeople.objects.get)(user_id=user_id, status=True)
        await sync_to_async(OrderCourse.objects.get)(user=user.user_id, course=course.id)
        await query.answer(ok=False, error_message="Вы уже купили этот курс. Оплата не требуется.")
        return
    except OrderCourse.DoesNotExist:
        # покупок нет, подтверждаем платеж
        await query.answer(ok=True)





async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message.successful_payment:
        selection_data = context.user_data.get('selection_data')
        name_class = selection_data.__class__.__name__
        if name_class == 'SubscriptionOptions':
            await successful_payment_subscriptions(update, context)
        elif name_class == 'Course':
            await successful_payment_course(update, context)

    context.user_data.pop('invoice_payload')
    context.user_data.pop('selection_data')



async def successful_payment_subscriptions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    selection_data = context.user_data.get('selection_data')
    data = {
        'user_id': update.effective_user.id,
        'username': update.effective_user.first_name,
        'subscription': selection_data.slug,
        'status': True
    }
    try:
        await sync_to_async(SignedPeople.objects.create)(**data)
        await update.message.reply_text('Вы теперь подписчик! ознакомтись с политикой конфеденциальности')
        await privacy_policy(update, context)
    except SignedPeople.DoesNotExist as err:
        await update.message.reply_text(f'{err}')




async def successful_payment_course(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    selection_data = context.user_data.get('selection_data')
    try:
        user_id = update.effective_user.id
        user = await sync_to_async(SignedPeople.objects.get)(user_id=user_id)
    except OrderCourse.DoesNotExist:
        await update.message.reply_text(f'')
    data = {
        "user": user,
        "course": selection_data
    }
    try:
        await sync_to_async(OrderCourse.objects.create)(**data)
        await update.message.reply_text(f'эми сен курстун ээсисин !')
    except Exception as err:
        await update.message.reply_text(f'{err}')



async def pay_via_manager(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("Дорогой пользователь!Вы можете оплатить курс любым удобным "
                                  "для вас способом. После осуществления платежа, пожалуйста, "
                                  "сделайте фото квитанции и отправьте его в наш бот."
                                  "Наш менеджер проверит зачисление денег на счет и изменит статус"
                                  " вашего доступа к курсу.Для перевода денег, пожалуйста,"
                                  " используйте следующие реквизиты:"
                                  "[СЧЕТ КУДА МОЖНО ОТПРАВИТЬ ДЕНЕГ..........................] \n\n" 
                                  "Если у вас возникнут вопросы, не стесняйтесь обращаться к нам!"
                                  "Спасибо!")












