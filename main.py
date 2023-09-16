import logging
import sqlite3
from telegram import ReplyKeyboardMarkup, InlineKeyboardMarkup, Update, InlineKeyboardButton
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)

HOME, ORDER, PRODUCT_OR_SERVICE, HELP, CONTACTUS, ABOUT, CONFIRM, SUBMIT = range(8)


'''
conn = sqlite3.connect('database.db')
c = conn.cursor()
c.execute("""CREATE TABLE products (
            name text,
            price real,
            description text
)""")
c.execute("INSERT INTO products VALUES ('PCB', 123.34, 'this is good')")
conn.commit()
c.execute("SELECT * from products WHERE name='PCB'")
conn.commit()
conn.close()
'''


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
            [['Place Order'], ['Help', 'ContactUs'],
             ['About']], resize_keyboard=True
        ),
    )
    context.user_data.setdefault('msg', []).append(msg)
    return HOME


def product_or_services(update: Update, context: CallbackContext):
    for x in context.user_data.get('msg', []):
        try:
            x.delete()
        except Exception:
            pass
    msg = update.message.reply_text(
        "Products and Services",
        reply_markup=ReplyKeyboardMarkup(
            [['Products', 'Services'],
             ['Back']], resize_keyboard=True
        ),
    )
    context.user_data.setdefault('msg', []).append(msg)
    return PRODUCT_OR_SERVICE


def order(update: Update, context: CallbackContext):
    context.user_data['p_or_s'] = update.message.text
    for x in context.user_data.get('msg', []):
        try:
            x.delete()
        except Exception:
            pass

    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT name from " + context.user_data.get('p_or_s'))
    keyboard = []
    row = []
    for i, x in enumerate(c.fetchall()):
        row.append(x[0])
        if (i + 1) % 2 == 0:
            keyboard.append(row)
            row = []
    c.close()
    conn.close()
    if row:
        keyboard.append(row)
    keyboard.append(['Back'])
    msg = update.message.reply_text("Order page\n\nAvailable Items", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
    context.user_data.setdefault('msg', []).append(msg)
    return ORDER


def products(update: Update, context: CallbackContext):
    for x in context.user_data.get('msg', []):
        try:
            x.delete()
        except Exception:
            pass
    conn = sqlite3.connect('database.db')
    c = conn.cursor()
    c.execute("SELECT * from " + context.user_data.get('p_or_s') + " WHERE name=?", (update.message.text,))
    aproduct = c.fetchone()
    if not aproduct:
        msg = update.message.reply_text("Item not found",  reply_markup=ReplyKeyboardMarkup([["Back"]], resize_keyboard=True), parse_mode="html")
        context.user_data.setdefault('msg', []).append(msg)
        return
    msg_txt = f"""

Name:  <b>{aproduct[0]}</b>
Unit Price:  <b>{aproduct[1]}ETB</b>
Description:  <code>{aproduct[2]}</code>
<b> {aproduct[3]} </b>

Customer Message: {context.user_data.get('customer_message') or None}

<code>use /message your message to us</code>
    <u>eg.</u> /message i want it for this monday
<code>use /calc number of items you want"</code>
    <u>eg.</u> /calc 4
    """
    msg = update.message.reply_text(msg_txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Submit', callback_data='s'), InlineKeyboardButton('Cancel', callback_data='c')]]), parse_mode="html")
    context.user_data.setdefault('msg', []).append(msg)
    context.user_data['ordering'] = aproduct[0]
    context.user_data['selected_item'] = update.message.text
    context.user_data['selected_price'] = aproduct[1]
    return CONFIRM


def customer_message(update: Update, context: CallbackContext):
    context.user_data['customer_message'] = ' '.join(context.args)
    update.message.text = context.user_data['selected_item']
    return products(update, context)


def calc_item(update: Update, context: CallbackContext):
    if not context.args or len(context.args) != 1 or not context.args[0].isdigit():
        msg = update.message.reply_text('invalid data to calc')
        context.user_data.setdefault('msg', []).append(msg)
        return
    msg = update.message.reply_text(f"{context.args[0]} items equals to {int(context.args[0]) * context.user_data.get('selected_price', 0)}")
    context.user_data.setdefault('msg', []).append(msg)


def order_confirm(update: Update, context: CallbackContext):
    for x in context.user_data.get('msg', []):
        try:
            x.delete()
        except Exception:
            pass
    msg = update.message.reply_text(f"<b>Confirm your Order</b>\n\nOrdering: {context.user_data.get('ordering', '-')}\n\n<code>{update.message.text}</code>\n\n___", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton('Submit', callback_data='s'), InlineKeyboardButton('Cancel', callback_data='c')]]), parse_mode="html")
    context.user_data.setdefault('msg', []).append(msg)
    context.user_data['ordering_msg'] = update.message.text
    return SUBMIT


