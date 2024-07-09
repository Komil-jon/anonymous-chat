from flask import Flask, request
import requests
import base64
import json
import io
import os

BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN = os.getenv('ADMIN')
GROUP = os.getenv('GROUP')
USERNAME = os.getenv('USERNAME')
PASSWORD = os.getenv('PASSWORD')
PAYMENT_TOKEN = os.getenv('PAYMENT_TOKEN')
GIT_TOKEN = os.getenv('GIT_TOKEN')
USER = os.getenv('USER')
REPO = os.getenv('REPO')
BRANCH = os.getenv('BRANCH')


global lan
# global last_update_id
# only for testing 👆
lan = 'en'

COMMANDS = ['/help', '/show', '/cancel', '/premium', '/report', '/policy', '/menu', '/bonus', 'Manual', "Qo'llanma",
            "Руководство", 'My link', "Mening havolam", "Моя ссылка", 'Premium 🎁', "Премиум 🎁", 'Feedback',
            "Fikr-mulohaza", "Обратная связь", 'Policy', "Siyosat", "Политика", 'Coins 🎁', "Tangalar 🎁", "Монеты 🎁",
            "Bonus 🔥", "Бонус 🔥"]

app = Flask(__name__)


@app.route('/', methods=['POST'])
def handle_webhook():
    try:
        process(json.loads(request.get_data()))
        return 'Success!'
    except Exception as e:
        print('error was:', e, json.loads(request.get_data()))
        return '-1'

@app.route('/activate', methods=['GET'])
def activate():
    return "Activation successful!", 200

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
            "ru": "Вы нажали на недействительную ссылку."
        }
    }
    # if it is /start
    if text == '/start':
        menu(user_id,
             f"👋 *{t.get('1').get(lan, t.get('1').get('en'))}* {first_name} ! *{t.get('2').get(lan, t.get('2').get('en'))}*")
        if not any(str(user_id) in line.split()[0] for line in open('users.txt')):
            with open('users.txt', 'a') as file:
                file.write(f"{user_id} N {first_name.split()[0]} {0}\n")
            file.close()
            with open('referral.txt', 'a') as file:
                file.write(f"{user_id} {0}\n")
            file.close()
            alert(json.dumps(user))
            git_update('users.txt')
            git_update('referral.txt')
        with open(f"{user_id}.txt", 'w') as file:
            file.write(' ')
        file.close()
        with open(f'{user_id}_block.txt', 'w') as file:
            file.write(' ')
        file.close()
        return
    # if it contains a referal link
    with open('users.txt') as file:
        lines = file.readlines()
        for line in lines:
            if text[7:] == line.split()[0] or text[7:] == line.split()[1]:
                if text[7:] == 'N':
                    break
                user_name = line.split()[2]
                send_id = line.split()[0]
                reply_markup = {'inline_keyboard': [
                    [{'text': f"{t.get('3').get(lan, t.get('3').get('en'))}", 'callback_data': f"{send_id}"}],
                    [{'text': f"{t.get('4').get(lan, t.get('4').get('en'))}", 'callback_data': f"{0}"}]]}
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', params={'chat_id': user_id,
                                                                                              'text': f"ℹ️ *{t.get('5').get(lan, t.get('5').get('en'))}* {user_name}\n",
                                                                                              'parse_mode': 'Markdown',
                                                                                              'reply_markup': json.dumps(
                                                                                                  reply_markup)})
                file.close()
                with open(f"{user_id}.txt", 'w') as file:
                    file.write(' ')
                file.close()
                with open(f'{user_id}_block.txt', 'w') as file:
                    file.write(' ')
                file.close()
                if not any(str(user_id) in line.split()[0] for line in open('users.txt')):
                    with open('users.txt', 'a') as file:
                        file.write(f"{user_id} N {first_name.split()[0]} {0}\n")
                    file.close()
                    # create fererral for the current user
                    with open('referral.txt', 'a') as file:
                        file.write(f"{user_id} {0}\n")
                    file.close()
                    # give credit to the owner of the referral
                    with open('referral.txt', 'r') as file:
                        lines = file.readlines()
                    newline = ' '
                    for line in lines:
                        if line.split()[0] == send_id:
                            newline = f"{line.split()[0]} {int(line.split()[1]) + 1}\n"
                            break
                    with open('referral.txt', 'w') as file:
                        if newline != ' ':
                            file.write(newline)
                        file.writelines([line for line in lines if f"{send_id}" not in line])
                    git_update('users.txt')
                    git_update('referral.txt')
                return
        file.close()
        menu(user_id,
             f"*{t.get('1').get(lan, t.get('1').get('en'))}* {first_name} ! {t.get('6').get(lan, t.get('6').get('en'))} 😔")


