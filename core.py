import telebot
import requests
import json
from telebot import types
from datetime import datetime

# Type here your Telegram Bot API token
API_TOKEN = "XXXX"

bot = telebot.TeleBot(API_TOKEN)

address = ""
key_ = ""


def get_tx(key, address):
    req = requests.get("https://api.bscscan.com/api"
                       + "?module=account"
                       + "&action=txlist"
                       + f"&address={address}"
                       + "&startblock=0"
                       + "&endblock=99999999"
                       + "&sort=desc"
                       + f"&apikey={key}")
    return json.loads(req.text)


def sort_tx(tx_list):
    inc_tx = [tx for tx in tx_list["result"] if tx["to"] == address.lower()]
    print(len(inc_tx))
    return inc_tx


def get_inc_tx():
    return sort_tx(get_tx(key_, address))


def unit_conv(unit):
    if '.' in unit:
        if len(unit) == 5:
            return float(unit) * 10**3
        if len(unit) == 8:
            return float(unit) * 10**6
        if len(unit) == 11:
            return float(unit) * 10**9
        if len(unit) == 14:
            return float(unit) * 10**12
    if len(unit) == 19 or 18:
        return int(unit) * 10**-18
    if len(unit) == 16:
        return int(unit) * 10**-15
    if len(unit) == 13:
        return int(unit) * 10**-12
    if len(unit) == 10:
        return int(unit) * 10**-9
    if len(unit) == 7:
        return int(unit) * 10**-6
    if len(unit) == 4:
        return int(unit) * 10**-3
    if len(unit) == 1:
        return int(unit)
    else:
        return unit


@bot.message_handler(commands=["start"])
def say_hi(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton("Type your BSCscan Apikey")
    btn2 = types.KeyboardButton("Type address")
    btn3 = types.KeyboardButton("Get incoming transactions")
    markup.add(btn1, btn2, btn3)
    bot.send_message(message.chat.id, text="Hi", reply_markup=markup)


@bot.message_handler(content_types=["text"])
def type_data(message):
    if message.text == "Type your BSCscan Apikey":
        msg = bot.reply_to(
            message,
            """\
    Type or Paste your ApiKey from BSCscan
    """,
        )
        bot.register_next_step_handler(msg, process_get_key)
    if message.text == "Type address":
        msg = bot.reply_to(
            message,
            """\
    Type or Paste your address
    """,
        )
        bot.register_next_step_handler(msg, process_get_address)
    if message.text == "Get incoming transactions":
        try:
            for tx in get_inc_tx():
                print(tx)
                bot.send_message(message.chat.id,
                                 text=
                                 "time : " f"{datetime.utcfromtimestamp(float(tx['timeStamp'])).strftime('%Y-%m-%d %H:%M:%S')} \n" \
                                 "type : " f"{tx['functionName']} \n" \
                                 "value : " f"{unit_conv(tx['value'])} \n" \
                                 "status : " f"{'Done' if tx['txreceipt_status'] == '1' else 'Fail'}"

                                 )
        except Exception as e:
            bot.reply_to(message, "oops! Try again type your data")


def process_get_key(message):
    global key_
    key_ = message.text
    bot.reply_to(message, "ApiKey added!")


def process_get_address(message):
    global address
    address = message.text
    bot.reply_to(message, "Address added!")


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling()
