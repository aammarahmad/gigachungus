from config import (invalid_format_warning, wrong_info, menu, greet, report_a_manual,
                    language_changed, report_b_manual, report_c_manual)
from keys import TOKEN, REQUEST_KEYS
from functions import (report_a_request, report_b_request, language, log, report_log,
                       add_to_arabic_users, remove_from_arabic_users)
from apifunctions import generate_rep_id, get_chat_id, report_c_request, log_req
import telebot


bot = telebot.TeleBot(TOKEN, threaded=False)


def start_handler(msg):
    chat_id = msg.chat.id
    lang = language(chat_id)
    bot.send_photo(chat_id, photo=open(greet[lang], 'rb'), caption=menu[lang])
    log(msg)


def change_language_handler(msg):
    lang = 0 if msg.text.strip('/') == 'ar' else 1
    chat_id = msg.chat.id
    if lang == 0:
        add_to_arabic_users(chat_id)
    else:
        remove_from_arabic_users(chat_id)
    bot.reply_to(msg, language_changed[lang])


def report_ab_handler(msg):
    log(msg)
    chat_id = msg.chat.id
    lang = language(chat_id)
    text = msg.txt
    report = report_a_request(text, lang) if text.startswith('a') else report_b_request(text, lang)
    if report == -1:
        bot.reply_to(msg, text=invalid_format_warning[lang])
    elif report == -2:
        bot.reply_to(msg, text=wrong_info[lang])
    else:
        bot.send_message(chat_id=chat_id, text=report)
        report_log(chat_id, report)


def report_c_handler(msg):
    chat_id = msg.chat.id
    rep_id = generate_rep_id(chat_id)
    bot.send_message(chat_id=chat_id, text=rep_id)


def report_manual_handler(msg):
    chat_id = msg.chat.id
    lang = language(chat_id)
    text = (report_a_manual[lang] if msg.text.endswith('a') else report_b_manual[lang] if msg.text.endswith('b')
    else report_c_manual[lang])
    bot.send_message(chat_id=chat_id, text=report_a_manual[lang])


def api_report_request_handler(request_json):
    log_req(request_json)
    if request_json is None:
        return 400
    key = request_json.get('key')
    if key not in REQUEST_KEYS:
        return 'Your are not allowed to use this service', 403
    chat_id = get_chat_id(request_json.get('repid'))
    if chat_id is None:
        return 'rep_id invalid or expired', 400

    lang = language(chat_id)
    report = report_c_request(request_json, lang)
    if report == -1:
        bot.send_message(chat_id=chat_id, text='An unexpected error occurred')
        return 'bad request', 400
    elif report == -2:
        bot.send_message(chat_id=chat_id, text=wrong_info[lang])
        return 'wrong info', 400
    else:
        bot.send_message(chat_id=chat_id, text=report)
    return 'report sent', 200