def message(user_id, message_id, text, message_from, update):
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
    try:
        with open(f"{user_id}.txt", 'r') as file:
            line = file.readline()
            if line == ' ':
                photo_params = {'chat_id': user_id,
                                'photo': 'AgACAgQAAxkBAAIuR2WuZvtoW63jd1ofW7wRHPUsCCenAALfwjEb_55wUW-rrK_j4J_5AQADAgADeQADNAQ',
                                'caption': f"🤷‍♂️ {t.get('1').get(lan, t.get('1').get('en'))}",
                                'parse_mode': 'Markdown'}
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', params=photo_params)
                return
            else:
                send_id = int(line.split()[0])
                with open(f"{send_id}_block.txt", 'r') as file:
                    if file.readline().strip() == str(user_id):
                        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                                      params={'chat_id': user_id,
                                              'text': f"ℹ️ {t.get('16').get(lan, t.get('16').get('en'))}",
                                              'parse_mode': 'Markdown'})
                        cancel(user_id)
                        return
                if line.split()[1] != 'N':
                    reply_id = int(line.split()[1])
                else:
                    reply_id = None
                with open('log.txt', 'a') as f:
                    f.write(
                        f"{message_id} <em>{t.get('10').get(lan, t.get('10').get('en'))}</em>{message_from.get('first_name', t.get('13').get(lan, t.get('13').get('en')))}, <em>{t.get('11').get(lan, t.get('11').get('en'))}</em>{message_from.get('id', t.get('13').get(lan, t.get('13').get('en')))}, <em>{t.get('12').get(lan, t.get('12').get('en'))}</em>{message_from.get('username', t.get('13').get(lan, t.get('13').get('en')))}\n")
                with open('database.txt', 'a') as f:
                    f.write(
                        f"{update.get('message').get('from').get('username', update.get('message').get('from').get('first_name'))} ({update.get('message').get('from').get('id')}) -> {send_id} = {text}\n")
                if user_id == send_id:
                    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', params={'chat_id': send_id,
                                                                                                  'text': f"ℹ️ *{t.get('2').get(lan, t.get('2').get('en'))}*",
                                                                                                  'parse_mode': 'Markdown'})
                    cancel(user_id)
                    return
                if is_premium(send_id) != ' ':
                    reply_markup = {'inline_keyboard': [[{'text': f"{t.get('3').get(lan, t.get('3').get('en'))}",
                                                          'callback_data': f"P{message_id} {user_id}"}], [
                                                            {'text': f"{t.get('4').get(lan, t.get('4').get('en'))}",
                                                             'callback_data': f"R{user_id} {message_id}"}], [
                                                            {'text': f"{t.get('15').get(lan, t.get('15').get('en'))}",
                                                             'callback_data': f"S{user_id} {message_id}"}]]}
                else:
                    reply_markup = {'inline_keyboard': [[{'text': f"{t.get('4').get(lan, t.get('4').get('en'))}",
                                                          'callback_data': f"R{user_id} {message_id}"}], [
                                                            {'text': f"{t.get('15').get(lan, t.get('15').get('en'))}",
                                                             'callback_data': f"S{user_id} {message_id}"}]]}
                status = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                                       params={'chat_id': send_id,
                                               'text': f"<strong>{t.get('5').get(lan, t.get('5').get('en'))}</strong> 🎯\n\n{text}",
                                               'parse_mode': 'HTML', 'reply_markup': json.dumps(reply_markup),
                                               'reply_to_message_id': reply_id}).status_code
                if (status == 200):
                    reply_markup = {'inline_keyboard': [
                        [{'text': f"{t.get('6').get(lan, t.get('6').get('en'))}", 'callback_data': f"{send_id}"}],
                        [{'text': f"{t.get('7').get(lan, t.get('7').get('en'))}", 'callback_data': f"{0}"}]]}
                    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', params={'chat_id': user_id,
                                                                                                  'text': f"✅ *{t.get('8').get(lan, t.get('8').get('en'))}*",
                                                                                                  'parse_mode': 'Markdown',
                                                                                                  'reply_markup': json.dumps(
                                                                                                      reply_markup)})
                else:
                    data = {'chat_id': user_id, 'text': f"😔 *{t.get('9').get(lan, t.get('9').get('en'))}*",
                            'parse_mode': 'Markdown'}
                    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data)
                cancel(user_id)
                git_update('log.txt')
                git_update('database.txt')
                return
    except Exception as e:
        photo_params = {'chat_id': user_id,
                        'photo': 'AgACAgIAAxkBAAIvQWWwyLNT4dqnXG5kibP4XhSTQwABMQAC-88xGzN5iUmJB5GrnpZcNQEAAwIAA20AAzQE',
                        'caption': f"{t.get('14').get(lan, t.get('14').get('en'))}", 'parse_mode': 'Markdown'}
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', params=photo_params)
        print(e)
    return


