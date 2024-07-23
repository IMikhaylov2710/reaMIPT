import telebot
from telebot import types
import sqlite3
import hashlib
import config
from DB.dbLogic import handleRequest, createNewAlias, getItemsByClass, getClasses, handleRequestInfo, getUsers, addUser
from helpers.sequrityLogic import hashUser

bot = telebot.TeleBot('')
    
bot.approve_chat_join_request

connection = sqlite3.connect('DB/mipt.db', check_same_thread=False)

userList = getUsers(connection)
userDic = {}
users = []
admins = []
for i in userList:
    print(i)
    userDic[i[1]] = i[0]
    if i[-1] == 'admin':
        admins.append(i[1])
        users.append(i[1])
    elif i[-1] == 'user':
        users.append(i[1])

print(users, admins, userDic)

@bot.message_handler(func=lambda message: hashUser(message.from_user.id) not in users)
def goAway(message):
    bot.send_message(message.from_user.id, f'Нет доступа {hashUser(message.from_user.id)}')

@bot.message_handler(func=lambda message: hashUser(message.from_user.id) not in admins, commands=['admin'])
def admin(message):
    bot.send_message(message.from_user.id, 'У вас нет админских прав')

@bot.message_handler(func=lambda message: hashUser(message.from_user.id) in admins, commands=['admin'])
def admin(message):
    markup = types.InlineKeyboardMarkup()
    btn2 = types.InlineKeyboardButton('Внести нового пользователя', callback_data='userReg')
    markup.add(btn2)
    bot.send_message(message.from_user.id, "Админ", reply_markup=markup)

@bot.message_handler(func=lambda message: hashUser(message.from_user.id) in admins, commands=['statistics'])
def stat(message):
    classes = getClasses(connection)
    markup = types.InlineKeyboardMarkup()
    for i in classes:
        btn = types.InlineKeyboardButton(i[0], callback_data='info|'+i[0])
        markup.add(btn)
    bot.send_message(message.from_user.id, 'Выберите класс, для которого вы хотите получить информацию о наличии', reply_markup=markup)

