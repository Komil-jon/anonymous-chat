from flask import Flask, request
from pymongo import MongoClient
import requests
import json
import os

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN = os.getenv('ADMIN')
GROUP = os.getenv('GROUP')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
PAYMENT_TOKEN = os.getenv('PAYMENT_TOKEN')

# global lan
# only for testing 👆
lan = 'en'

COMMANDS = [
    '/help', '/show', '/cancel', '/premium', '/report', '/policy', '/menu', '/bonus', 'Manual', "Qo'llanma",
    "Руководство", 'My link', "Mening havolam", "Моя ссылка", 'Premium 🎁', "Премиум 🎁", 'Feedback',
    "Fikr-mulohaza", "Обратная связь", 'Policy', "Siyosat", "Политика", 'Coins 🎁', "Tangalar 🎁", "Монеты 🎁",
    "Bonus 🔥", "Бонус 🔥"
]

app = Flask(__name__)

@app.route('/', methods=['POST'])
def handle_webhook():
    try:
        process(json.loads(request.get_data()))
        return 'Success!'
    except Exception as e:
        print('error was:', e, json.loads(request.get_data()))
        return '-1'

def testing():
    global last_update_id
    last_update_id = -1
    while True:
        updates = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getUpdates?offset={last_update_id}").json().get('result', []
        )
        for update in updates:
            print(update)
            process(update)
            last_update_id = update['update_id'] + 1

def process(update):
    global lan
    if 'message' in update:
        lan = update['message']['from'].get('language_code', 'en')
        if 'text' in update['message']:
            text = update['message']['text']
            if text[:6] == '/start':
                initial(
                    update['message']['from']['id'],
                    update['message']['from']['first_name'],
                    update['message']['text'], update['message']['from']
                )
            elif any(text == command for command in COMMANDS):
                commands(
                    update['message']['from']['id'], text
                )
            elif update['message']['from']['id'] == int(ADMIN) and text.split()[0] == '/make_premium':
                make_premium(text)
            else:
                message(
                    update['message']['from']['id'],
                    update['message']['message_id'],
                    text
                )
        else:
            media(
                update['message']['from']['id'],
                update['message']['message_id']
            )
    elif 'callback_query' in update and 'data' in update['callback_query']:
        
        text = update['callback_query']['message'].get('text') or update['callback_query']['message'].get('caption')

        lan = update['callback_query']['from'].get(
            'language_code',
            'en'
        )
        callback(
            update['callback_query']['data'],
            update['callback_query']['from']['id'],
            update['callback_query']['message']['message_id'],
            text
        )
    elif 'inline_query' in update:
        lan = update['inline_query']['from'].get(
            'language_code',
            'en'
        )
        inline(
            update['inline_query']['from']['id'],
            update['inline_query']['query'],
            update['inline_query']['id']
        )
    else:
        print("unwanted type of message", update)
        lan = 'en'



def initial(user_id, first_name, text, user):
    t = {
        "1": {
            "en": "Hey!",
            "uz": "Salom!",
            "ru": "Привет!"
        },
        "2": {
            "en": "What's up?",
            "uz": "Nima gap?",
            "ru": "Как дела?"
        },
        "3": {
            "en": "Start the conversation",
            "uz": "Suhbatni boshlash",
            "ru": "Начать разговор"
        },
        "4": {
            "en": "Cancel",
            "uz": "Bekor qilish",
            "ru": "Отмена"
        },
        "5": {
            "en": "You are writing to",
            "uz": "Siz yozmoqchi bo'lgan inson",
            "ru": "Вы пишете"
        },
        "6": {
            "en": "You clicked on an invalid link..",
            "uz": "Siz bosgan havolada muammo bor.",
            "ru": "Вы нажаmenuли на недействительную ссылку."
        }
    }
    if text == '/start':
        if database_search({"id": user_id}) == None:
            record = {
                "id": user_id,
                "name": first_name,
                "nick": None,
                "referral": 0,
                "username": user.get("username", None),
                "to": None,
                "previous": None,
                "block": None,
                "premium": False,
                "coins": 0
            }
            database_insert(record)
            alert(json.dumps(user))
        menu(
            user_id,
            f"👋 *{t.get('1').get(lan, t.get('1').get('en'))}* {first_name} ! *{t.get('2').get(lan, t.get('2').get('en'))}*"
        )
    else:
        if text[7].isdigit():
            receiver = database_search({"id": int(text[7:])})
        else:
            receiver = database_search({"nick": text[7:]})
        if receiver == None:
            if database_search({"id": user_id}) == None:
                record = {
                    "id": user_id,
                    "name": first_name,
                    "nick": None,
                    "referral": 0,
                    "username": user.get("username", None),
                    "to": None,
                    "previous": None,
                    "block": None,
                    "premium": False,
                    "coins": 0
                }
                database_insert(record)
            menu(
                user_id,
                f"*{t.get('1').get(lan, t.get('1').get('en'))}* {first_name} ! {t.get('6').get(lan, t.get('6').get('en'))} 😔"
            )
        else:
            reply_markup = {
                'inline_keyboard':
                    [[{'text': f"{t.get('3').get(lan, t.get('3').get('en'))}", 'callback_data': f"{receiver['id']}"}],
                    [{'text': f"{t.get('4').get(lan, t.get('4').get('en'))}", 'callback_data': f"{0}"}]]
            }
            requests.post(
                url = f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                params={
                    'chat_id': user_id,
                    'text': f"ℹ️ *{t.get('5').get(lan, t.get('5').get('en'))}* {receiver['name']}\n",
                    'parse_mode': 'Markdown',
                    'reply_markup': json.dumps(reply_markup)}
            )
            if database_search({"id": user_id}) == None:
                record = {
                    "id": user_id,
                    "name": first_name,
                    "nick": None,
                    "referral": 0,
                    "username": user.get("username", None),
                    "to": None,
                    "previous": None,
                    "block": None,
                    "premium": False,
                    "coins": 0
                }
                database_insert(record)
                alert(json.dumps(user))