def media(user_id, message_id, message_from, update):
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
    try:
        with open(f"{user_id}.txt", 'r') as file:
            line = file.readline()
            if line == ' ':
                photo_params = {'chat_id': user_id,
                                'photo': 'AgACAgQAAxkBAAIuR2WuZvtoW63jd1ofW7wRHPUsCCenAALfwjEb_55wUW-rrK_j4J_5AQADAgADeQADNAQ',
                                'caption': f"🤷‍♂️ {t.get('1').get(lan, t.get('1').get('en'))}",
                                'parse_mode': 'Markdown'}
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', params=photo_params)
                return
            else:
                send_id = int(line.split()[0])
                with open(f"{send_id}_block.txt", 'r') as file:
                    if file.readline().strip() == str(user_id):
                        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                                      params={'chat_id': user_id,
                                              'text': f"ℹ️ {t.get('16').get(lan, t.get('16').get('en'))}",
                                              'parse_mode': 'Markdown'})
                        cancel(user_id)
                        return
                if line.split()[1] != 'N':
                    reply_id = int(line.split()[1])
                else:
                    reply_id = None
                with open('log.txt', 'a') as f:
                    f.write(
                        f"{message_id} <em>{t.get('10').get(lan, t.get('10').get('en'))}</em>{message_from.get('first_name', t.get('13').get(lan, t.get('13').get('en')))}, <em>{t.get('11').get(lan, t.get('11').get('en'))}</em>{message_from.get('id', t.get('13').get(lan, t.get('13').get('en')))}, <em>{t.get('12').get(lan, t.get('12').get('en'))}</em>{message_from.get('username', t.get('13').get(lan, t.get('13').get('en')))}\n")

                with open('database.txt', 'a') as f:
                    f.write(
                        f"{update.get('message').get('from').get('username', update.get('message').get('from').get('first_name'))} ({update.get('message').get('from').get('id')}) -> {send_id} = (media) {message_id}\n")
                if user_id == send_id:
                    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', params={'chat_id': send_id,
                                                                                                  'text': f"ℹ️ *{t.get('2').get(lan, t.get('2').get('en'))}*",
                                                                                                  'parse_mode': 'Markdown'})
                    cancel(user_id)
                    return
                forwarded_message_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage',
                                                     data={'chat_id': send_id, 'from_chat_id': user_id,
                                                           'message_id': message_id,
                                                           'reply_to_message_id': reply_id}).json()['result'][
                    'message_id']
                if is_premium(send_id) != ' ':
                    reply_markup = {'inline_keyboard': [[{'text': f"{t.get('3').get(lan, t.get('3').get('en'))}",
                                                          'callback_data': f"P{message_id} {user_id}"}], [
                                                            {'text': f"{t.get('4').get(lan, t.get('4').get('en'))}",
                                                             'callback_data': f"R{user_id} {message_id}"}], [
                                                            {'text': f"{t.get('14').get(lan, t.get('14').get('en'))}",
                                                             'callback_data': f"S{user_id} {message_id}"}]]}
                else:
                    reply_markup = {'inline_keyboard': [[{'text': f"{t.get('4').get(lan, t.get('4').get('en'))}",
                                                          'callback_data': f"R{user_id} {message_id}"}], [
                                                            {'text': f"{t.get('14').get(lan, t.get('14').get('en'))}",
                                                             'callback_data': f"S{user_id} {message_id}"}]]}
                status = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                                       params={'chat_id': send_id,
                                               'text': f"*{t.get('5').get(lan, t.get('5').get('en'))}* 🎯",
                                               'parse_mode': 'Markdown', 'reply_markup': json.dumps(reply_markup),
                                               'reply_to_message_id': forwarded_message_id}).status_code
                if status == 200:
                    reply_markup = {'inline_keyboard': [
                        [{'text': f"{t.get('6').get(lan, t.get('6').get('en'))}", 'callback_data': f"{send_id}"}],
                        [{'text': f"{t.get('7').get(lan, t.get('7').get('en'))}", 'callback_data': f"{0}"}]]}
                    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', params={'chat_id': user_id,
                                                                                                  'text': f"✅ *{t.get('8').get(lan, t.get('8').get('en'))}*",
                                                                                                  'parse_mode': 'Markdown',
                                                                                                  'reply_markup': json.dumps(
                                                                                                      reply_markup)})
                else:
                    data = {'chat_id': user_id, 'text': f"😔 {t.get('9').get(lan, t.get('9').get('en'))}",
                            'parse_mode': 'Markdown'}
                    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data)
                cancel(user_id)
                git_update('log.txt')
                git_update('database.txt')
                return
    except:
        photo_params = {'chat_id': user_id,
                        'photo': 'AgACAgIAAxkBAAIvQWWwyLNT4dqnXG5kibP4XhSTQwABMQAC-88xGzN5iUmJB5GrnpZcNQEAAwIAA20AAzQE',
                        'caption': f"{t.get('15').get(lan, t.get('15').get('en'))}", 'parse_mode': 'Markdown'}
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', params=photo_params)
    return


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
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", params=params)
    elif data[0] == 'C':
        actual_message = '\n'.join(text.split('\n')[2:])
        cancel(user_id)
        params = {
            'chat_id': user_id,
            'message_id': message_id,
            'text': f"ℹ️ *{t.get('1').get(lan, t.get('1').get('en'))} {t.get('2').get(lan, t.get('2').get('en'))}*\n\n{actual_message}",
            'parse_mode': 'Markdown'
        }
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", params=params)
    elif data[0] == 'R':
        actual_message = '\n'.join(text.split('\n')[2:])
        with open(f"{user_id}.txt", 'w') as file:
            file.write(f"{data[1:].split()[0]} {data[1:].split()[1]}")
        file.close()
        if is_premium(user_id) != ' ':
            reply_markup = {'inline_keyboard': [[{'text': f"{t.get('3').get(lan, t.get('3').get('en'))}",
                                                  'callback_data': f"P{data[1:].split()[1]} {data[1:].split()[0]}"}], [
                                                    {'text': f"{t.get('5').get(lan, t.get('5').get('en'))}",
                                                     'callback_data': "C"}]]}
            params = {
                'chat_id': user_id,
                'message_id': message_id,
                'text': f"🔁 *{t.get('4').get(lan, t.get('4').get('en'))}*\n\n{actual_message}",
                # based on the 'you have a new reply'
                'reply_markup': json.dumps(reply_markup),
                'parse_mode': 'Markdown'
            }
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", params=params)
        else:
            reply_markup = {
                'inline_keyboard': [[{'text': f"{t.get('5').get(lan, t.get('5').get('en'))}", 'callback_data': "C"}]]}
            params = {
                'chat_id': user_id,
                'message_id': message_id,
                'text': f"🔁 *{t.get('4').get(lan, t.get('4').get('en'))}*\n\n{actual_message}",
                'reply_markup': json.dumps(reply_markup),
                'parse_mode': 'Markdown'
            }
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", params=params)
    elif data[0] == 'P':
        actual_message = '\n'.join(text.split('\n')[2:])
        with open('users.txt', 'r') as file:
            lines = file.readlines()
        index_to_update = -1
        for i, line in enumerate(lines):
            if line.split()[0] == str(user_id):
                index_to_update = i
                break

        if index_to_update != -1:
            if int(lines[index_to_update].split()[3]) > 0:
                lines[
                    index_to_update] = f"{user_id} {lines[index_to_update].split()[1]} {lines[index_to_update].split()[2]} {int(lines[index_to_update].split()[3]) - 1}\n"
                remainder = int(lines[index_to_update].split()[3])
            else:
                reply_markup = {'inline_keyboard': [[{'text': f"{t.get('6').get(lan, t.get('6').get('en'))}",
                                                      'callback_data': f"R{data[1:].split()[1]} {data[1:].split()[0]}"}],
                                                    [{'text': f"{t.get('5').get(lan, t.get('5').get('en'))}",
                                                      'callback_data': "C"}]]}
                params = {
                    'chat_id': int(user_id),
                    'message_id': int(message_id),
                    'text': f"😔 <strong>{t.get('7').get(lan, t.get('7').get('en'))}</strong>\n\n{actual_message}",
                    'reply_markup': json.dumps(reply_markup),
                    'parse_mode': 'HTML'
                }
                requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", params=params)
                return
            updated_message = f"😔 <strong>{t.get('8').get(lan, t.get('8').get('en'))}</strong>"
            with open('log.txt', 'r') as log_file:
                log_lines = log_file.readlines()
                for log_line in log_lines:
                    if log_line.split()[0] == data[1:].split()[0]:
                        updated_message = log_line[len(log_line.split()[0]) + 1:]
                        break
            reply_markup = {'inline_keyboard': [[{'text': f"{t.get('6').get(lan, t.get('6').get('en'))}",
                                                  'callback_data': f"R{data[1:].split()[1]} {data[1:].split()[0]}"}], [
                                                    {'text': f"{t.get('5').get(lan, t.get('5').get('en'))}",
                                                     'callback_data': "C"}]]}
            params = {
                'chat_id': int(user_id),
                'message_id': int(message_id),
                'text': f"✍️ <strong>{t.get('9').get(lan, t.get('9').get('en'))}</strong> {updated_message}<strong>{t.get('17').get(lan, t.get('17').get('en'))} ☄️ {remainder}</strong>\n\n{actual_message}",
                'reply_markup': json.dumps(reply_markup),
                'parse_mode': 'HTML'
            }
            requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", params=params)
            with open('users.txt', 'w') as file:
                file.writelines(lines)
            git_update('users.txt')
    elif data[0] == 'B':
        with open('block.txt', 'a') as file:
            file.write(f"{data[1:]}\n")
    elif data[0] == 'F':
        with open(f'{user_id}_block.txt', 'w') as file:
            file.write(f"{data[1:]}\n")
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageText',
                      json={'chat_id': user_id, 'message_id': message_id,
                            'text': f"{t.get('23').get(lan, t.get('23').get('en'))}", 'parse_mode': 'Markdown'})
        # here i will write what to do if the permamnet block probably open another file for each user like blocklist
        # which will be different from the one written in block.txt
        # here i can make a premium feature like blocking many people at the same time
        return
    elif data[0] == 'S':
        reply_markup = {'inline_keyboard': [[{'text': f"{t.get('6').get(lan, t.get('6').get('en'))}",
                                              'callback_data': f"R{data[1:].split()[0]} {data[1:].split()[1]}"}], [
                                                {'text': f"{t.get('5').get(lan, t.get('5').get('en'))}",
                                                 'callback_data': "C"}], [
                                                {'text': f"{t.get('19').get(lan, t.get('19').get('en'))}",
                                                 'callback_data': f"F{data[1:].split()[0]}"}]]}
        params = {
            'chat_id': int(user_id),
            'message_id': int(message_id),
            'text': f"😔 {t.get('20').get(lan, t.get('20').get('en'))}",
            'reply_markup': json.dumps(reply_markup),
            'parse_mode': 'Markdown'
        }
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", params=params)
        reply_markup = {
            'inline_keyboard': [[{'text': f"{t.get('21').get(lan, t.get('21').get('en'))}", 'callback_data': 'admin'}]]}
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', json={'chat_id': data[1:].split()[0],
                                                                                  'photo': "AgACAgIAAxkBAAIxOGW0AAF2jzpzYv_lUNBTf4MmM8bDiwAC0tgxG9uooUkcZ7YZbWL4rQEAAwIAA3kAAzQE",
                                                                                  'caption': f"{t.get('22').get(lan, t.get('22').get('en'))}",
                                                                                  'parse_mode': 'Markdown',
                                                                                  'reply_markup': reply_markup,
                                                                                  'reply_to_message_id':
                                                                                      data[1:].split()[1]})
        params = {
            'chat_id': GROUP,
            'from_chat_id': data[1:].split()[0],
            'message_id': data[1:].split()[1],
        }
        reply_id = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/copyMessage', json=params).json()['result'][
            'message_id']
        reply_markup = {
            'inline_keyboard': [[{'text': f"Block Permanently", 'callback_data': f'B{data[1:].split()[0]}'}]]}
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', json={'chat_id': GROUP,
                                                                                    'text': f'Author ID: {data[1:].split()[0]}\nMessage ID: {data[1:].split()[1]}\nReciever ID: {user_id}',
                                                                                    'parse_mode': 'Markdown',
                                                                                    'reply_markup': reply_markup,
                                                                                    'reply_to_message_id': reply_id})
    elif data == 'premium':
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage",
                      json={'chat_id': user_id, 'message_id': message_id})
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
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendInvoice", json=invoice_payload)
    elif data == 'admin':
        params = {'chat_id': user_id, 'message_id': message_id,
                  'caption': f"🫴 *{t.get('18').get(lan, t.get('18').get('en'))}*", 'parse_mode': 'Markdown'}
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageCaption", params=params)
        with open(f"{user_id}.txt", 'w') as file:
            file.write(f"{ADMIN} N")
        file.close()
    elif data == 'cancel':
        cancel(user_id)
        edit_params = {'chat_id': user_id, 'message_id': message_id, 'media': json.dumps({'type': 'photo',
                                                                                          'media': "AgACAgQAAxkBAAIuK2WuZPTLfwz7mXXKgkcFY-P9BPMGAAKosDEbbrvEUro4KdfBM6SeAQADAgADeQADNAQ",
                                                                                          'caption': f"ℹ️ *{t.get('1').get(lan, t.get('1').get('en'))}*",
                                                                                          'parse_mode': 'Markdown', }), }
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageMedia", params=edit_params)
    elif data == 'not':
        edit_media_params = {
            'chat_id': user_id,
            'message_id': message_id,
            'media': json.dumps({
                'type': 'photo',
                'media': "AgACAgQAAxkBAAIuF2WuYgABCmA8ijQ4qQkhemj8_On9ZwACkrIxGwYMXFF66sxmpl7htwEAAwIAA3gAAzQE",
                'caption': f"👌 *{t.get('12').get(lan, t.get('12').get('en'))}*",
                'parse_mode': 'Markdown'
            }),
        }
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageMedia", params=edit_media_params)
    elif data == 'buy':
        reply_markup = {'inline_keyboard': [[{'text': '1 Galacoins = 1000.00 UZS', 'callback_data': '.'}],
                                            [{'text': '5 Galacoins = 4500.00 UZS', 'callback_data': '?'}],
                                            [{'text': '10 Galacoins = 8000.00 UZS', 'callback_data': '!'}],
                                            [{'text': '20 Galacoins = 15000.00 UZS', 'callback_data': '&'}],
                                            [{'text': "Report & Reward", 'callback_data': 'admin'}]]}
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/editMessageCaption',
                      params={'chat_id': user_id, 'message_id': message_id,
                              'caption': f"{t.get('13').get(lan, t.get('13').get('en'))}", 'parse_mode': 'Markdown',
                              'reply_markup': json.dumps(reply_markup)})
    elif data == '.' or data == '?' or data == '!' or data == '&':
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage",
                      json={'chat_id': user_id, 'message_id': message_id})
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
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendInvoice", json=invoice_payload)
    elif len(data) >= 2 and data[1].isdigit():
        params = {'chat_id': user_id, 'message_id': message_id,
                  'text': f"🫴 *{t.get('16').get(lan, t.get('16').get('en'))}*", 'parse_mode': 'Markdown'}
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/editMessageText", params=params)
        with open(f"{user_id}.txt", 'w') as file:
            file.write(f"{data} N")
        file.close()
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
    results = [{'type': 'article', 'id': '1', 'title': f"{t.get('1').get(lan, t.get('1').get('en'))}",
                'input_message_content': {
                    'message_text': f"{t.get('2').get(lan, t.get('2').get('en'))}\n[{text}](t.me/anonym_xbot?start={user_id})",
                    'parse_mode': 'Markdown', 'disable_web_page_preview': True}}]
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/answerInlineQuery',
                  json={'inline_query_id': query_id, 'results': results, 'cache_time': 0})
    return


