import hashlib

def hashUser(userID):
    hash = hashlib.sha256(str(userID).encode('utf-8')).hexdigest()
    return hash

def handleRequest(callbackData, conn):

    with conn:
        callDataSplit = callbackData.split('|')
        hash = callDataSplit[1]
        toDo = callDataSplit[0]
        cur = conn.cursor()
        cur.execute("""select * from aliases where alias = ?""", (hash, ))
        row = cur.fetchone()
        if row:
            if toDo == 'push':
                sql = """INSERT INTO reagents VALUES (?, ?)
                ON CONFLICT(name) DO UPDATE
                SET quantity = quantity + 1"""
                cur.execute(sql, (row[0], 1))
                conn.commit()

            elif toDo == 'pull':
                sql = """UPDATE reagents SET quantity = quantity - 1 
                        WHERE name = '%s'
                        """ % row[0]
                cur.execute(sql)
                conn.commit()

        else:

            return 'Этого реагента пока нет в базе'
        
def handleRequestInfo(callbackData, conn):

    callDataSplit = callbackData.split('|')
    hash = callDataSplit[1]
    with conn:
        cur = conn.cursor()
        sqlResult = """SELECT * FROM reagents INNER JOIN aliases on reagents.name = aliases.name WHERE alias = '%s'""" % hash
        cur.execute(sqlResult)
        row = cur.fetchall()

    return row

def getClasses(conn):

    cur = conn.cursor()
    sql = """SELECT DISTINCT class FROM aliases"""
    cur.execute(sql)
    row = cur.fetchall()

    return row

def getQuantityByClass(conn, classForFetch):

    cur = conn.cursor()
    sql = """SELECT * FROM aliases WHERE class = (?)"""
    cur.execute(sql, classForFetch)
    row = cur.fetchall()

    return row

def createNewAlias(name, conn):

    cur = conn.cursor()
    cur.execute("""SELECT * FROM aliases WHERE name =?""", name)
    row = cur.fetchone()
    if row:

        return cur.lastowid
    else:
        m = hashlib.sha256(name).hexdigest()
        sql = """INSERT INTO aliases(name,alias)
              VALUES(?,?)"""
        cur = conn.cursor()
        cur.execute(sql, (name, m))
        conn.commit()

        return cur.lastrowid

def getItemsByClass(className, conn):
    with conn:
        cur = conn.cursor()
        sql = "select name, alias from aliases where class='%s'" % className
        cur.execute(sql) 
        row = cur.fetchall()

    return row

def getUsers(conn):
    with conn:
        cur = conn.cursor()
        sql = """select * from users"""
        cur.execute(sql)
        row = cur.fetchall()

    return row

def addUser(conn, userID, name, role):

    hash = hashUser(userID)
    with conn:
        cur = conn.cursor()
        sql = """INSERT INTO users VALUES (?, ?, ?)"""
        cur.execute(sql, (name, hash, role))
    conn.commit()

def removeUser(conn, name):

    with conn:
        cur = conn.cursor()
        sql = """DELETE FROM users WHERE name = (?)"""
        cur.execute(sql, name)
    conn.commit()
