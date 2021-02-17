import urllib
import telebot
from telebot import types
import config
from instaparser import Scrap
import gc

bot = telebot.TeleBot(config.token)
anw = 10
sc = None

# Запустить / перезапустить кнопки
@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)  # Create keyboard markup
    item1 = types.KeyboardButton('🔎Инстаграм парсинг')
    item2 = types.KeyboardButton('⏳Процесс')
    item4 = types.KeyboardButton('📥Запросить уже найденные аккаунты')
    item3 = types.KeyboardButton('🍪Загрузить cookies')
    markup.add(item1, item2)  # Firs line buttons
    markup.add(item4)
    markup.add(item3)  # Second line buttons
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)


@bot.message_handler(commands=['restart'])
def restart(message):
    bot.send_message(message.chat.id, 'Бот начал перезагрузку. Подождите 1-2 минуты.')
    try:
        sc.close_all_drivers()
    except Exception as e:
        print(e)
    if sc.saved(sc.marks):
        try:
            file = open('result_parser.txt', 'rb')
            bot.send_document(message.chat.id, file)
            file.close()
        except:
            bot.send_message(message.chat.id, 'Не удалось сохранить данные.')
    else:
        bot.send_message(message.chat.id, "Не удалось сохранить данные.")
    bot.stop_polling()
    bot.stop_polling()


@bot.message_handler(commands=['clear'])
def clear(message):
    gc.enable()
    bot.send_message(message.chat.id, 'Очиста проведена успешно!')


@bot.message_handler(content_types='text')
def msg(message):
    global sc
    if sc is None:
        sc = Scrap()
    if message.text == '🔎Инстаграм парсинг':
        if sc.process_busy is False:
            bot.register_next_step_handler(bot.send_message(message.chat.id, 'Количество аккаунтов которое нужно'),
                                           step1)
        elif sc.process_busy is True:
            bot.send_message(message.chat.id, 'Занято незаверешенным процессом!\nДождитесь завершения или перезапустите бота командой /restart')

    if message.text == '⏳Процесс':
        if sc.process_busy is True:
            try:
                msg = bot.send_message(message.chat.id, f'<b>Текущий аккаунт:</b> {sc.user}\n<b>Постов просмотренно:</b> {len(sc.posts)}/{sc.number_of_posts}\n<b>Найдено отметок:</b> {len(sc.marks)}/{anw}\n<b>Безрезультатных попыток: </b>{sc.counter_repeat}/{sc.kill_edge}', parse_mode='html')

            except Exception as e:
                print(e)

        else:
            bot.send_message(message.chat.id, str('Сейчас нет активных процессов'))

    if message.text == '🍪Загрузить cookies':
        markup = types.InlineKeyboardMarkup()
        item1 = types.InlineKeyboardButton('Отмена', callback_data='cookies_no')
        markup.add(item1)
        msg = bot.send_message(message.chat.id, 'Отправьте файл cookies', reply_markup=markup)
        bot.register_next_step_handler(msg, use_cookies)

    if message.text == '📥Запросить уже найденные аккаунты':
        try:
            if sc.saved(sc.marks):
                try:
                    if sc.usernames is not None:
                        usernames = str(sc.usernames).replace("'", "").replace('[', '').replace(']', '')
                        file = open('result_parser.txt', 'rb')
                        bot.send_document(message.chat.id, file, caption=usernames)
                    elif sc.usernames is None:
                        file = open('result_parser.txt', 'rb')
                        bot.send_document(message.chat.id, file)
                except:
                    bot.send_message(message.chat.id, 'Не удалось сохранить данные')
            else:
                bot.send_message(message.chat.id, "Не удалось сохранить данные")
        except:
            bot.send_message('Сейчас нет активных процессов')


def step1(message):
    global anw
    anw = str(message.text)
    if anw.isdigit():  # Условие которое пропускает только, если строка состоит из чисел
        anw = int(anw)
        if anw >= 1:
            bot.register_next_step_handler(bot.send_message(message.chat.id, 'Юзернеймы инсты через запятую'), step2)
        else:
            bot.send_message(message.chat.id, 'Число не может быть меньше 1!\nВведите число ещё раз.')
            bot.register_next_step_handler(bot.send_message(message.chat.id, 'Количество аккаунтов которое нужно'),
                                           step1)
    else:
        bot.send_message(message.chat.id, 'Используйте только цифры!')
        bot.register_next_step_handler(bot.send_message(message.chat.id, 'Количество аккаунтов которое нужно'), step1)


def step2(message):
    global sc
    try:
        bot.send_message(message.chat.id,
                         'Бот начал работу.\nДля отслеживания процесса вы можете воспользоваться кнопкой "⏳Процесс"')

        if sc is None:
            sc = Scrap()  # Создал экземляр класса
            sc.scrap(sc.split_usernames(message.text), anw)
        else:
            sc.scrap(sc.split_usernames(message.text), anw)
        try:
            if sc.saved(sc.marks):
                try:
                    file = open('result_parser.txt', 'rb')
                    try:
                        bot.send_message(message.chat.id, f'Готово!\n<b>Отметок было найдено:</b> {len(sc.marks)}', parse_mode='html')
                    except:
                        bot.send_message(message.chat.id, 'Готово!')
                    try:
                        if sc.usernames is not None:
                            usernames = str(sc.usernames).replace("'", "").replace('[', '').replace(']', '')
                            file = open('result_parser.txt', 'rb')
                            bot.send_document(message.chat.id, file, caption=usernames)
                        elif sc.usernames is None:
                            file = open('result_parser.txt', 'rb')
                            bot.send_document(message.chat.id, file)
                    except:
                            bot.send_document(message.chat.id, file)
                            file.close()
                except:
                    bot.send_message(message.chat.id, 'Не удалось сохранить данные.')

                pass
        except Exception as e:
            print(e)




    except Exception as e:
        bot.send_message(message.chat.id, f'Попробуйте ещё раз!\nВозможно файл оказался пустым.')
        print(e)

    sc = None


@bot.message_handler(content_types=["document"])
def use_cookies(message):
    global file_info
    document_id = message.document.file_id
    markup = types.InlineKeyboardMarkup()
    item1 = types.InlineKeyboardButton('Да', callback_data='cookies_yes')
    item2 = types.InlineKeyboardButton('Нет', callback_data='cookies_no')
    markup.add(item1, item2)
    bot.send_message(message.chat.id, 'Вы уверены, что хотите изменить файл cookies?', reply_markup=markup)
    file_info = bot.get_file(document_id)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    try:
        if call.message:
            if call.data == 'cookies_yes':
                urllib.request.urlretrieve(f'http://api.telegram.org/file/bot{config.token}/{file_info.file_path}',
                                           'insta.txt')
                print(file_info.file_path)
                bot.edit_message_text('Cookies были изменены!', chat_id=call.message.chat.id,
                                      message_id=call.message.message_id)
            if call.data == 'cookies_no':
                bot.edit_message_text('Изменение cookies было отменено!', chat_id=call.message.chat.id,
                                      message_id=call.message.message_id)

    except Exception as e:
        print(e)


bot.polling()