def process(update):
    global lan
    if 'message' in update:  # 'text' in update['message']:
        lan = update['message']['from']['language_code']  # .get('language_code', 'en')
        if 'text' in update['message']:
            text = update['message']['text']
            if text[:6] == '/start':
                initial(update['message']['from']['id'], update['message']['from']['first_name'],
                        update['message']['text'], update['message']['from'])
            elif any(text == command for command in COMMANDS):
                commands(update['message']['from']['id'], text)
            elif text == '/INITIALIZE' and update['message']['from']['id'] == int(ADMIN):
                initialize()
            elif text == '/SENDDATABASE' and update['message']['from']['id'] == int(ADMIN):
                send_database()
            elif text == '/SENDUSERS' and update['message']['from']['id'] == int(ADMIN):
                send_users()
            elif text == '/SENDLOGS' and update['message']['from']['id'] == int(ADMIN):
                send_logs()
            elif text == '/SENDREFERRAL' and update['message']['from']['id'] == int(ADMIN):
                send_referral()
            elif text.split()[0] == '/SENDBLOCK' and update['message']['from']['id'] == int(ADMIN):
                send_block()
            elif text.split()[0] == '/REMOVE' and update['message']['from']['id'] == int(ADMIN):
                remove(text)
            elif text.split()[0] == '/SHOWCOINS' and update['message']['from']['id'] == int(ADMIN):
                show_coins(text)
            elif text.split()[0] == '/SHOWBONUSES' and update['message']['from']['id'] == int(ADMIN):
                show_bonuses(text)
            elif text.split()[0] == '/REMOVEBONUS' and update['message']['from']['id'] == int(ADMIN):
                remove_bonus(text)
            elif text == '/ERASE' and update['message']['from']['id'] == int(ADMIN):
                erase()
            elif text.split()[0] == '/PREMIUM' and update['message']['from']['id'] == int(
                    ADMIN):  # text should be something like this: text = /PREMIUM 123467890 ADMIN Komiljon 456 (number of messages to see)
                make_premium(text)
            elif text.split()[0] == '/BROADCAST' and update['message']['from']['id'] == int(ADMIN):
                broadcast(text)
            elif text.split()[0] == '/NEON' and update['message']['from']['id'] == int(ADMIN):
                neon()
            else:
                message(update['message']['from']['id'], update['message']['message_id'], update['message']['text'],
                        update['message']['from'], update)
        else:
            media(update['message']['from']['id'], update['message']['message_id'], update['message']['from'], update)
    elif 'callback_query' in update and 'data' in update['callback_query']:
        try:
            text = update['callback_query']['message']['text']
        except:
            text = update['callback_query']['message']['caption']
        lan = update['callback_query']['from'].get('language_code', 'en')
        callback(update['callback_query']['data'], update['callback_query']['from']['id'],
                 update['callback_query']['message']['message_id'], text)
    elif 'inline_query' in update:
        lan = update['inline_query']['from'].get('language_code', 'en')
        inline(update['inline_query']['from']['id'], update['inline_query']['query'], update['inline_query']['id'])
    else:
        print('unwanted type of message')
        print(update)
        lan = 'en'


