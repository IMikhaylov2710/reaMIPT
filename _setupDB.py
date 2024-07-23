import sqlite3
import hashlib
import pandas as pd

conn = sqlite3.connect('DB/mipt.db')

test_data = [[
    'Cleanup S-Cap', 1, 'cleanup'
], [
    'Evrogen FFPE', 3, 'cleanup'
], [
    'Evrogen new kit', 5, 'cleanup'
], [
    'miSeq 250PE micro', 4, 'NGS'
]
]

usersDic = {
    121420608: 'i.mikhailov',
    251946129: 'p.molodtsova'
}

cur = conn.cursor()

try:
    sql = """select * from users"""
    cur.execute(sql)

except:
    sqlSetup1 = """CREATE TABLE IF NOT EXISTS reagents(
    name text unique not null, 
    quantity integer);"""

    sqlSetup2 = """CREATE TABLE IF NOT EXISTS aliases(
    name text not null unique,
    alias text not null, 
    class text not null);"""

    sqlSetup3 = """CREATE TABLE IF NOT EXISTS users(
    name text not null,
    userHash text not null, 
    userRights text not null
    )"""
    cur.execute(sqlSetup1)
    cur.execute(sqlSetup2)
    cur.execute(sqlSetup3)
    conn.commit()

usersRows = []
for user in usersDic:
    hash = hashlib.sha256(str(user).encode('utf-8')).hexdigest()
    row = [usersDic[user], hash, 'admin']
    sqlUsers = """INSERT OR REPLACE INTO users VALUES (?, ?, ?)"""
    cur.execute(sqlUsers, row)
    print(cur.lastrowid)
    conn.commit()

for i in test_data:
    sql = """INSERT OR REPLACE INTO reagents VALUES (?, ?)"""
    cur.execute(sql, (i[0], i[1]))
    print(cur.lastrowid)
    hash = hashlib.sha256(str(i[0]).encode('utf-8')).hexdigest()[:16]
    sql2 = """INSERT OR REPLACE INTO aliases VALUES (?, ?, ?)"""
    cur.execute(sql2, (i[0], hash, i[2]))
    conn.commit()
    print(cur.lastrowid)
