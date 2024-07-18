import telebot
from telebot import types
import sqlite3
from DB.dbLogic import handleRequest, createNewAlias, getItemsByClass, getClasses

bot = telebot.TeleBot('7016692600:AAEjyXhtwlfiXleml-yGCqvw3UHfnQTACtM')
    
bot.approve_chat_join_request

users = [121420608]
usersDic = {
    121420608: 'i.mikhailov'
}
admins = [121420608]

connection = sqlite3.connect('DB/mipt.db', check_same_thread=False)

@bot.message_handler(func=lambda message: message.from_user.id not in users)
def goAway(message):
    bot.send_message(message.from_user.id, 'Нет доступа')

@bot.message_handler(func=lambda message: message.from_user.id not in admins, commands=['admin'])
def admin(message):
    bot.send_message(message.from_user.id, 'У вас нет админских прав')

@bot.message_handler(func=lambda message: message.from_user.id in admins, commands=['admin'])
def admin(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Управление БД", callback_data='DBedit')
    btn2 = types.InlineKeyboardButton('Внести нового пользователя', callback_data='UserReg')
    markup.add(btn1, btn2)
    bot.send_message(message.from_user.id, "Админ", reply_markup=markup)

@bot.message_handler(func=lambda message: message.from_user.id in admins, commands=['statistics'])
def stat(message):
    classes = getClasses(connection)
    markup = types.InlineKeyboardMarkup()
    for i in classes:
        btn = types.InlineKeyboardButton(i[0], callback_data='info|'+i[0])
        markup.add(btn)
    bot.send_message(message.from_user.id, 'Выберите класс, для которого вы хотите получить информацию о наличии', reply_markup=markup)

@bot.message_handler(func=lambda message: message.from_user.id in users, commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Go", callback_data = 'globalStart')
    markup.add(btn1)
    bot.send_message(message.from_user.id, "Привет! Я - бот для учета реактивов. Не забывайте мной пользоваться, чтобы вносить и списывать реагенты.", reply_markup=markup)
    
@bot.message_handler(func=lambda message: message.from_user.id in users, commands=['new'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("ВНЕСТИ", callback_data='pushReag')
    btn2 = types.InlineKeyboardButton('СПИСАТЬ/ВСКРЫТЬ', callback_data='pullReag')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Внести новые реактивы / Списать реактивы", reply_markup=markup)
    

@bot.message_handler(func=lambda message: message.from_user.id in users, commands=['help'])
def help(message):
    bot.send_message(message.from_user.id, "в боковом меню основные команды, в основном сейчас бот заполняет или списывает реагентику, не надо с ним общаться, делайте все кнопками.")
    
@bot.callback_query_handler(func=lambda call:True)
def callback_worker(call):

    #general block
    if call.data == 'globalStart':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("ВНЕСТИ", callback_data='pushReag')
        btn2 = types.InlineKeyboardButton("СПИСАТЬ/ВСКРЫТЬ", callback_data='pullReag')
        markup.add(btn1, btn2)
        bot.send_message(call.message.chat.id, "Внести новые реактивы / Списать реактивы", reply_markup=markup)

    elif call.data == 'pushReag':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Выделение", callback_data='pushCleanup')
        btn2 = types.InlineKeyboardButton("NGS", callback_data='pushNGS')
        markup.add(btn1, btn2)
        bot.send_message(call.message.chat.id, "Внести реактивы", reply_markup=markup)
    
    elif call.data == 'pushCleanup':
        markup = types.InlineKeyboardMarkup()
        currentClass = 'cleanup'
        items = getItemsByClass(currentClass, connection)
        for item in items:
            print(len(item[0]), 'push|'+item[1])
            button = types.InlineKeyboardButton(str(item[0]).rstrip(), callback_data='push|'+item[1])
            markup.add(button)
        bot.send_message(call.message.chat.id, "Внести набор для выделения, чтобы внести один в базу", reply_markup=markup)

    elif call.data == 'pushNGS':
        markup = types.InlineKeyboardMarkup()
        currentClass = 'NGS'
        items = getItemsByClass(currentClass, connection)
        for item in items:
            print(len(item[0]), 'push|'+item[1])
            button = types.InlineKeyboardButton(str(item[0]).rstrip(), callback_data='push|'+item[1])
            markup.add(button)
        bot.send_message(call.message.chat.id, "Выберите набор для NGS, чтобы внести один в базу", reply_markup=markup)

    elif call.data == 'pullReag':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Выделение", callback_data='pullCleanup')
        btn2 = types.InlineKeyboardButton("NGS", callback_data='pullNGS')
        markup.add(btn1, btn2)
        bot.send_message(call.message.chat.id, "Списать набор", reply_markup=markup)
    
    elif call.data == 'pullCleanup':
        markup = types.InlineKeyboardMarkup()
        currentClass = 'cleanup'
        items = getItemsByClass(currentClass, connection)
        for item in items:
            print(len(item[0]), 'pull|'+item[1])
            button = types.InlineKeyboardButton(str(item[0]).rstrip(), callback_data='pull|'+item[1])
            markup.add(button)
        bot.send_message(call.message.chat.id, "Внести набор для выделения, чтобы списать один", reply_markup=markup)

    elif call.data == 'pullNGS':
        markup = types.InlineKeyboardMarkup()
        currentClass = 'NGS'
        items = getItemsByClass(currentClass, connection)
        for item in items:
            print(len(item[0]), 'pull|'+item[1])
            button = types.InlineKeyboardButton(str(item[0]).rstrip(), callback_data='pull|'+item[1])
            markup.add(button)
        bot.send_message(call.message.chat.id, "Выберите набор для NGS, чтобы списать", reply_markup=markup)

    else:
        try:
            handleRequest(call.data, connection)
        except:
            bot.send_message(call.message.chat.id, 'Что-то серьезно сломалось, пишите @bochonni')

bot.polling(none_stop=True, interval=0)