def cancel(user_id):
    with open(f"{user_id}.txt", 'w') as file:
        file.write(' ')
    file.close()
    return


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
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                      params={'chat_id': user_id, 'text': f"ℹ️ *{t.get('2').get(lan, t.get('2').get('en'))}*",
                              'parse_mode': 'Markdown'})
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
    else:
        return
    return


def menu(user_id, text):
    if is_premium(user_id) == ' ':
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
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage", data=data)
    return


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
    with open('referral.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.split()[0] == str(user_id):
                reply_markup = {'inline_keyboard': [[{'text': f"{t.get('4').get(lan, t.get('4').get('en'))}",
                                                      'switch_inline_query': f"{t.get('5').get(lan, t.get('5').get('en'))}"}],
                                                    [{'text': f"{t.get('2').get(lan, t.get('2').get('en'))}",
                                                      'callback_data': 'admin'}]]}
                if is_premium(user_id) != ' ':
                    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', json={'chat_id': user_id,
                                                                                              'photo': "AgACAgQAAxkBAAIwLGWzlzlpi_rv496Er9Sc2ZHiooGvAAJsxTEbkVehUaCXAuue0SroAQADAgADcwADNAQ",
                                                                                              'caption': f"{t.get('1').get(lan, t.get('1').get('en'))} *{line.split()[1]}*\n\n{t.get('3').get(lan, t.get('3').get('en'))}",
                                                                                              'parse_mode': 'Markdown',
                                                                                              'reply_markup': reply_markup,
                                                                                              'disable_web_page_preview': True})
                else:
                    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', json={'chat_id': user_id,
                                                                                              'photo': "AgACAgQAAxkBAAIwLGWzlzlpi_rv496Er9Sc2ZHiooGvAAJsxTEbkVehUaCXAuue0SroAQADAgADcwADNAQ",
                                                                                              'caption': f"{t.get('1').get(lan, t.get('1').get('en'))} *{line.split()[1]}*\n\n{t.get('6').get(lan, t.get('6').get('en'))}",
                                                                                              'parse_mode': 'Markdown',
                                                                                              'reply_markup': reply_markup,
                                                                                              'disable_web_page_preview': True})
    return


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
    with open('users.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.split()[0] == str(user_id):
                reply_markup = {'inline_keyboard': [
                    [{'text': f"{t.get('1').get(lan, t.get('1').get('en'))}", 'callback_data': 'buy'}]]}
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', json={'chat_id': user_id,
                                                                                          'photo': 'AgACAgQAAxkBAAItkmWuSiqGuKWYvf4sg5n_WKhbZ_-cAAISszEbmwFcUbXmCXMUFvixAQADAgADeAADNAQ',
                                                                                          'caption': f"*{t.get('2').get(lan, t.get('2').get('en'))} {line.split()[3]} {t.get('3').get(lan, t.get('3').get('en'))}.*",
                                                                                          'parse_mode': 'Markdown',
                                                                                          'reply_markup': reply_markup})
    return


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
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', json={
        'chat_id': user_id,
        'photo': "AgACAgQAAxkBAAIvmWWyAAHwS7PbaJmFEwABhQz3hrnJa0wAAizAMRuCKpFRSbqRcnk9xFEBAAMCAANzAAM0BA",
        'caption': f"⚠️ {t.get('3').get(lan, t.get('3').get('en'))}\n\n",
        'parse_mode': 'Markdown',
        'reply_markup': reply_markup
    })
    return


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
    requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                  data={'chat_id': user_id, 'caption': f"{t.get(lan, t.get('en'))}", 'parse_mode': 'Markdown',
                        'photo': "AgACAgQAAxkBAAIvqWWyArVKqYTTJif9vNJeP09w_y4YAAIvwDEbgiqRUU8MArKikLFlAQADAgADcwADNAQ"})
    return


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
    file_id = 'AgACAgQAAxkBAAItlGWuSxYfx7WKZutB_iRYskIHAAHWPgACx7IxG4jlVFG9vvHI1ot3AgEAAwIAA3gAAzQE'

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

    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', json={
        'chat_id': user_id,
        'photo': file_id,
        'caption': params['text'],
        'parse_mode': 'Markdown',
        'reply_markup': params['reply_markup']
    })

    return


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
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', data={'chat_id': user_id,
                                                                              'caption': f"<strong>{t.get('1').get(lan, t.get('1').get('en'))}</strong>\n\n<em>{t.get('2').get(lan, t.get('2').get('en'))}</em>\n\n{t.get('3').get(lan, t.get('3').get('en'))}\n{t.get('4').get(lan, t.get('4').get('en'))}\n{t.get('5').get(lan, t.get('5').get('en'))}\n{t.get('6').get(lan, t.get('6').get('en'))}\n{t.get('7').get(lan, t.get('7').get('en'))}\n{t.get('8').get(lan, t.get('8').get('en'))}\n{t.get('9').get(lan, t.get('9').get('en'))}\n{t.get('10').get(lan, t.get('10').get('en'))}\n",
                                                                              'parse_mode': 'HTML',
                                                                              'photo': 'AgACAgQAAxkBAAIvjWWx_-E_ccV4_Qd0ht1LF1epaY_rAAIrwDEbgiqRUQ-zkIsKLa7VAQADAgADcwADNAQ'})
    return


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
    case = is_premium(user_id)
    if case != ' ':
        text = f"*{t.get('1').get(lan, t.get('1').get('en'))}*\n`t.me/anonym_xbot?start={user_id}`\n\n*{t.get('2').get(lan, t.get('2').get('en'))}*\n`t.me/anonym_xbot?start={case}`\n\n*{t.get('3').get(lan, t.get('3').get('en'))}*"
    else:
        text = f"*{t.get('1').get(lan, t.get('1').get('en'))}*\n`t.me/anonym_xbot?start={user_id}`\n\n*{t.get('3').get(lan, t.get('3').get('en'))}*"
    reply_markup = {'inline_keyboard': [[{'text': f"{t.get('4').get(lan, t.get('4').get('en'))}",
                                          'switch_inline_query': f"{t.get('5').get(lan, t.get('5').get('en'))}"}]]}
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto', json={'chat_id': user_id,
                                                                              'photo': "AgACAgQAAxkBAAIvomWyAgHpKNE4W6DSeY0MKfBJFE77AAIuwDEbgiqRUb1p-RWeIeDSAQADAgADeQADNAQ",
                                                                              'caption': text, 'parse_mode': 'Markdown',
                                                                              'reply_markup': reply_markup,
                                                                              'disable_web_page_preview': True})
    return


