# #!/usr/bin/env python
# # pylint: disable=unused-argument
# # This program is dedicated to the public domain under the CC0 license.
#
# """Basic example for a bot that can receive payment from user."""
#
# import logging
# from decouple import config
#
#
#
# from telegram import LabeledPrice, ShippingOption, Update
# from telegram.ext import (
#     Application,
#     CommandHandler,
#     ContextTypes,
#     MessageHandler,
#     PreCheckoutQueryHandler,
#     ShippingQueryHandler,
#     filters,
# )
#
# # Enable logging
# logging.basicConfig(
#     format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
# )
# # set higher logging level for httpx to avoid all GET and POST requests being logged
# logging.getLogger("httpx").setLevel(logging.WARNING)
#
# logger = logging.getLogger(__name__)
#
# PAYMENT_PROVIDER_TOKEN = "284685063:TEST:NjM1Mjk1ZTEyZDk1"
#
#
# async def start_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     """Displays info on how to use the bot."""
#     msg = (
#         " /noshipping for an "
#         "invoice without shipping."
#     )
#
#     await update.message.reply_text(msg)
#
#
# async def start_without_shipping_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
#
#     chat_id = update.message.chat_id
#     title = "Payment Example"
#     description = "Payment Example using python-telegram-bot"
#     payload = "Custom-Payload"
#     currency = "USD"
#     price = 1
#     prices = [LabeledPrice("Test", price * 100)]
#     await context.bot.send_invoice(
#         chat_id, title, description, payload, PAYMENT_PROVIDER_TOKEN, currency, prices
#     )
#     await update.message.reply_text('')
#
#
# async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#
#     query = update.pre_checkout_query
#     if query.invoice_payload != "Custom-Payload":
#         await query.answer(ok=False, error_message="Something went wrong...")
#     else:
#         await query.answer(ok=True)
#
#
#
# async def successful_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     await update.message.reply_text("Thank you for your payment!")
#
#
# def main() -> None:
#     application = Application.builder().token(config("TOKEN_BOT")).build()
#     application.add_handler(CommandHandler("start", start_callback))
#     application.add_handler(CommandHandler("noshipping", start_without_shipping_callback))
#     application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
#
#     application.add_handler(
#         MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment_callback)
#     )
#
#
#     application.run_polling(allowed_updates=Update.ALL_TYPES)
#
#
# if __name__ == "__main__":
#     main()
#
#
#
#
#
#
