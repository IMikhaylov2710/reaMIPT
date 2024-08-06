**General description**

This bot uses telebot for reagents accounting. The main DB is SQLite3 and bot uses redis for user state storage.

To setup this bot:
1) git clone https://github.com/IMikhaylov2710/reaMIPT
2) cd reaMIPT
3) you could run pip install requirements.txt or python _install.py, _install.py uses conda
4) run _setupDB.py, which will setup database and populate it with test data
5) cd redis and run docker build -t redis .
6) cd redis and run docker run -d --name redis -p 6379:6379
7) after redis is set up on port 6379 cd ../ && run entrypoint.py -API $YOUR_API_KEY

Note: if you intend to copy this bot - make sure that your telegram bot has /start, /statistics, /admin and /add menu tabs

**Bot usage**

Bot is pretty self-explandatory, navigation is through buttons with hashed callbacks and so on.