def is_premium(user_id):
    with open('users.txt', 'r') as file:
        lines = file.readlines()
        for line in lines:
            if line.split()[0] == str(user_id):
                if line.split()[1] == 'N':
                    return ' '
                else:
                    return line.split()[1]
    return ' '


def initialize():
    with open('users.txt', 'r') as file:
        for line in file.readlines():
            with open(f'{line.split()[0]}.txt', 'w') as f:
                f.write(' ')
            with open(f'{line.split()[0]}_block.txt', 'w') as f:
                f.write(' ')
    return


def neon():
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', json={'chat_id': ADMIN,
                                                                                'text': '<strong>Table of commands:</strong>\n\n<em>/INITIALIZE\n/SENDDATABASE\n/SENDUSERS\n/SENDLOGS\n/SENDREFERRAL\n/SENDBLOCK\n/REMOVE {chat_id} {message_id}\n/SHOWCOINS {user_id}\n/SHOWBONUSES {user_id}\n/REMOVEBONUSES {user_id}\n/ERASE\n/UNBLOCK {user_id}\n/PREMIUM {user_id} {custom_link} {custom name} {coins}\n/BROADCAST ALL/{user_id} {message_content_in_markdown}</em>',
                                                                                'parse_mode': 'HTML'})


def broadcast(text):
    if text.split()[1] == 'ALL':
        with open('users.txt', 'r') as file:
            lines = file.readlines()
            for line in lines:
                response = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                                         json={'chat_id': line.split()[0],
                                               'text': text[len(text.split()[0]) + len(text.split()[1]) + 1:],
                                               'parse_mode': 'Markdown'}).status_code
                if response != 200:
                    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                                  json={'chat_id': ADMIN, 'text': f"*Error!:* {line}", 'parse_mode': 'Markdown'})
                else:
                    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                                  json={'chat_id': ADMIN, 'text': f"*Success!:* {line}", 'parse_mode': 'Markdown'})
    else:
        response = requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                                 json={'chat_id': text.split()[1],
                                       'text': text[len(text.split()[0]) + len(text.split()[1]) + 1:],
                                       'parse_mode': 'Markdown'}).status_code
        if response != 200:
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                          json={'chat_id': ADMIN, 'text': '*Error!*', 'parse_mode': 'Markdown'})
        else:
            requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                          json={'chat_id': ADMIN, 'text': '*Success!*', 'parse_mode': 'Markdown'})
    return