def message(user_id, message_id, text):
    t = {
        "1": {
            "en": "*Currently, you do not have any ongoing conversations.*\nPress the button _Start the conversation_, _Reply_ or _Send another message_.",
            "uz": "*Siz hozircha hech kim bilan suhbat boshlamagansiz.*\n_Suhbatni boshlash_, _Javob yozish_ yoki _Yana boshqa xabar yuborish_ tugmasini bosing.",
            "ru": "*В настоящее время у вас нет текущих разговоров.*\nНажмите кнопку _Начать разговор_, _Ответить_ или _Отправить еще одно сообщение_."
        },
        "2": {
            "en": "You can not write to yourself. Hence, the conversation cancelled.",
            "uz": "Siz o'zingizga yozolmaysiz. Shu sababli suhbat bekor qilindi.",
            "ru": "Вы не можете писать себе. Поэтому разговор прервался."
        },
        "3": {
            "en": "Author",
            "uz": "Muallif",
            "ru": "Автор"
        },
        "4": {
            "en": "Reply",
            "uz": "Javob yozish",
            "ru": "Ответить"
        },
        "5": {
            "en": "You have a new message",
            "uz": "Sizda yangi xabar mavjud",
            "ru": "У вас новое сообщение"
        },
        "6": {
            "en": "Send another message",
            "uz": "Yana boshqa xabar yuborish",
            "ru": "Отправить еще одно сообщение"
        },
        "7": {
            "en": "Cancel",
            "uz": "Bekor qilish",
            "ru": "Отмена"
        },
        "8": {
            "en": "Your message is delivered Successfully!",
            "uz": "Sizning xabaringiz muvaffaqiyatli yetkazildi!",
            "ru": "Ваше сообщение успешно доставлено!"
        },
        "9": {
            "en": "I could not deliver your message.\nYour message contains keywords.",
            "uz": "Sizning xabaringizni yetkazib berolmadim.\n.Sizning xabaringizda kalit so'zlar mavjud.",
            "ru": "Я не смог доставить ваше сообщение.\nВаше сообщение содержит ключевые слова."
        },
        "10": {
            "en": "First name: ",
            "uz": "Ismi: ",
            "ru": "Имя: "
        },
        "11": {
            "en": "Telegram ID: ",
            "uz": "Telegram IDsi: ",
            "ru": "Идентификатор телеграммы: "
        },
        "12": {
            "en": "Username: @",
            "uz": "Foydalanuvchi nomi: @",
            "ru": "Имя пользователя: @"
        },
        "13": {
            "en": "Not available",
            "uz": "Mavjud emas",
            "ru": "Нет в наличии"
        },
        "14": {
            "en": "_System has been updated._ *Please re /start.*",
            "uz": "_Botda yangilandi._ *Iltimos /start buyrugini bering.*",
            "ru": "_Система обновлена._ *Пожалуйста, перезапустите /start.*"
        },
        "15": {
            "en": "Spam",
            "uz": "Spam",
            "ru": "Спам"
        },
        "16": {
            "en": "*You have been blocked by the receiver!*\n_I can not deliver your message_.",
            "uz": "*Siz yozmoqchi bo'lgan foydalanuvchi sizni bloklagan!*\n_Afsuski, xabaringizni yetkaza olmayman_.",
            "ru": "*Вы были заблокированы получателем!*\n_Я не могу доставить ваше сообщение_."
        }
    }
    sender = database_search({"id": user_id})
    receiver_id = sender["to"]
    if receiver_id == None:
        photo_params = {
            'chat_id': user_id,
            'photo': 'https://raw.githubusercontent.com/Komil-jon/anonymous-chat/main/assets/error.jpg',
            'caption': f"🤷‍♂️ {t.get('1').get(lan, t.get('1').get('en'))}",
            'parse_mode': 'Markdown'
        }
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto',
            params=photo_params
        )
    else:
        receiver_id = int(receiver_id)
        receiver = database_search({"id": receiver_id})
        if receiver["block"] != user_id:
            if user_id == receiver_id:
                requests.post(
                    f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                    params={
                        'chat_id': receiver_id,
                        'text': f"ℹ️ *{t.get('2').get(lan, t.get('2').get('en'))}*",
                        'parse_mode': 'Markdown'}
                )
                cancel(user_id)
            else:
                if receiver["premium"]:
                    reply_markup = {'inline_keyboard': [[{'text': f"{t.get('3').get(lan, t.get('3').get('en'))}", 'callback_data': f"P{message_id} {user_id}"}], [
                                                        {'text': f"{t.get('4').get(lan, t.get('4').get('en'))}", 'callback_data': f"R{user_id} {message_id}"}], [
                                                        {'text': f"{t.get('15').get(lan, t.get('15').get('en'))}", 'callback_data': f"S{user_id} {message_id}"}]]
                                    }
                else:
                    reply_markup = {'inline_keyboard': [[{'text': f"{t.get('4').get(lan, t.get('4').get('en'))}", 'callback_data': f"R{user_id} {message_id}"}], [
                                                        {'text': f"{t.get('15').get(lan, t.get('15').get('en'))}", 'callback_data': f"S{user_id} {message_id}"}]]
                                    }
                status = requests.post(
                    f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                    params={'chat_id': receiver_id,
                            'text': f"<strong>{t.get('5').get(lan, t.get('5').get('en'))}</strong> 🎯\n\n{text}",
                            'parse_mode': 'HTML',
                            'reply_markup': json.dumps(reply_markup),
                            'reply_to_message_id': sender["previous"]
                            }
                ).status_code
                if (status == 200):
                    reply_markup = {'inline_keyboard': [
                                [{'text': f"{t.get('6').get(lan, t.get('6').get('en'))}", 'callback_data': f"{receiver_id}"}],
                                [{'text': f"{t.get('7').get(lan, t.get('7').get('en'))}", 'callback_data': f"{0}"}]]}
                    requests.post(
                        f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                        params={'chat_id': user_id,
                                'text': f"✅ *{t.get('8').get(lan, t.get('8').get('en'))}*",
                                'parse_mode': 'Markdown',
                                'reply_markup': json.dumps(reply_markup)
                                }
                    )
                else:
                    data = {
                        'chat_id': user_id,
                        'text': f"😔 *{t.get('9').get(lan, t.get('9').get('en'))}*",
                        'parse_mode': 'Markdown'
                    }
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        data=data
                    )
                cancel(user_id)
        else:
            requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                params={'chat_id': user_id,
                        'text': f"ℹ️ {t.get('16').get(lan, t.get('16').get('en'))}",
                        'parse_mode': 'Markdown'
                        }
            )
            cancel(user_id)

