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

cur = conn.cursor()

for i in test_data:
    sql = """INSERT OR REPLACE INTO reagents VALUES (?, ?)"""
    cur.execute(sql, (i[0], i[1]))
    hash = hashlib.sha256(str(i[0]).encode('utf-8')).hexdigest()[:16]
    sql2 = """INSERT OR REPLACE INTO aliases VALUES (?, ?, ?)"""
    cur.execute(sql2, (i[0], hash, i[2]))
    conn.commit()
    print(i[0])
    print(cur.lastrowid)