def order_submit(update: Update, context: CallbackContext):
    for x in context.user_data.get('msg', []):
        try:
            x.delete()
        except Exception:
            pass
    if update.callback_query.data == 's':
        context.bot.send_message(chat_id=-1001798663641, text=f"___\n\n\nOrdering: {context.user_data.get('ordering', '-')}\n\nName: {update.effective_user.first_name}\nUsername: @{update.effective_user.username}\nMessage: {context.user_data.get('customer_message')}\n\n\n___")
        msg = context.bot.send_message(update.effective_chat.id, text=f"Thanks   <b>{update.effective_user.first_name}</b>\n\n<code>Order submitted successfully!\nWe will contact you shortly</code>", parse_mode="html")
        context.user_data.setdefault('msg', []).append(msg)
    elif update.callback_query.data == 'c':
        msg = context.bot.send_message(update.effective_chat.id, text=f"Order Canceled")
        context.user_data.setdefault('msg', []).append(msg)


    msg = context.bot.send_message(update.effective_chat.id, text=
        "Welcome to ciket",
        reply_markup=ReplyKeyboardMarkup(
            [['Place Order'], ['Help', 'ContactUs'],
             ['About']], resize_keyboard=True
        ),
    )
    context.user_data.setdefault('msg', []).append(msg)
    return HOME


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
    msg = update.message.reply_text("Ciket Technology\n\nPhone: +2519111111\nEmail: ciket@gmail.com\n\nHave a Question or want to give us Feedback or to report a But.\nPlease don't hesitate to reach out <a href='https://'", reply_markup=ReplyKeyboardMarkup([["Back"]], resize_keyboard=True))
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
    updater = Updater("6416370425:AAHfwMPDxp6KusdP39AnUHiqlfaEIMHnYRY")
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            HOME: [
                MessageHandler(Filters.regex('Place Order'), product_or_services),
                MessageHandler(Filters.regex('Help'), helper),
                MessageHandler(Filters.regex('ContactUs'), contactus),
                MessageHandler(Filters.regex('About'), about),
            ],
            PRODUCT_OR_SERVICE: [
                MessageHandler(Filters.regex('Products'), order),
                MessageHandler(Filters.regex('Services'), order),
                MessageHandler(Filters.regex('Back'), start),
            ],
            ORDER: [
                MessageHandler(Filters.regex('Back'), product_or_services),
                MessageHandler(Filters.text, products),
            ],
            CONFIRM: [
                MessageHandler(Filters.regex('Back'), start),
                CommandHandler('message', customer_message),
                CommandHandler('calc', calc_item),
                CallbackQueryHandler(order_submit, pattern='s|c'),
            ],
            SUBMIT: [
                MessageHandler(Filters.regex('Back'), start),
                CallbackQueryHandler(order_submit, pattern='s|c'),
            ]
        },
        fallbacks=[MessageHandler(Filters.regex('Back'), start), CommandHandler('start', start)],
    )

    dispatcher.add_handler(MessageHandler(Filters.all, effective_delete), -1)
    dispatcher.add_handler(conv_handler)

    updater.start_polling(drop_pending_updates=True)
    updater.idle()


if __name__ == '__main__':
    print('starting....')
    main()

# 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