def media(user_id, message_id):
    t = {
        "1": {
            "en": "*Currently, you do not have any ongoing conversations.*\nPress the button _Start the conversation_, _Reply_ or _Send another message_.",
            "uz": "*Siz hozircha hech kim bilan suhbat boshlamagansiz.*\n_Suhbatni boshlash_, _Javob yozish_ yoki _Yana boshqa xabar yuborish_ tugmasini bosing.",
            "ru": "*В настоящее время у вас нет текущих разговоров.*\nНажмите кнопку _Начать разговор_, _Ответить_ или _Отправить еще одно сообщение_."
        },
        "2": {
            "en": "You can not write to yourself. Hence, the conversation cancelled.",
            "uz": "Siz o'zingizga yozolmaysiz. Shu sababli suhbat bekor qilindi.",
            "ru": "Вы не можете писать себе. Поэтому разговор прервался."
        },
        "3": {
            "en": "Author",
            "uz": "Muallif",
            "ru": "Автор"
        },
        "4": {
            "en": "Reply",
            "uz": "Javob yozish",
            "ru": "Ответить"
        },
        "5": {
            "en": "You have a new media",
            "uz": "Sizda yangi mediafayl mavjud",
            "ru": "У вас новые медиа"
        },
        "6": {
            "en": "Send another message",
            "uz": "Yana boshqa xabar yuborish",
            "ru": "Отправить еще одно сообщение"
        },
        "7": {
            "en": "Cancel",
            "uz": "Bekor qilish",
            "ru": "Отмена"
        },
        "8": {
            "en": "Your media is delivered Successfully!",
            "uz": "Sizning xabaringiz muvaffaqiyatli yetkazildi!",
            "ru": "Ваше медиа успешно доставлено!"
        },
        "9": {
            "en": "I could not deliver your media.\nThere is a problem with your media.",
            "uz": "Sizning mediafaylingizni yetkazib berolmadim.\n.Sizning mediafaylingizda muammo bor.",
            "ru": "Я не смог доставить ваши медиафайлы.\nВозникла проблема с вашими медиафайлами."
        },
        "10": {
            "en": "First name: ",
            "uz": "Ismi: ",
            "ru": "Имя: "
        },
        "11": {
            "en": "Telegram ID: ",
            "uz": "Telegram IDsi: ",
            "ru": "Идентификатор телеграммы: "
        },
        "12": {
            "en": "Username: @",
            "uz": "Foydalanuvchi nomi: @",
            "ru": "Имя пользователя: @"
        },
        "13": {
            "en": "Not available",
            "uz": "Mavjud emas",
            "ru": "Нет в наличии"
        },
        "14": {
            "en": "Spam",
            "uz": "Spam",
            "ru": "Спам"
        },
        "15": {
            "en": "_System has been updated._ *Please re /start.*",
            "uz": "_Botda yangilandi._ *Iltimos /start buyrugini bering.*",
            "ru": "_Система обновлена._ *Пожалуйста, перезапустите /start.*"
        },
        "16": {
            "en": "*You have been blocked by the receiver!*\n_I can not deliver your message_.",
            "uz": "*Siz yozmoqchi bo'lgan foydalanuvchi sizni bloklagan!*\n_Afsuski, xabaringizni yetkaza olmayman_.",
            "ru": "*Вы были заблокированы получателем!*\n_Я не могу доставить ваше сообщение_."
        }
    }
    sender = database_search({"id": user_id})
    receiver = sender["to"]
    if receiver == None:
        photo_params = {
            'chat_id': user_id,
            'photo': 'https://raw.githubusercontent.com/Komil-jon/anonymous-chat/main/assets/error.jpg',
            'caption': f"🤷‍♂️ {t.get('1').get(lan, t.get('1').get('en'))}",
            'parse_mode': 'Markdown'
        }
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto',
            params=photo_params
        )
    else:
        if database_search({"id": receiver, "block": user_id}) == None:
            if user_id == receiver:
                requests.post(
                    f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                    params={'chat_id': receiver,
                            'text': f"ℹ️ *{t.get('2').get(lan, t.get('2').get('en'))}*",
                            'parse_mode': 'Markdown'
                            }
                )
                cancel(user_id)
            else:
                forwarded_message_id = requests.post(
                    f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage',
                        data={'chat_id': receiver,
                            'from_chat_id': user_id,
                            'message_id': message_id,
                            'reply_to_message_id': sender["previous"]
                              }
                ).json()['result']['message_id']

                if sender["premium"]:
                    reply_markup = {
                        'inline_keyboard':
                            [[{'text': f"{t.get('3').get(lan, t.get('3').get('en'))}", 'callback_data': f"P{message_id} {user_id}"}],
                             [{'text': f"{t.get('4').get(lan, t.get('4').get('en'))}", 'callback_data': f"R{user_id} {message_id}"}],
                             [{'text': f"{t.get('14').get(lan, t.get('14').get('en'))}", 'callback_data': f"S{user_id} {message_id}"}]]
                    }
                else:
                    reply_markup = {
                        'inline_keyboard': [[{'text': f"{t.get('4').get(lan, t.get('4').get('en'))}", 'callback_data': f"R{user_id} {message_id}"}],
                                            [{'text': f"{t.get('14').get(lan, t.get('14').get('en'))}", 'callback_data': f"S{user_id} {message_id}"}]]
                    }
                status = requests.post(
                    f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                        params={
                            'chat_id': receiver,
                            'text': f"*{t.get('5').get(lan, t.get('5').get('en'))}* 🎯",
                            'parse_mode': 'Markdown',
                            'reply_markup': json.dumps(reply_markup),
                            'reply_to_message_id': forwarded_message_id
                        }
                ).status_code

                if status == 200:
                    reply_markup = {
                        'inline_keyboard': [[{'text': f"{t.get('6').get(lan, t.get('6').get('en'))}", 'callback_data': f"{receiver}"}],
                                            [{'text': f"{t.get('7').get(lan, t.get('7').get('en'))}", 'callback_data': f"{0}"}]]
                    }
                    requests.post(
                        f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                        params={
                            'chat_id': user_id,
                            'text': f"✅ *{t.get('8').get(lan, t.get('8').get('en'))}*",
                            'parse_mode': 'Markdown',
                            'reply_markup': json.dumps(reply_markup)
                            }
                    )
                else:
                    data = {
                        'chat_id': user_id,
                        'text': f"😔 *{t.get('9').get(lan, t.get('9').get('en'))}*",
                        'parse_mode': 'Markdown'
                    }
                    requests.post(
                        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                        data=data
                    )
                cancel(user_id)
        else:
            requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                params={
                    'chat_id': user_id,
                    'text': f"ℹ️ {t.get('16').get(lan, t.get('16').get('en'))}",
                    'parse_mode': 'Markdown'
                }
            )
            cancel(user_id)


