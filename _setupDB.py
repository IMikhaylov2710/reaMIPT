import sqlite3
import hashlib
import pandas as pd
import sys

conn = sqlite3.connect('DB/mipt.db')

validation = input('are you sure you want to redo setup? This will delete all tables, print "DELETE" to confirm: ')
if not validation == 'DELETE':
    sys.exit()
else:
    test_data = [[
        'Cleanup S-Cap', 1, 'Выделение'
    ], [
        'Evrogen FFPE', 3, 'Выделение'
    ], [
        'Evrogen new kit', 5, 'Выделение'
    ], [
        'miSeq 250PE micro', 4, 'NGS'
    ]
    ]

    usersDic = {
        121420608: 'i.mikhailov'
    }

    cur = conn.cursor()

    sqlDelete1 = """DROP TABLE IF EXISTS users"""
    sqlDelete2 = """DROP TABLE IF EXISTS reagents"""
    sqlDelete3 = """DROP TABLE IF EXISTS classes"""
    sqlDelete4 = """DROP TABLE IF EXISTS organizations""" 

    cur.execute(sqlDelete1)
    cur.execute(sqlDelete2)
    cur.execute(sqlDelete3)
    cur.execute(sqlDelete4)
    conn.commit()

    try:
        sql = """select * from users"""
        cur.execute(sql)

    except:

        sqlSetup1 = """CREATE TABLE IF NOT EXISTS organizations(
        organizationName text not null, 
        organizationID text not null unique);"""

        sqlSetup2 = """CREATE TABLE IF NOT EXISTS classes(
        className text not null, 
        classID text not null, 
        organizationID text not null, 
        FOREIGN KEY(organizationID) REFERENCES organizations(organizationID));
        """

        sqlSetup3 = """CREATE TABLE IF NOT EXISTS users(
        name text not null,
        userHash text not null unique, 
        userRights text not null,
        organizationID text not null,
        FOREIGN KEY(organizationID) REFERENCES organizations(organizationID));"""

        sqlSetup4 = """CREATE TABLE IF NOT EXISTS reagents(
        name text unique not null, 
        quantity integer, 
        alias text not null, 
        classID text not null, 
        organizationID text not null,
        FOREIGN KEY(classID) REFERENCES classes(classID),
        FOREIGN KEY(organizationID) REFERENCES organizations(organizationID));"""

        cur.execute(sqlSetup1)
        cur.execute(sqlSetup2)
        cur.execute(sqlSetup3)
        cur.execute(sqlSetup4)
        conn.commit()

    usersRows = []

    orgDefault = "INSERT OR REPLACE INTO organizations VALUES (?, ?)"
    hashOrg = hashlib.sha256(str('MIPT').encode('utf-8')).hexdigest()
    cur.execute(orgDefault, ('МФТИ ЦВГТ', hashOrg))
    print(cur.lastrowid)
    conn.commit()

    for user in usersDic:
        hash = hashlib.sha256(str(user).encode('utf-8')).hexdigest()
        row = [usersDic[user], hash, 'admin', hashOrg]
        sqlUsers = """INSERT OR REPLACE INTO users VALUES (?, ?, ?, ?)"""
        cur.execute(sqlUsers, row)
        print(cur.lastrowid)
        conn.commit()

    classSetup = list(set([row[-1] for row in test_data]))
    for item in classSetup:
        pair = (item, hashlib.sha256(str(item).encode('utf-8')).hexdigest()[:16], hashOrg)
        sql = """INSERT OR REPLACE INTO classes VALUES (?, ?, ?)"""
        cur.execute(sql, pair)
        conn.commit()

    for i in test_data:
        print(i, 'test data')
        classHash = """SELECT classID FROM classes WHERE className = (?) AND organizationID = (?)"""
        cur.execute(classHash, (i[-1], hashOrg))
        row = cur.fetchall()
        print(row[0][0], 'classID')
        hash = hashlib.sha256(str(i[0]).encode('utf-8')).hexdigest()[:16]
        sql = """INSERT OR REPLACE INTO reagents VALUES (?, ?, ?, ?, ?)"""
        print(i[0], i[1], hash, row[0][0], hashOrg)
        cur.execute(sql, (i[0], i[1], hash, row[0][0], hashOrg))
        print(cur.lastrowid, 'last row ID')
        conn.commit()
