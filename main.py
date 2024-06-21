import json
from random import randint

import telebot
from telebot import types

from config import TOKEN

bot = telebot.TeleBot(TOKEN)

user_flags = {}

with open('albumbase.json', encoding='utf-8') as db:
    data = json.load(db)


def create_keyboard(buttons):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=1)
    keyboard.add(*buttons)
    return keyboard


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_flags[chat_id] = {'read_disclaimer': False}
    mainkeys = create_keyboard(['🔮 Случайный Альбом',
                                '🧙‍♂️ Обратная Связь',
                                '📙 Перейти в Оранжевый Паблик в VK'])
    mess = (f'Привет, <b>{message.from_user.first_name}</b>!\n'
            f'Это телеграм-бот <b>Оранжевого Телеграма</b>.\n\nОн может:\n\n'
            f'🔮 - подкинуть из архива случайный альбом '
            f'с интересной музыкой.\nСейчас в архиве {len(data)} альбомов.\n\n'
            f'🧙‍♂️ - помочь связаться с администратором '
            f'<b>Оранжевого Телеграма</b>\n\n'
            f'📙 - направить вас в <b>Оранжевый Паблик</b> в ВК.\nЗа '
            f'дюжину лет там накопилось почти 4000 постов с разной '
            f'музыкой.\n\n'
            f'Нажмите на одну из интересующих вас кнопок:')
    bot.send_message(chat_id, mess, reply_markup=mainkeys, parse_mode='HTML')
    bot.register_next_step_handler_by_chat_id(chat_id, sorting_function)


@bot.message_handler(content_types=['text'])
def sorting_function(message):
    chat_id = message.chat.id
    if message.text == '🧙‍♂️ Обратная Связь':
        bot.send_message(chat_id, "/disclaimer")
        disclaimer(message)
    elif (message.text == '🔮 Случайный Альбом' or
          message.text == '🔮 Ещё Один Случайный Альбом!'):
        bot.send_message(chat_id, "/randomize")
        random_album(message)
    elif message.text == '📙 Перейти в Оранжевый Паблик в VK':
        bot.send_message(chat_id, "/vk")
        vk(message)
    elif message.text == '🔙 Вернуться в главное меню':
        start(message)
    else:
        contact(message)


@bot.message_handler(commands=['disclaimer'])
def disclaimer(message):
    chat_id = message.chat.id
    basekey = create_keyboard(['🧡 Ясно-понятно',
                               '🔙 Вернуться в главное меню'])
    user_flags[chat_id] = {'read_disclaimer': False}
    mess = (f"Добро пожаловать!\n\n"
            f"Нажмите на кнопку с сердечком 🧡 и напишите свой "
            f"вопрос в одном сообщении. Я отвечу вам в ближайшее время.")
    bot.send_message(chat_id, mess, reply_markup=basekey, parse_mode='HTML')
    bot.register_next_step_handler_by_chat_id(chat_id, contact)


@bot.message_handler(func=lambda message: message.text.count('/') == 0 and
                                          '🧡 Ясно-понятно'
                                          not in message.text)
def contact(message):
    chat_id = message.chat.id
    if message.reply_to_message and chat_id == 449248371:
        user_chat_id = message.reply_to_message.text.split(" : ")[0]
        bot.send_message(chat_id=user_chat_id,
                         text=f"<b>{message.text}</b>",
                         parse_mode='HTML')
        return

    if not user_flags[chat_id]['read_disclaimer']:
        if message.text == '🧡 Ясно-понятно':
            user_flags[chat_id][
                'read_disclaimer'] = True
            markup = types.ReplyKeyboardRemove()
            bot.send_message(chat_id,
                             "Отлично! Теперь вы можете отправлять "
                             "сообщения.\n\nЧтобы вернуться в меню просто "
                             "введите '/start' (или нажмите на эту команду)",
                             reply_markup=markup)
            return
        else:
            bot.send_message(chat_id,
                             "Путь к общению лежит через сердце. Жми 🧡.")

    if user_flags[chat_id]['read_disclaimer']:
        bot.send_message(chat_id='449248371',
                         text=f"{message.chat.id} | "
                              f"{message.from_user.first_name} : "
                              f"\n\n{message.text}")


@bot.message_handler(commands=['vk'])
def vk(message):
    chat_id = message.chat.id
    markup = types.InlineKeyboardMarkup(row_width=1)
    markup.add(types.InlineKeyboardButton("Перейти в ВК",
                            url='https://vk.com/limited_edition_click_here'))
    bot.send_message(chat_id,
                     "🧙‍♂️ А вот и портал в Оранжевый Паблик!...",
                     reply_markup=markup)

    return_button = create_keyboard(['🔙 Вернуться в главное меню'])
    bot.send_message(chat_id, "...или можно вернуться в главное меню.",
                     reply_markup=return_button)


@bot.message_handler(commands=['randomize'])
def random_album(message):
    chat_id = message.chat.id
    user_flags[chat_id] = {'read_disclaimer': False}
    onecemorekey = create_keyboard(['🔮 Ещё Один Случайный Альбом!',
                                    '🔙 Вернуться в главное меню'])
    todayspick = data[randint(0, len(data) - 1)]
    title = todayspick['title']
    about = todayspick['about']
    links = todayspick['links']
    picture = todayspick['picture']
    link_text = " | ".join([f"<a href='{link}'>{service}</a>"
                            for service, link in links.items() if
                            link != 'none'])
    mess = f"<b>{title}</b>\n\n{about}\n\n{link_text}"
    bot.send_photo(chat_id, photo=open(picture, 'rb'))
    bot.send_message(chat_id, mess, reply_markup=onecemorekey,
                     parse_mode='HTML')
    bot.register_next_step_handler_by_chat_id(chat_id, sorting_function)


if __name__ == '__main__':
    print('Бот запущен!')
    while True:
        try:
            bot.polling(none_stop=True)
        except:
            pass