def callback(data, user_id, message_id, text):
    t = {
        "1": {
            "en": "You cancelled the conversation!",
            "uz": "Siz suhbatni bekor qildingiz!",
            "ru": "Вы отменили разговор!"
        },
        "2": {
            "en": "The message was:",
            "uz": "Xabar shundan iborat edi:",
            "ru": "Сообщение было:"
        },
        "3": {
            "en": "Author",
            "uz": "Muallif",
            "ru": "Автор"
        },
        "4": {
            "en": "Send your reply! Message was:",
            "uz": "Javobingizni yuboring! Xabar shundan iborat edi:",
            "ru": "Отправьте свой ответ! Сообщение было:"
        },
        "5": {
            "en": "Cancel",
            "uz": "Bekor qilish",
            "ru": "Отмена"
        },
        "6": {
            "en": "Reply",
            "uz": "Javob yozish",
            "ru": "Ответить"
        },
        "7": {
            "en": "You do not have enough ☄️ Galacoins!",
            "uz": "Sizda ☄️ Galakoynlar yetarli emas!",
            "ru": "У вас недостаточно ☄️ Галакоинов!"
        },
        "8": {
            "en": "We are having trouble fetching the name. If you are seeing this message, please /report this issue",
            "uz": "Ismni olishda muammo bor. Agar siz bu xabarni ko'rsatsangiz, iltimos, /report buyrug'ini bajaring",
            "ru": "У нас возникли проблемы с получением имени. Если вы видите это сообщение, пожалуйста, /report об этой проблеме"
        },
        "9": {
            "en": "The message below has been written by",
            "uz": "Quyidagi xabarni yozgan inson bu",
            "ru": "Сообщение ниже написал"
        },
        "10": {
            "en": "Become a premium member and get additional features stated.",
            "uz": "Premium rejasiga a'zo bo'ling va aytilgan qo'shimcha imkoniyatlarga ega bo'ling.",
            "ru": "Станьте премиум-участником и получите заявленные дополнительные функции."
        },
        "11": {
            "en": "Permanent premium plan",
            "uz": "Doimiy premium rejasi",
            "ru": "Постоянный план премиум-подписки"
        },
        "12": {
            "en": "No worries, you can still use the bot without any annoying ads.",
            "uz": "Xavotir olmang, siz shundog'am botni hech qanday reklamasiz foydalanishingiz mumkin.",
            "ru": "Без беспокойств, вы все равно можете использовать бота без назойливой рекламы."
        },
        "13": {
            "en": "_Current price of 1 Galacoin = 1000.00 UZS_\n☄️ *Choose an appropriate section\n\n☝️ If you find a bug and report it, you will be rewarded!*",
            "uz": "_1 Galakoynning joriy narxi = 1000.00 UZS_\n☄️ *Mos keladigan bo'limni tanlang\n\n☝️ Agar botdan birorta kamchilik topasangiz va xabarni bersangiz, siz mukofotlanasiz!*",
            "ru": "_Текущая цена 1 Галакоина = 1000,00 UZS_\n☄️ *Выберите подходящий раздел\n\n☝️ Если вы найдете ошибку и сообщите о ней, вы будете вознаграждены!*"
        },
        "14": {
            "en": "Payment",
            "uz": "To'lov",
            "ru": "Оплата"
        },
        "15": {
            "en": "Pay to get Galacoins",
            "uz": "Galakoynlar olish uchun to'lov qilish",
            "ru": "Оплатите, чтобы получить Галакоинов"
        },
        "16": {
            "en": "Alright. Send your message",
            "uz": "Tushunarli. Xabaringizni yuboring",
            "ru": "Хорошо. Отправьте свое сообщение"
        },
        "17": {
            "en": "Remaining Galacoins",
            "uz": "Qolgan Galakoynlar",
            "ru": "Оставшиеся Галакоинов"
        },
        "18": {
            "en": "You are writing to the administrator.",
            "uz": "Siz administratorga yozyapsiz.",
            "ru": "Вы пишите администратору."
        },
        "19": {
            "en": "Block temporarily",
            "uz": "Vaqtincha bloklash",
            "ru": "Временно заблокировать"
        },
        "20": {
            "en": "*I am really sorry to show this message!*\n\n_I will notify the administrator about it._",
            "uz": "*Bundan judayam afsusdaman!*\n\n_Bu haqida administratorni xabar beraman._",
            "ru": "*Мне очень жаль показывать это сообщение!*\n\n_Я сообщу об этом администратору._"
        },
        "21": {
            "en": "No, it is wrong",
            "uz": "Yo'q, bu xato",
            "ru": "Нет, это неправильно"
        },
        "22": {
            "en": "*Warning*\n\n_This message is found to be spam by the reciever._\nYou are warned not to send such annoying/discriminating messages again!\n\n*Too many warnings may result to be permanently blocked.*",
            "uz": "*Ogohlantirish*\n\n_Ushbu xabar qabul qiluvchi tomonidan spam deb topildi._\nSizni bunday haqoratli/kamsituvchi xabarlarni boshqa yubormaslik haqida ogohlantirilaman!\n\n*Juda koʻp ogohlantirishlar butunlay bloklanishiga olib kelishi mumkin.*",
            "ru": "*Предупреждение*\n\n_Получатель считает это сообщение спамом._\nВас предупреждают, чтобы вы больше не отправляли такие раздражающие/дискриминирующие сообщения!\n\n*Слишком много предупреждений может привести к постоянной блокировке.*"
        },
        "23": {
            "en": "*User is blocked!*\n\n*Note:*\n_Previously blocked users are unblocked right now._",
            "uz": "*Foydalanuvchi bloklandi!*\n\n*Eslatma:*\n_Avval bloklangan foydalanuvchilar hozir blokdan chiqariladi._",
            "ru": "*Пользователь заблокирован!*\n\n*Примечание:*\n_Ранее заблокированные пользователи разблокируются прямо сейчас._"
        },
        "24": {
            "en": "_You do not have enough bonus points to redeem!_",
            "uz": "_Qoʻlga kiritish uchun bonus ballaringiz yetarli emas!_",
            "ru": "_У вас недостаточно бонусных баллов для использования!_"
        },
        "25": {
            "en": "_Send me the custom link you want to claim.\n\n*Once you submit it, please wait for the administrator's approval!*_",
            "uz": "_Olmoqchi bo'lgan maxsus so'zli havolangizni yozing.\n\n*Yuborib bo'lganingizdan so'ng administratorni javobini kuting!*_",
            "ru": "_Отправьте мне персонализированную ссылку, на которую вы хотите заявить права.\n\n*После отправки дождитесь одобрения администратора!*_"
        }

    }
    if data[0] == '0':
        cancel(user_id)
        params = {
            'chat_id': user_id,
            'message_id': message_id,
            'text': f"ℹ️ *{t.get('1').get(lan, t.get('1').get('en'))}*",
            'parse_mode': 'Markdown'
        }
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
            params=params
        )
    elif data[0] == 'C':
        actual_message = '\n'.join(text.split('\n')[2:])
        cancel(user_id)
        params = {
            'chat_id': user_id,
            'message_id': message_id,
            'text': f"ℹ️ *{t.get('1').get(lan, t.get('1').get('en'))} {t.get('2').get(lan, t.get('2').get('en'))}*\n\n{actual_message}",
            'parse_mode': 'Markdown'
        }
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
            params=params
        )
    elif data[0] == 'R':
        actual_message = '\n'.join(text.split('\n')[2:])
        query = {"id": user_id}
        update = {
            "$set":
                {
                    "to": int(data[1:].split()[0]),
                    "previous": int(data[1:].split()[1])
                }
        }
        database_update(query, update)

        if database_search({"id": user_id})["premium"]:
            reply_markup = {
                'inline_keyboard':
                    [[{'text': f"{t.get('3').get(lan, t.get('3').get('en'))}", 'callback_data': f"P{data[1:].split()[1]} {data[1:].split()[0]}"}],
                     [{'text': f"{t.get('5').get(lan, t.get('5').get('en'))}", 'callback_data': "C"}]]
            }
            params = {
                'chat_id': user_id,
                'message_id': message_id,
                'text': f"🔁 *{t.get('4').get(lan, t.get('4').get('en'))}*\n\n{actual_message}",
                # based on the 'you have a new reply'
                'reply_markup': json.dumps(reply_markup),
                'parse_mode': 'Markdown'
            }
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                params=params
            )
        else:
            reply_markup = {
                'inline_keyboard': [[{'text': f"{t.get('5').get(lan, t.get('5').get('en'))}", 'callback_data': "C"}]]
            }
            params = {
                'chat_id': user_id,
                'message_id': message_id,
                'text': f"🔁 *{t.get('4').get(lan, t.get('4').get('en'))}*\n\n{actual_message}",
                'reply_markup': json.dumps(reply_markup),
                'parse_mode': 'Markdown'
            }
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                params=params
            )
    elif data[0] == 'P': # message_id, user_id
        actual_message = '\n'.join(text.split('\n')[2:])
        user = database_search({"id": user_id})
        if user["coins"] > 0:
            query = {"id": user_id}
            update = {"$set": {"coins": user["coins"] - 1}}
            database_update(query, update)
            #updated_message = f"😔 <strong>{t.get('8').get(lan, t.get('8').get('en'))}</strong>"
            updated_message = database_search({"id": int(data[1:].split()[1])})
            reply_markup = {
                'inline_keyboard': [[{'text': f"{t.get('6').get(lan, t.get('6').get('en'))}", 'callback_data': f"R{data[1:].split()[1]} {data[1:].split()[0]}"}],
                                    [{'text': f"{t.get('5').get(lan, t.get('5').get('en'))}",'callback_data': "C"}]]
            }
            params = {
                'chat_id': int(user_id),
                'message_id': int(message_id),
                'text': f"✍️ <strong>{t.get('9').get(lan, t.get('9').get('en'))}</strong> {updated_message}<strong>{t.get('17').get(lan, t.get('17').get('en'))} ☄️ {user['coins'] - 1}</strong>\n\n{actual_message}",
                'reply_markup': json.dumps(reply_markup),
                'parse_mode': 'HTML'
            }
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                params=params
            )

        else:
            reply_markup = {
                'inline_keyboard':
                    [[{'text': f"{t.get('6').get(lan, t.get('6').get('en'))}", 'callback_data': f"R{data[1:].split()[1]} {data[1:].split()[0]}"}],
                    [{'text': f"{t.get('5').get(lan, t.get('5').get('en'))}", 'callback_data': "C"}]]
            }
            params = {
                'chat_id': int(user_id),
                'message_id': int(message_id),
                'text': f"😔 <strong>{t.get('7').get(lan, t.get('7').get('en'))}</strong>\n\n{actual_message}",
                'reply_markup': json.dumps(reply_markup), 'parse_mode': 'HTML'}
            requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
                params=params
            )
    elif data[0] == 'B':
        query = {"id": user_id}
        update = {"$set": {"block": data[1:]}}
        database_update(query, update)
    elif data[0] == 'F':
        query = {"id": user_id}
        update = {"$set": {"block": data[1:]}}
        database_update(query, update)
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',
            params={
                'chat_id': user_id,
                'message_id': message_id,
                'text': f"{t.get('23').get(lan, t.get('23').get('en'))}", 'parse_mode': 'Markdown'
            }
        )
        # here i will write what to do if the permanent block probably open another file for each user like blocklist
        # which will be different from the one written in block.txt
        # here i can make a premium feature like blocking many people at the same time
    elif data[0] == 'S':
        reply_markup = {
            'inline_keyboard':
                [[{'text': f"{t.get('6').get(lan, t.get('6').get('en'))}", 'callback_data': f"R{data[1:].split()[0]} {data[1:].split()[1]}"}],
                 [{'text': f"{t.get('5').get(lan, t.get('5').get('en'))}", 'callback_data': "C"}],
                 [{'text': f"{t.get('19').get(lan, t.get('19').get('en'))}",'callback_data': f"F{data[1:].split()[0]}"}]]
        }
        params = {
            'chat_id': int(user_id),
            'message_id': int(message_id),
            'text': f"😔 {t.get('20').get(lan, t.get('20').get('en'))}",
            'reply_markup': json.dumps(reply_markup),
            'parse_mode': 'Markdown'
        }
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
            params=params
        )
        reply_markup = {
            'inline_keyboard':
                [[{'text': f"{t.get('21').get(lan, t.get('21').get('en'))}", 'callback_data': 'admin'}]]
        }
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto',
            json={
                'chat_id': data[1:].split()[0],
                'photo': "https://raw.githubusercontent.com/Komil-jon/anonymous-chat/main/assets/spam.jpg",
                'caption': f"{t.get('22').get(lan, t.get('22').get('en'))}",
                'parse_mode': 'Markdown',
                'reply_markup': reply_markup,
                'reply_to_message_id':data[1:].split()[1]
            }
        )
        params = {
            'chat_id': GROUP,
            'from_chat_id': data[1:].split()[0],
            'message_id': data[1:].split()[1],
        }
        reply_id = requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage',
            json=params
        ).json()['result']['message_id']
        reply_markup = {
            'inline_keyboard':
                [[{'text': f"Block Permanently", 'callback_data': f'B{data[1:].split()[0]}'}]]
        }
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
            json={'chat_id': GROUP,
                  'text': f'Author ID: {data[1:].split()[0]}\nMessage ID: {data[1:].split()[1]}\nReciever ID: {user_id}',
                  'parse_mode': 'Markdown',
                  'reply_markup': reply_markup,
                  'reply_to_message_id': reply_id
            }
        )
    elif data == 'premium':
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage",
            json={
                'chat_id': user_id,
                'message_id': message_id
            }
        )
        invoice_payload = {
            'chat_id': user_id,
            'title': f"{t.get('14').get(lan, t.get('14').get('en'))}",
            'description': f"🔥 {t.get('10').get(lan, t.get('10').get('en'))} 🔐",
            'payload': 'payload',
            'provider_token': PAYMENT_TOKEN,
            'start_parameter': 'start_parameter',
            'currency': 'UZS',
            'prices': json.dumps([{'label': f"{t.get('11').get(lan, t.get('11').get('en'))}", 'amount': 1000000}]),
            'max_tip_amount': 1000000000,
            'suggested_tip_amounts': [100000, 200000, 300000, 400000]
        }
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendInvoice",
            json=invoice_payload
        )
    elif data == 'admin':
        params = {
            'chat_id': user_id,
            'message_id': message_id,
            'caption': f"🫴 *{t.get('18').get(lan, t.get('18').get('en'))}*", 'parse_mode': 'Markdown'
        }
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageCaption",
            params=params
        )
        query = {"id": user_id}
        update = {"$set": {"to": ADMIN, "previous": None}}
        database_update(query, update)
    elif data == 'cancel':
        cancel(user_id)
        edit_params = {
            'chat_id': user_id,
            'message_id': message_id,
            'media': json.dumps({
                'type': 'photo',
                'media': "https://raw.githubusercontent.com/Komil-jon/anonymous-chat/main/assets/not_report.jpg",
                'caption': f"ℹ️ *{t.get('1').get(lan, t.get('1').get('en'))}*",
                'parse_mode': 'Markdown',
                }
            )
        }
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageMedia",
            params=edit_params
        )
    elif data == 'redeem':
        user = database_search({"id": user_id})
        if user["referral"] >= 10:
            requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageCaption',
                params={
                    'chat_id': user_id,
                    'message_id': message_id,
                    'caption': f"{t.get('25').get(lan, t.get('25').get('en'))}",
                    'parse_mode': 'Markdown'
                }
            )
            query = {"id": user_id}
            update = {"$set": {"to": ADMIN}}
            database_update(query, update)

        else:
            requests.post(
                f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageCaption',
                params={
                    'chat_id': user_id,
                    'message_id': message_id,
                    'caption': f"{t.get('24').get(lan, t.get('24').get('en'))}",
                    'parse_mode': 'Markdown'
                }
            )

    elif data == 'not':
        edit_media_params = {
            'chat_id': user_id,
            'message_id': message_id,
            'media': json.dumps({
                'type': 'photo',
                'media': "https://raw.githubusercontent.com/Komil-jon/anonymous-chat/main/assets/reject.jpg",
                'caption': f"👌 *{t.get('12').get(lan, t.get('12').get('en'))}*",
                'parse_mode': 'Markdown'
            }),
        }
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageMedia",
            params=edit_media_params
        )
    elif data == 'buy':
        reply_markup = {'inline_keyboard': [[{'text': '1 Galacoins = 1000.00 UZS', 'callback_data': '.'}],
                                            [{'text': '5 Galacoins = 4500.00 UZS', 'callback_data': '?'}],
                                            [{'text': '10 Galacoins = 8000.00 UZS', 'callback_data': '!'}],
                                            [{'text': '20 Galacoins = 15000.00 UZS', 'callback_data': '&'}],
                                            [{'text': "Report & Reward", 'callback_data': 'admin'}]]}
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageCaption',
            params={
                'chat_id': user_id,
                'message_id': message_id,
                'caption': f"{t.get('13').get(lan, t.get('13').get('en'))}",
                'parse_mode': 'Markdown',
                'reply_markup': json.dumps(reply_markup)
            }
        )
    elif data == '.' or data == '?' or data == '!' or data == '&':
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage",
            json={
                'chat_id': user_id,
                'message_id': message_id
            }
        )
        if data == '.':
            amount = '100000'
            count = 1
        elif data == '?':
            amount = '450000'
            count = 5
        elif data == '!':
            amount = '800000'
            count = 10
        else:
            amount = '1500000'
            count = 20
        invoice_payload = {
            'chat_id': user_id,
            'title': f"{t.get('14').get(lan, t.get('14').get('en'))}",
            'description': f"{t.get('15').get(lan, t.get('15').get('en'))} ☄️",
            'payload': 'payload',
            'provider_token': PAYMENT_TOKEN,
            'start_parameter': 'start_parameter',
            'currency': 'UZS',
            'prices': json.dumps([{'label': f"{count} Galacoins ☄️", 'amount': amount}]),
            'max_tip_amount': 1000000000,
            'suggested_tip_amounts': [100000, 200000, 300000, 400000]
        }
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendInvoice",
            json=invoice_payload
        )
    elif len(data) >= 2 and data[1].isdigit():
        params = {
            'chat_id': user_id,
            'message_id': message_id,
            'text': f"🫴 *{t.get('16').get(lan, t.get('16').get('en'))}*",
            'parse_mode': 'Markdown'
        }
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText",
            params=params
        )
        query = {"id": int(user_id)}
        update = {"$set": {"to": data, "previous": None}}
        database_update(query, update)
    else:
        print('Uncatched callback query')
        return
    return