@bot.message_handler(func=lambda message: hashUser(message.from_user.id) in users, commands=['start'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Go", callback_data = 'globalStart')
    markup.add(btn1)
    bot.send_message(message.from_user.id, "Привет! Я - бот для учета реактивов. Не забывайте мной пользоваться, чтобы вносить и списывать реагенты.", reply_markup=markup)
    
@bot.message_handler(func=lambda message: hashUser(message.from_user.id) in users, commands=['new'])
def start(message):
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("ВНЕСТИ", callback_data='pushReag')
    btn2 = types.InlineKeyboardButton('СПИСАТЬ/ВСКРЫТЬ', callback_data='pullReag')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Внести новые реактивы / Списать реактивы", reply_markup=markup)
    

@bot.message_handler(func=lambda message: hashUser(message.from_user.id) in users, commands=['help'])
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
        markup.add(types.InlineKeyboardButton("в начало >", callback_data='globalStart'))
        bot.send_message(call.message.chat.id, "Внести реактивы", reply_markup=markup)
    
    elif call.data == 'pushCleanup':
        markup = types.InlineKeyboardMarkup()
        currentClass = 'cleanup'
        items = getItemsByClass(currentClass, connection)
        for item in items:
            button = types.InlineKeyboardButton(str(item[0]).rstrip(), callback_data='push|'+item[1])
            markup.add(button)
        markup.add(types.InlineKeyboardButton("в начало >", callback_data='globalStart'))
        bot.send_message(call.message.chat.id, "Внести набор для выделения, чтобы внести один в базу", reply_markup=markup)

    elif call.data == 'pushNGS':
        markup = types.InlineKeyboardMarkup()
        currentClass = 'NGS'
        items = getItemsByClass(currentClass, connection)
        for item in items:
            button = types.InlineKeyboardButton(str(item[0]).rstrip(), callback_data='push|'+item[1])
            markup.add(button)
        markup.add(types.InlineKeyboardButton("в начало >", callback_data='globalStart'))
        bot.send_message(call.message.chat.id, "Выберите набор для NGS, чтобы внести один в базу", reply_markup=markup)

    elif call.data == 'pullReag':
        markup = types.InlineKeyboardMarkup()
        btn1 = types.InlineKeyboardButton("Выделение", callback_data='pullCleanup')
        btn2 = types.InlineKeyboardButton("NGS", callback_data='pullNGS')
        markup.add(btn1, btn2)
        markup.add(types.InlineKeyboardButton("в начало >", callback_data='globalStart'))
        bot.send_message(call.message.chat.id, "Списать набор", reply_markup=markup)
    
    elif call.data == 'pullCleanup':
        markup = types.InlineKeyboardMarkup()
        currentClass = 'cleanup'
        items = getItemsByClass(currentClass, connection)
        for item in items:
            button = types.InlineKeyboardButton(str(item[0]).rstrip(), callback_data='pull|'+item[1])
            markup.add(button)
        markup.add(types.InlineKeyboardButton("в начало >", callback_data='globalStart'))
        bot.send_message(call.message.chat.id, "Внести набор для выделения, чтобы списать один", reply_markup=markup)

    elif call.data == 'pullNGS':
        markup = types.InlineKeyboardMarkup()
        currentClass = 'NGS'
        items = getItemsByClass(currentClass, connection)
        for item in items:
            button = types.InlineKeyboardButton(str(item[0]).rstrip(), callback_data='pull|'+item[1])
            markup.add(button)
        markup.add(types.InlineKeyboardButton("в начало >", callback_data='globalStart'))
        bot.send_message(call.message.chat.id, "Выберите набор для NGS, чтобы списать", reply_markup=markup)

    elif call.data == 'userReg':
        markup = types.InlineKeyboardMarkup()
        config.newUserAddition = True
        btn1 = types.InlineKeyboardButton("Внести пользователя", callback_data='newUser')
        btn2 = types.InlineKeyboardButton('Внести админа', callback_data='newAdmin')
        markup.add(btn1, btn2, types.InlineKeyboardButton("в начало >", callback_data='globalStart'))
        bot.send_message(call.message.chat.id, "Выберите роль, которую хотите дать новому пользователю", reply_markup=markup)

    elif call.data == 'newUser':
        config.newUserRole = 'user'
        bot.send_message(call.message.chat.id, "Введите данные пользователя в формате userID, имя_пользователя ЧЕРЕЗ ЗАПЯТУЮ")
    elif call.data == 'newAdmin':
        config.newUserRole = 'admin'
        bot.send_message(call.message.chat.id, "Введите данные пользователя в формате userID, имя_пользователя ЧЕРЕЗ ЗАПЯТУЮ")

    else:
        try:
            handleRequest(call.data, connection)
            res = handleRequestInfo(call.data, connection)
            #for user in usersDic:
                #bot.send_message(user, f'Пользователь {userDic[hashUser(call.message.chat.id)]} что-то сделал с реагентом {str(res[0][0])}, в наличии {str(res[0][1])}') 
            bot.send_message(call.message.chat.id, f'Пользователь {userDic[hashUser(call.message.chat.id)]} что-то сделал с реагентом {str(res[0][0])}, в наличии {str(res[0][1])}')
        except:
            bot.send_message(call.message.chat.id, 'Что-то серьезно сломалось, пишите @bochonni')

@bot.message_handler(content_types="text")
def message_reply(message):
    if config.newUserAddition:
        print(message.text)
        name = message.text.split(',')[1].strip()
        userID = hashUser(message.text.split(',')[0].strip())
        addUser(connection, userID, name, config.newUserRole)
        config.newUserAddition = False
        config.newUserRole = ''

bot.polling(none_stop=True, interval=0)