def send_database():
    with open('database.txt', 'r') as file:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", params={'chat_id': ADMIN},
                      files={'document': ('Database.txt', io.StringIO(''.join(file.readlines())))})
    file.close()
    return


def send_users():
    with open('users.txt', 'r') as file:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", params={'chat_id': ADMIN},
                      files={'document': ('User.txt', io.StringIO(''.join(file.readlines())))})
    file.close()
    return


def send_logs():
    with open('log.txt', 'r') as file:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", params={'chat_id': ADMIN},
                      files={'document': ('Logs.txt', io.StringIO(''.join(file.readlines())))})
    file.close()
    return


def send_referral():
    with open('referral.txt', 'r') as file:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", params={'chat_id': ADMIN},
                      files={'document': ('Referral.txt', io.StringIO(''.join(file.readlines())))})
    file.close()
    return


def send_block():
    with open('block.txt', 'r') as file:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendDocument", params={'chat_id': ADMIN},
                      files={'document': ('Block.txt', io.StringIO(''.join(file.readlines())))})
    file.close()
    return


def unblock(text):
    with open('block.txt', 'r') as file:
        lines = file.readlines()
    with open('block.txt', 'w') as file:
        file.writelines([line for line in lines if f"{text.split()[1]}" not in line])
    git_update('block.txt')