def inline(user_id, text, query_id):
    t = {
        "1": {
            "en": "Write a message. Then click me!",
            "uz": "Xabar yozing. So'ng menga bosing!",
            "ru": "Напиши сообщение. Затем кликните меня!"
        },
        "2": {
            "en": "_Click the link below to chat with me anonymously._",
            "uz": "_Men bilan anonim suhbatlashish uchun quyidagi havolani bosing._",
            "ru": "_Нажмите на ссылку ниже, чтобы поговорить со мной анонимно._"
        }
    }
    results = [
        {'type': 'article',
         'id': '1',
         'title': f"{t.get('1').get(lan, t.get('1').get('en'))}",
         'input_message_content': {
             'message_text': f"{t.get('2').get(lan, t.get('2').get('en'))}\n[{text}](t.me/anonym_xbot?start={user_id})",
             'parse_mode': 'Markdown',
             'disable_web_page_preview': True
            }
         }
    ]
    requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/answerInlineQuery',
        json={
            'inline_query_id': query_id,
            'results': results,
            'cache_time': 0
        }
    )

def cancel(user_id):
    query = {"id": user_id}
    update = {"$set": {"to": None}}
    database_update(query, update)

def commands(user_id, text):
    t = {
        "1": {
            "en": "Choose:",
            "uz": "Tanlang:",
            "ru": "Выберите:"
        },
        "2": {
            "en": "You cancelled the conversation!",
            "uz": "Siz suhbatni bekor qildingiz!",
            "ru": "Вы отменили разговор!"
        }
    }

    if text == '/cancel':
        cancel(user_id)
        requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
            params={
                'chat_id': user_id,
                'text': f"ℹ️ *{t.get('2').get(lan, t.get('2').get('en'))}*",
                'parse_mode': 'Markdown'
            }
        )
    elif text == '/help' or text == "Manual" or text == "Qo'llanma" or text == "Руководство":
        help(user_id)
    elif text == '/show' or text == 'My link' or text == "Mening havolam" or text == "Моя ссылка":
        show(user_id)
    elif text == '/premium' or text == 'Premium 🎁' or text == "Премиум 🎁":
        premium_features(user_id)
    elif text == '/report' or text == 'Feedback' or text == "Fikr-mulohaza" or text == "Обратная связь":
        report(user_id)
    elif text == '/policy' or text == 'Policy' or text == "Siyosat" or text == "Политика":
        zero_trust(user_id)
    elif text == '/menu':
        menu(user_id, f"*{t.get('1').get(lan, t.get('1').get('en'))}*")
    elif text == 'Coins 🎁' or text == "Tangalar 🎁" or text == "Монеты 🎁":
        coins(user_id)
    elif text == 'Bonus 🔥' or text == 'Бонус 🔥' or text == '/bonus':
        bonus(user_id)


