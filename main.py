import logging

from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update, KeyboardButton, WebAppInfo
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

HOME, ORDER, HELP, CONTACTUS, ABOUT, SUBMIT = range(6)


def effective_delete(update: Update, context: CallbackContext):
    if update.message:
        update.message.delete()


def start(update: Update, context: CallbackContext):
    for x in context.user_data.get('msg', []):
        try:
            x.delete()
        except Exception:
            pass
    msg = update.message.reply_text(
        "Welcome to ciket",
        reply_markup=ReplyKeyboardMarkup(
            [[KeyboardButton('HOME', web_app=WebAppInfo("https://google.com"))], ['Place Order'], ['Help', 'ContactUs'],
             ['About']], resize_keyboard=True
        ),
    )
    context.user_data.setdefault('msg', []).append(msg)
    return HOME


def order(update: Update, context: CallbackContext):
    for x in context.user_data.get('msg', []):
        try:
            x.delete()
        except Exception:
            pass
    msg = update.message.reply_text("Order page\n\nAvailable products", reply_markup=ReplyKeyboardMarkup([
        ['PCB', 'ANTI theft system'],
        ['LED Tapela', '3D Design and Printing'],
        ['PCB', 'ANTI theft system'],
        ['PCB', '3D Design and Printing', 'ANTI theft system'],
        ['PCB', 'ANTI theft system'],
        ["Back"]
    ], resize_keyboard=True))
    context.user_data.setdefault('msg', []).append(msg)
    return ORDER


def products(update: Update, context: CallbackContext):
    for x in context.user_data.get('msg', []):
        try:
            x.delete()
        except Exception:
            pass
    msg = update.message.reply_text(f"Ordering   <b>{update.message.text}</b>\n\nPlease provide the following details\n\n<code>Type\nAmount\nAlso\nOther\nDetails</code>", reply_markup=ReplyKeyboardMarkup([["Back"]], resize_keyboard=True), parse_mode="html")
    context.user_data.setdefault('msg', []).append(msg)
    return SUBMIT


def order_submit(update: Update, context: CallbackContext):
    for x in context.user_data.get('msg', []):
        try:
            x.delete()
        except Exception:
            pass
    msg = update.message.reply_text(f"Thanks   <b>{update.message.from_user.first_name}</b>\n\n<code>Order submitted successfully!\nWe will contact you shortly</code>", parse_mode="html")
    return start(update, context)


def helper(update: Update, context: CallbackContext):
    for x in context.user_data.get('msg', []):
        try:
            x.delete()
        except Exception:
            pass
    msg = update.message.reply_text("HELP page", reply_markup=ReplyKeyboardMarkup([["Back"]], resize_keyboard=True))
    context.user_data.setdefault('msg', []).append(msg)
    # return HELP


def contactus(update: Update, context: CallbackContext):
    for x in context.user_data.get('msg', []):
        try:
            x.delete()
        except Exception:
            pass
    msg = update.message.reply_text("CONTACTUS page", reply_markup=ReplyKeyboardMarkup([["Back"]], resize_keyboard=True))
    context.user_data.setdefault('msg', []).append(msg)
    # return CONTACTUS


def about(update: Update, context: CallbackContext):
    for x in context.user_data.get('msg', []):
        try:
            x.delete()
        except Exception:
            pass
    msg = update.message.reply_text("ABOUT page", reply_markup=ReplyKeyboardMarkup([["Back"]], resize_keyboard=True))
    context.user_data.setdefault('msg', []).append(msg)
    # return ABOUT


def main() -> None:
    updater = Updater("6416370425:AAHc8VUcj8fwrlvh45d1YdKqUeLigiG7hwg")
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            HOME: [
                MessageHandler(Filters.regex('Place Order'), order),
                MessageHandler(Filters.regex('Help'), helper),
                MessageHandler(Filters.regex('ContactUs'), contactus),
                MessageHandler(Filters.regex('About'), about),
            ],
            ORDER: [
                MessageHandler(Filters.regex('Back'), start),
                MessageHandler(Filters.text, products),
            ],
            SUBMIT: [
                MessageHandler(Filters.regex('Back'), start),
                MessageHandler(Filters.text, order_submit),
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('Back'), start), CommandHandler('start', start)],
    )

    dispatcher.add_handler(MessageHandler(Filters.all, effective_delete), -1)
    dispatcher.add_handler(conv_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    print('starting....')
    main()

# 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