def erase():
    with open('database.txt', 'w') as file:
        file.write(' ')
    file.close()
    return


def remove(text):
    if requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/deleteMessage",
                     json={'chat_id': f"{text.split()[1]}", 'message_id': f"{text.split()[2]}"}).status_code == 200:
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                      json={'chat_id': ADMIN, 'text': f"*Done!*", 'parse_mode': 'Markdown'})
    else:
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                      json={'chat_id': ADMIN, 'text': f"*I could not delete this message.*", 'parse_mode': 'Markdown'})


def remove_bonus(text):
    with open('referral.txt', 'r') as file:
        lines = file.readlines()
    newline = ' '
    for line in lines:
        if line.split()[0] == text.split()[1]:
            newline = f"{line.split()[0]} {int(line.split()[1]) - int(text.split()[2])}\n"
            break
    with open('referral.txt', 'w') as file:
        if newline != ' ':
            file.write(newline)
        file.writelines([line for line in lines if f"{text.split()[1]}" not in line])
        requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                      json={'chat_id': ADMIN, 'text': f"*Done!*", 'parse_mode': 'Markdown'})
    git_update('referral.txt')
    return


def show_coins(text):
    with open('users.txt', 'r') as file:
        for line in file.readlines():
            if text.split()[1] == line.split()[0]:
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                              json={'chat_id': ADMIN, 'text': f"*This user has *{line.split()[3]} Galacoins.",
                                    'parse_mode': 'Markdown'})
                return
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                  json={'chat_id': ADMIN, 'text': f"*I could not find this user.*", 'parse_mode': 'Markdown'})
    return


def show_bonuses(text):
    with open('referral.txt', 'r') as file:
        for line in file.readlines():
            if text.split()[1] == line.split()[0]:
                requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                              json={'chat_id': ADMIN, 'text': f"*This user has *{line.split()[1]} bonuses.",
                                    'parse_mode': 'Markdown'})
                return
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',
                  json={'chat_id': ADMIN, 'text': f"*I could not find this user.*", 'parse_mode': 'Markdown'})
    return


def make_premium(text):
    with open('users.txt', 'r') as file:
        lines = file.readlines()
        updated_lines = [line for line in lines if f"{text.split()[1]}" not in line]
    file.close()
    with open('users.txt', 'w') as file:
        file.write(f"{text.split()[1]} {text.split()[2]} {text.split()[3]} {text.split()[4]}\n")
        file.writelines(updated_lines)
    file.close()
    requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage',json={'chat_id': ADMIN, 'text': '*Done!*', 'parse_mode': 'Markdown'})
    git_update('users.txt')
    return


def alert(user):
    params = {
        'chat_id': ADMIN,
        'text': "<strong>NEW MEMBER!!!\n</strong>" + user,
        'parse_mode': 'HTML',
    }
    print(requests.post(f'https://api.telegram.org/bot{BOT_TOKEN}/sendMessage', params=params))


def git_update(filename):
    with open(filename, "r") as file:
        new_content = file.read()
    new_content_bytes = new_content.encode("utf-8")
    new_content_base64 = base64.b64encode(new_content_bytes).decode("utf-8")
    url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{filename}"
    headers = {
        "Authorization": f"token {GIT_TOKEN}"
    }
    response = requests.get(url, headers=headers)
    response_data = response.json()
    sha = response_data["sha"]
    payload = {
        "message": "Update users.txt",
        "content": new_content_base64,
        "sha": sha,
        "branch": BRANCH
    }
    update_url = f"https://api.github.com/repos/{USER}/{REPO}/contents/{filename}"
    print(requests.put(update_url, json=payload, headers=headers).json())


if __name__ == '__main__':
    app.run(debug=False)