def menu(user_id, text):
    if not database_search({"id": user_id})["premium"]:
        t = {
            "en": ["My link", "Premium 🎁", "Policy", "Manual", "Feedback", "Bonus 🔥"],
            "uz": ["Mening havolam", "Premium 🎁", "Siyosat", "Qo'llanma", "Fikr-mulohaza", "Bonus 🔥"],
            "ru": ["Моя ссылка", "Премиум 🎁", "Политика", "Руководство", "Обратная связь", "Бонус 🔥"]
        }
        options = t.get(lan, t.get('en'))
    else:
        t = {
            "en": ["My link", "Coins 🎁", "Policy", "Manual", "Feedback", "Bonus 🔥"],
            "uz": ["Mening havolam", "Tangalar 🎁", "Siyosat", "Qo'llanma", "Fikr-mulohaza", "Bonus 🔥"],
            "ru": ["Моя ссылка", "Монеты 🎁", "Политика", "Руководство", "Обратная связь", "Бонус 🔥"]
        }
        options = t.get(lan, t.get('en'))
    keyboard = {
        'keyboard': [
            options[:3],
            options[3:]
        ],
        'one_time_keyboard': False,
        'resize_keyboard': True
    }
    data = {
        'chat_id': user_id,
        'text': text,
        'reply_markup': json.dumps(keyboard),
        'parse_mode': 'Markdown'
    }
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        data=data
    )


def bonus(user_id):
    t = {
        "1": {
            "en": "_The number of bonus points:_",
            "uz": "_Sizdagi bonuslar soni:_",
            "ru": "_Количество бонусных баллов:_"
        },
        "2": {
            "en": "Use",
            "uz": "Ishlatish",
            "ru": "Использовать"
        },
        "3": {
            "en": "What you can do with Bonus points?\n1) You can convert them into Galacoins ☄️.\n2) You can earn more bonus points by pressing the share button.♨️\n\n*2 Bonus points = 1 Galacoin.*\n_To get Galacoins press Use and describe briefly how much Galacoins you need._",
            "uz": "Bonus ballari bilan nima qilish mumkin?\n1) Siz ularni Galakoynlarga aylantirishingiz mumkin ☄️.\n2) Ulashish tugmasini bosish orqali koʻproq bonus ball olishingiz mumkin.♨️\n\n*2 Bonus ball = 1 Galakoyn.*\n_Galakoynlar olish uchun Ishlatish tugmasini bosing va sizga qancha Galakoyn kerakligini qisqacha tavsiflab bering._",
            "ru": "Что вы можете делать с бонусными баллами?\n1) Вы можете конвертировать их в галакоины ☄️.\n2) Вы можете заработать больше бонусных баллов, нажав кнопку Поделиться.♨️\n\n*2 Бонусных балла = 1 Галакоин.*\n_Чтобы получить Галакоины, нажмите Использовать и кратко опишите, сколько галакоинов вам нужно._"
        },
        "4": {
            "en": "Share",
            "uz": "Tarqatish",
            "ru": "Поделиться"
        },
        "5": {
            "en": "Send me anonymous messages.",
            "uz": "Menga anonim xabarlar yuboring.",
            "ru": "Отправьте мне анонимные сообщения."
        },
        "6": {
            "en": "What you can do with Bonus points?\n_When you have 10 bonus point you can get a custom link._",
            "uz": "Bonus ballari bilan nima qilish mumkin?\n_Agar sizda 10 bonus ball bo'lsa, siz maxsus havola olishingiz mumkin._",
            "ru": "Что вы можете делать с бонусными баллами?\n_Когда у вас есть 10 бонусных баллов, вы можете получить персонализированную ссылку._"
        }
    }
    user = database_search({"id": user_id})
    reply_markup = {
        'inline_keyboard':
            [[{'text': f"{t.get('4').get(lan, t.get('4').get('en'))}", 'switch_inline_query': f"{t.get('5').get(lan, t.get('5').get('en'))}"}],
             [{'text': f"{t.get('2').get(lan, t.get('2').get('en'))}", 'callback_data': 'redeem'}]]
    }
    if user["premium"]:
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto',
            json={'chat_id': user_id,
                  'photo': "https://raw.githubusercontent.com/Komil-jon/anonymous-chat/main/assets/bonus.jpg",
                  'caption': f"{t.get('1').get(lan, t.get('1').get('en'))} *{user['referral']}*\n\n{t.get('3').get(lan, t.get('3').get('en'))}",
                  'parse_mode': 'Markdown',
                  'reply_markup': reply_markup,
                  'disable_web_page_preview': True
            }
        )
    else:
        requests.post(
            f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto',
            json={'chat_id': user_id,
                  'photo': "https://raw.githubusercontent.com/Komil-jon/anonymous-chat/main/assets/bonus.jpg",
                  'caption': f"{t.get('1').get(lan, t.get('1').get('en'))} *{user['referral']}*\n\n{t.get('6').get(lan, t.get('6').get('en'))}",
                  'parse_mode': 'Markdown',
                  'reply_markup': reply_markup,
                  'disable_web_page_preview': True
            }
        )


