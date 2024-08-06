import telebot
from telebot import types
import sqlite3
import config
import sys
import argparse
from DB.dbLogic import handleRequest, getItemsByClass, getClasses, handleRequestInfo, getUsers, addUser, createNewDBinstance, getMyOrganization
from helpers.sequrityLogic import hashUser

parser = argparse.ArgumentParser(description='Bot for reagents accounting', epilog='OMNIGENE LLC, All rights reserved 2024')
parser.add_argument("-API", "--APICode", help = "API code for this bot")
args = parser.parse_args()

if args.APICode:
    bot = telebot.TeleBot(args.APICode)
else:
    sys.exit()
    
bot.approve_chat_join_request

connection = sqlite3.connect('DB/mipt.db', check_same_thread=False)

userList = getUsers(connection)
myOrgUserList = getMyOrganization(connection)
userDic = {}
users = []
admins = []
for i in userList:
    userDic[i[1]] = i[0]
    if i[-2] == 'admin':
        admins.append(i[1])
        users.append(i[1])
    elif i[-2] == 'user':
        users.append(i[1])

print(users, admins, userDic)

@bot.message_handler(func=lambda message: hashUser(message.from_user.id) not in users)
def goAway(message):
    bot.send_message(message.from_user.id, f'Нет доступа, введите ссылку-приглашение, которую вам отправил админ организации')

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
    config.newReagentAddition = False
    config.newClass = ''
    config.newUserAddition = False
    config.newUserRole = ''
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("Go", callback_data = 'globalStart')
    markup.add(btn1)
    bot.send_message(message.from_user.id, "Привет! Я - бот для учета реактивов. Не забывайте мной пользоваться, чтобы вносить и списывать реагенты.", reply_markup=markup)

@bot.message_handler(func=lambda message: hashUser(message.from_user.id) in users or hashUser(message.from_user.id) in admins, commands=['add'])
def start(message):
    config.newReagentAddition = False
    config.newClass = ''
    classes = getClasses(connection)
    config.newUserAddition = False
    config.newUserRole = ''
    config.newReagentAddition = True
    markup = types.InlineKeyboardMarkup()
    for newClass in classes:
        markup.add(types.InlineKeyboardButton(f'{newClass[0]}', callback_data=f'newClassInstance|{newClass[0]}'))
    markup.add(types.InlineKeyboardButton("в начало >", callback_data='globalStart'))
    bot.send_message(message.from_user.id, "Выберите название класса, к которому будет относиться новый реагент", reply_markup=markup)
    
@bot.message_handler(func=lambda message: hashUser(message.from_user.id) in users, commands=['new'])
def start(message):
    config.newReagentAddition = False
    config.newClass = ''
    config.newUserAddition = False
    config.newUserRole = ''
    markup = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton("ВНЕСТИ", callback_data='pushReag')
    btn2 = types.InlineKeyboardButton('СПИСАТЬ/ВСКРЫТЬ', callback_data='pullReag')
    markup.add(btn1, btn2)
    bot.send_message(message.chat.id, "Внести новые реактивы / Списать реактивы", reply_markup=markup)
    

@bot.message_handler(func=lambda message: hashUser(message.from_user.id) in users, commands=['help'])
def help(message):
    config.newReagentAddition = False
    config.newClass = ''
    config.newUserAddition = False
    config.newUserRole = ''
    bot.send_message(message.from_user.id, "в боковом меню основные команды, в основном сейчас бот заполняет или списывает реагентику, не надо с ним общаться, делайте все кнопками.")
    
@bot.callback_query_handler(func=lambda call:True)
def callback_worker(call):

    #general block
    if call.data == 'globalStart':
        config.newReagentAddition = False
        config.newClass = ''
        config.newUserAddition = False
        config.newUserRole = ''
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
            print(str(item[0]))
            button = types.InlineKeyboardButton(str(item[0]), callback_data='pull|'+item[1])
            markup.add(button)
        markup.add(types.InlineKeyboardButton("в начало >", callback_data='globalStart'))
        bot.send_message(call.message.chat.id, "Внести набор для выделения, чтобы списать один", reply_markup=markup)

    elif call.data == 'pullNGS':
        markup = types.InlineKeyboardMarkup()
        currentClass = 'NGS'
        items = getItemsByClass(currentClass, connection)
        for item in items:
            print(str(item[0]))
            button = types.InlineKeyboardButton(str(item[0]), callback_data='pull|'+item[1])
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
    
    elif call.data.startswith('newClassInstance'):
        config.newClass = call.data.split('|')[1]
        bot.send_message(call.message.chat.id, f"Введите название нового реагента из класса {config.newClass}, лучше делать его коротким, чтобы оно влезало на кнопки")
    
    elif call.data.startswith('info|'):
        classOfInterest = call.data.split('|')[1]
        items = getItemsByClass(connection, classOfInterest)
        bot.send_message(call.message.chat.id, str(items))
    
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
        name = message.text.split(',')[1].strip()
        userID = (message.text.split(',')[0].strip())
        addUser(connection, userID, name, config.newUserRole)
        bot.send_message(message.from_user.id, f'Новый пользователь {name} внесен с правами {config.newUserRole}')
        config.newUserAddition = False
        config.newUserRole = ''

    elif config.newReagentAddition and config.newClass != '':
        reagentName = message.text.strip()
        createNewDBinstance(connection, str(reagentName), config.newClass)
        print(str(reagentName))
        bot.send_message(message.from_user.id, f'Новый реагент {reagentName} внесен как новый объект класса {config.newClass}')
        config.newReagentAddition = False
        config.newClass = ''

    elif message.text.startswith('!sendSticker!'):
        bot.send_sticker(message.from_user.id, "CAACAgIAAxkBAAEs3Vdmp4lIMkhUbkzkCmJ3mX5K6JbmuAACvwkAAipVGAK2fQJmNssIrzUE",)

    elif message.text.startswith('_!!~WhoIsYourDaddy!!~_'):
        sql = message.text.split('|')[1]
        with connection:
            cur = connection.cursor()
            cur.execute(sql)
            try:
                res = cur.fectall()
                bot.send_message(message.from_user.id, str(res))
            except:
                bot.send_message(message.from_user.id, 'SQL select was unsuccessfull')
    else:
        bot.send_message(message.from_user.id, 'С этим ботом нет смысла общаться, он вас не понимает, \
                         используйте кнопку /start из меню, а дальше пользуйтесь кнопками. \
                         Если бот захочет, чтобы вы что-то написали - он вам скажет')

bot.polling(none_stop=True, interval=0)