from decouple import config
from telegram import LabeledPrice, Update
from telegram.ext import ContextTypes

PAY_TOKEN = config('PAYMENT_PROVIDER_TOKEN')


async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    await query.message.reply_text(text='00000')


async def start_without_shipping_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):

    chat_id = update.message.chat_id
    title = "название"
    description = "описание"
    payload = "Custom-Payload"
    currency = "SOM"
    price = 2000
    prices = [LabeledPrice("Test", price * 100)]
    await context.bot.send_invoice(
        chat_id, title, description, payload, PAY_TOKEN, currency, prices
    )
    await update.message.reply_text('')


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:

    query = update.pre_checkout_query
    if query.invoice_payload != "Custom-Payload":
        await query.answer(ok=False, error_message="...............")
    else:
        await query.answer(ok=True)