def coins(user_id):
    t = {
        "1": {
            "en": "Buy more",
            "uz": "Ko'proq sotib olish",
            "ru": "Купить еще"
        },
        "2": {
            "en": "You have",
            "uz": "Sizdagi ☄️ Galakoynlar soni",
            "ru": "У вас есть"
        },
        "3": {
            "en": "Galacoins ☄️",
            "uz": "",
            "ru": "Галакоинов ☄️"
        }
    }
    user = database_search({"id": user_id})
    reply_markup = {
        'inline_keyboard':
            [[{'text': f"{t.get('1').get(lan, t.get('1').get('en'))}", 'callback_data': 'buy'}]]
    }
    requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto',
        json={
            'chat_id': user_id,
            'photo': 'https://raw.githubusercontent.com/Komil-jon/anonymous-chat/main/assets/coins.jpg',
            'caption': f"*{t.get('2').get(lan, t.get('2').get('en'))} {user['coins']} {t.get('3').get(lan, t.get('3').get('en'))}.*",
            'parse_mode': 'Markdown',
            'reply_markup': reply_markup
        }
    )


def report(user_id):
    t = {
        "1": {
            "en": "Report",
            "uz": "Xabar berish",
            "ru": "Сообщить"
        },
        "2": {
            "en": "Cancel",
            "uz": "Bekor qilish",
            "ru": "Отмена"
        },
        "3": {
            "en": "*Disclaimer:* This is an anonymous chat platform. If you are reporting an issue with the bot or need assistance, please provide details about the problem. Avoid sharing any sensitive or personal information in this chat.",
            "uz": "*Ogohlantirish:* Bu anonim chat platformasi. Agar sizda bot bilan muammo bo'lsa yoki yordam kerak bo'lsa, iltimos, muammo haqida batafsil xabar bering. Ushbu chatda sirli yoki shaxsiy ma'lumotlarni hech kim bilan ulashmang.",
            "ru": "*Отказ от ответственности:* Это анонимная чат-платформа. Если вы сообщаете о проблеме с ботом или вам нужна помощь, предоставьте подробную информацию о проблеме. Не делитесь конфиденциальной или личной информацией в этом чате."
        }
    }
    reply_markup = {
        'inline_keyboard': [
            [{'text': f"{t.get('1').get(lan, t.get('1').get('en'))}", 'callback_data': 'admin'}],
            [{'text': f"{t.get('2').get(lan, t.get('2').get('en'))}", 'callback_data': 'cancel'}]
        ]
    }
    requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto',
        json={
            'chat_id': user_id,
            'photo': "https://raw.githubusercontent.com/Komil-jon/anonymous-chat/main/assets/report.jpg",
            'caption': f"⚠️ {t.get('3').get(lan, t.get('3').get('en'))}\n\n",
            'parse_mode': 'Markdown',
            'reply_markup': reply_markup
        }
    )


def zero_trust(user_id):
    t = {
        "en": "🔒 *Zero Trust Policy* 🔒\n\n"
              "We believe in 100% transparency and privacy. Here's why you can trust our project:\n\n"
              "🌐 *Open Source:* This project is 100% open source. You can review the code on GitHub.\n"
              "🔐 *Privacy Guaranteed:* We do not share any user data with third parties. Your privacy is our top priority.\n"
              "🚫 *No Ads:* This platform is ad-free. We are committed to providing a clean and uninterrupted experience.\n"
              "🤝 *Community-Focused:* Created for the community, by the community. Your feedback and suggestions matter!\n\n"
              "Feel free to explore and enjoy the platform. If you have any questions or concerns, let us know! 🚀",

        "uz": "🔒 *Zero Trust Policy* 🔒\n\n"
              "Biz 100% ochiqlik va maxfiylikka ishonamiz. Bu yerda nima uchun bizning loyihamizga ishonishingiz mumkinligi ko'rsatilgan:\n\n"
              "🌐 *Ochiq Manba:* Bu loyiha manbasi ommaga 100% ochiq. Siz uni GitHub-da kodni ko'ra olishingiz mumkin.\n"
              "🔐 *Maxfiylik Kafolati:* Biz foydalanuvchilar ma'lumotlarini uchinchi shaxslarga bermaymiz. Sizning maxfiylikingiz bizning asosiy tamoyilimiz.\n"
              "🚫 *Reklama Yo'q:* Bu platformada hech qanday reklama yo'q. Biz siznihar kunlik yoqimsiz reklamalar bilan be'zovta qilmaymiz.\n"
              "🤝 *Jamoatga Qaratilgan:* Bu loyiha jamoat uchun va jamoat tomonidan yaratilgan. Sizning shikoyat va takliflaringiz muhimdir!\n\n"
              "Platformani be'malol kuzatib o'ranib chiqishingiz mumkin. Agar savolingiz yoki takliflaringiz bo'lsa, bizga murojaat qiling! 🚀",

        "ru": "🔒 *Политика нулевого доверия* 🔒\n\n"
              "Мы верим в 100% прозрачность и конфиденциальность. Вот почему вы можете доверять нашему проекту:\n\n"
              "🌐 *Открытый исходный код:* Этот проект на 100% открыт. Вы можете просмотреть код на GitHub.\n"
              "🔐 *Гарантированная конфиденциальность:* Мы не передаем пользовательские данные третьим сторонам. Ваша конфиденциальность - наш главный приоритет.\n"
              "🚫 *Без рекламы:* Эта платформа не содержит рекламы. Мы стремимся обеспечить чистый и бесперебойный опыт.\n"
              "🤝 *Ориентирована на сообщество:* Создана для сообщества, сообществом. Ваше мнение и предложения имеют значение!\n\n"
              "Не стесняйтесь исследовать и наслаждаться платформой. Если у вас есть вопросы или заботы, дайте нам знать! 🚀"
    }
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
        data={
            'chat_id': user_id,
            'caption': f"{t.get(lan, t.get('en'))}",
            'parse_mode': 'Markdown',
            'photo': "https://raw.githubusercontent.com/Komil-jon/anonymous-chat/main/assets/policy.jpg"
        }
    )


def premium_features(user_id):
    t = {
        "en": "🌟 Premium Features 🌟\n\n"
              "Upgrade to our Premium plan to enjoy exclusive benefits:\n\n"
              "✨ *Custom Link*: Get a personalized link instead of an ID number!\n"
              "✉️ *Custom Name*: Change your name for the platform!\n"
              "🤫 *Secret Feature*: _Hidden description_\n\n"
              "*♨️Purchase once - Enjoy forever♨️* _(The premium plan is forever!)_\n\n"
              "Ready to elevate your experience? Upgrade now! 💎",

        "uz": "🌟 Premium re'janing afzalliklari 🌟\n\n"
              "Eksklyuziv imkoniyat va afzalliklardan foydalanish uchun bizning Premium re'jamizga o'ting:\n\n"
              "✨ *Shaxsiy Havola*: ID raqami o'rnida siz xohlagan so'z qo'ying!\n"
              "✉️ *Shaxsiy Ism*: Platforma uchun ismingizni o'zgartiring!\n"
              "🤫 *Sirli imkoniyat*: _Yashirin tavsif_\n\n"
              "*♨️Bir marta sotib oling - Doimiy ishlating♨️* _(Bizda Premium re'ja doimiy!)_\n\n"
              "Cheksiz imkoniyatlardan foydalanishga tayyormisiz? Hoziroq Premium foydalanuvchilar qatoriga kiring! 💎",

        "ru": "🌟 Преимущества Премиум 🌟\n\n"
              "Перейдите на наш Премиум-план, чтобы насладиться эксклюзивными преимуществами:\n\n"
              "✨ Пользовательская ссылка: Получите персональную ссылку вместо номера ID!\n"
              "✉️ Пользовательское имя: Измените свое имя на платформе!\n"
              "🤫 Секретная функция: Скрытое описание\n\n"
              "♨️Покупайте один раз - Наслаждайтесь вечно♨️ (Премиум-план навсегда!)\n\n"
              "Готовы улучшить свой опыт? Обновитесь сейчас! 💎"
    }
    a = {
        "1": {
            "en": "Become a premium user",
            "uz": "Premium foydalanuvchi bo'lish",
            "ru": "Станьте премиум-пользователем"
        },
        "2": {
            "en": "Not for now",
            "uz": "Hozircha emas",
            "ru": "Не сейчас"
        }
    }

    params = {
        'chat_id': user_id,
        'text': f"{t.get(lan, t.get('en'))}",
        'parse_mode': 'Markdown',
        'reply_markup': {
            'inline_keyboard': [
                [{'text': f"{a.get('1').get(lan, a.get('1').get('en'))}", 'callback_data': 'premium'}],
                [{'text': f"{a.get('2').get(lan, a.get('2').get('en'))}", 'callback_data': 'not'}],
            ]
        }
    }

    requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto',
        json={
            'chat_id': user_id,
            'photo': 'https://raw.githubusercontent.com/Komil-jon/anonymous-chat/main/assets/premium.jpg',
            'caption': params['text'],
            'parse_mode': 'Markdown',
            'reply_markup': params['reply_markup']
        }
    )


def help(user_id):
    t = {
        "1": {
            "en": "Welcome to the Anonymous Chat Bot!",
            "uz": "Anonim Chat Botiga xush kelibsiz!",
            "ru": "Добро пожаловать в Anonymous Chat Bot!"
        },
        "2": {
            "en": "Here are some commands you can use:",
            "uz": "Ishlatishingiz mumkin bo'lgan ba'zi buyruqlar:",
            "ru": "Вот несколько команд, которые вы можете использовать:"
        },
        "3": {
            "en": "/start - Restart and update the bot",
            "uz": "/start - Botni qayta ishga tushirish va yangilash",
            "ru": "/start - Перезапустите и обновите бота."
        },
        "4": {
            "en": "/show - Display your unique link for receiving anonymous messages",
            "uz": "/show - Sizning xabarlar qabul qilishingiz uchun havolangizni ko'rsatish",
            "ru": "/show - Показать вашу уникальную ссылку для получения анонимных сообщений"
        },
        "5": {
            "en": "/cancel - Cancel the current conversation",
            "uz": "/cancel - Hozirgi suhbatni bekor qilish",
            "ru": "/cancel - Отменить текущий разговор"
        },
        "6": {
            "en": "/help - Display this help message",
            "uz": "/help - Manashu xabarni ko'rsatish",
            "ru": "/help - Показать это справочное сообщение"
        },
        "7": {
            "en": "/premium - Learn about premium features",
            "uz": "/premium - Premium imkoniyatlar haqida bilib olish",
            "ru": "/premium - Узнать о премиальных функциях"
        },
        "8": {
            "en": "/menu - Display the main menu",
            "uz": "/menu - Asosiy menyuni ko'rsatish",
            "ru": "/menu - Показать главное меню"
        },
        "9": {
            "en": "/report - Report an issue or provide feedback",
            "uz": "/report - Muammo haqida xabar berish yoki fikr bildirish",
            "ru": "/report - Сообщить о проблеме или предоставить обратную связь"
        },
        "10": {
            "en": "/policy - Learn why you can trust this project",
            "uz": "/policy - Nima uchun aynan bizga ishonishingiz mumkin ekanligi haqida batafsil bilish",
            "ru": "/policy - Узнать, почему вы можете доверять этому проекту"
        }
    }
    requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto',
        data={
            'chat_id': user_id,
            'caption': f"<strong>{t.get('1').get(lan, t.get('1').get('en'))}</strong>\n\n<em>{t.get('2').get(lan, t.get('2').get('en'))}</em>\n\n{t.get('3').get(lan, t.get('3').get('en'))}\n{t.get('4').get(lan, t.get('4').get('en'))}\n{t.get('5').get(lan, t.get('5').get('en'))}\n{t.get('6').get(lan, t.get('6').get('en'))}\n{t.get('7').get(lan, t.get('7').get('en'))}\n{t.get('8').get(lan, t.get('8').get('en'))}\n{t.get('9').get(lan, t.get('9').get('en'))}\n{t.get('10').get(lan, t.get('10').get('en'))}\n",
            'parse_mode': 'HTML',
            'photo': 'https://raw.githubusercontent.com/Komil-jon/anonymous-chat/main/assets/help.jpg'
        }
    )


def show(user_id):
    t = {
        "1": {
            "en": "Your link:",
            "uz": "Sizning havolangiz:",
            "ru": "Ваша ссылка:"
        },
        "2": {
            "en": "Your custom link:",
            "uz": "Sizning tanlangan havolangiz:",
            "ru": "Ваша персонализированная ссылка:"
        },
        "3": {
            "en": "Press the button to share your link with others. So that, they can chat with you anonymously.",
            "uz": "Sizning havolangizni boshqalarga yuborish uchun quyidagi tugmani bosing. Shunda ular siz bilan anonim suhbat qura oladilar.",
            "ru": "Нажмите кнопку, чтобы поделиться ссылкой с другими. Чтобы они могли общаться с вами анонимно."
        },
        "4": {
            "en": "Share",
            "uz": "Tarqatish",
            "ru": "Поделиться"
        },
        "5": {
            "en": "Send me anonymous messages.",
            "uz": "Menga anonim xabarlar yuboring.",
            "ru": "Отправьте мне анонимные сообщения."
        }
    }
    user = database_search({"id": user_id})
    if user["premium"]:
        text = f"*{t.get('1').get(lan, t.get('1').get('en'))}*\n`t.me/anonym_xbot?start={user_id}`\n\n*{t.get('2').get(lan, t.get('2').get('en'))}*\n`t.me/anonym_xbot?start={user['nick']}`\n\n*{t.get('3').get(lan, t.get('3').get('en'))}*"
    else:
        text = f"*{t.get('1').get(lan, t.get('1').get('en'))}*\n`t.me/anonym_xbot?start={user_id}`\n\n*{t.get('3').get(lan, t.get('3').get('en'))}*"
    reply_markup = {
        'inline_keyboard':
            [[{'text': f"{t.get('4').get(lan, t.get('4').get('en'))}", 'switch_inline_query': f"{t.get('5').get(lan, t.get('5').get('en'))}"}]]
    }
    requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto',
        json={
            'chat_id': user_id,
            'photo': "https://raw.githubusercontent.com/Komil-jon/anonymous-chat/main/assets/link.jpg",
            'caption': text,
            'parse_mode': 'Markdown',
            'reply_markup': reply_markup,
            'disable_web_page_preview': True
        }
    )


def alert(user):
    params = {
        'chat_id': ADMIN,
        'text': "<strong>NEW MEMBER!!!\n</strong>" + user,
        'parse_mode': 'HTML',
    }
    requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
        params=params
    )

def make_premium(text):
    query = {"id": int(text.split()[1])}
    update = {
        "$inc": {"referral": -10},
        "$set": {"nick": text.split()[2], "premium": True}
    }
    database_update(query, update)
    params = {
        'chat_id': ADMIN,
        'text': "<strong>Done!</strong>",
        'parse_mode': 'HTML',
    }
    requests.post(
        f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
        params=params
    )
def database_search(query):
    connection_string = f"mongodb+srv://{USERNAME}:{PASSWORD}@core.pur20xh.mongodb.net/?appName=Core"
    client = MongoClient(connection_string)
    db = client['anonymous']
    collection = db['users']
    return collection.find_one(query)

def database_insert(record):
    connection_string = f"mongodb+srv://{USERNAME}:{PASSWORD}@core.pur20xh.mongodb.net/?appName=Core"
    client = MongoClient(connection_string)
    db = client['anonymous']
    collection = db['users']
    collection.insert_one(record)

def database_update(query, update):
    connection_string = f"mongodb+srv://{USERNAME}:{PASSWORD}@core.pur20xh.mongodb.net/?appName=Core"
    client = MongoClient(connection_string)
    db = client['anonymous']
    collection = db['users']
    return collection.update_one(query, update).matched_count


if __name__ == '__main__':
    #testing()
    app.run(debug=False)
