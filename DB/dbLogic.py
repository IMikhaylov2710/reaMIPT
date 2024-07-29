import hashlib

def hashUser(userID):
    hash = hashlib.sha256(str(userID).encode('utf-8')).hexdigest()
    return hash

def getOrganizationByUser(conn, userID):
    hash = hashlib.sha256(str(userID).encode('utf-8')).hexdigest()
    with conn:
        cur = conn.cursor()
        sql = """SELECT organizations.organizationName FROM users INNER JOIN organizations ON organizations.organizationID = users.organizationID WHERE userHash = (?);"""
        cur.execute(sql, (hash, ))
        row = cur.fetchone()

    return row

def getAllUsersOfOrganization(conn, userID):
    return print('this will return all users from your organization')

#refactoring
def handleRequest(callbackData, conn):

    with conn:
        callDataSplit = callbackData.split('|')
        hash = callDataSplit[1]
        toDo = callDataSplit[0]
        cur = conn.cursor()
        cur.execute("""select * from reagents where alias = ?""", (hash, ))
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
                        WHERE name = (?)
                        """
                cur.execute(sql, (row[0], ))
                conn.commit()

        else:

            return 'Этого реагента пока нет в базе'

#refactoring   
def handleRequestInfo(callbackData, conn):

    callDataSplit = callbackData.split('|')
    hash = callDataSplit[1]
    with conn:
        cur = conn.cursor()
        sqlResult = """SELECT * FROM reagents INNER JOIN aliases on reagents.name = aliases.name WHERE alias = (?)"""
        cur.execute(sqlResult, (hash,))
        row = cur.fetchall()

    return row

def getClasses(conn):

    cur = conn.cursor()
    sql = """SELECT DISTINCT classID FROM classes"""
    cur.execute(sql)
    row = cur.fetchall()

    return row

#minor refactoring
def getQuantityByClass(conn, classForFetch):

    cur = conn.cursor()
    sql = """SELECT name, quantity FROM reagents WHERE class = (?)"""
    cur.execute(sql, classForFetch)
    row = cur.fetchall()

    return row

def createNewAlias(name, conn):

    cur = conn.cursor()
    '''cur.execute("""SELECT * FROM aliases WHERE name = (?) """, (name,))
    row = cur.fetchone()'''
    m = hashlib.sha256(name).hexdigest()[:16]
    sql = """INSERT INTO aliases(name,alias)
            VALUES(?,?)"""
    cur = conn.cursor()
    cur.execute(sql, (name, m))
    conn.commit()

    return cur.lastrowid

#refactoring
def getItemsByClass(conn, className):
    with conn:
        cur = conn.cursor()
        sql = """select reagents.name, reagents.quantity from aliases inner join reagents on reagents.name = aliases.name where class=(?)"""
        cur.execute(sql, (className, )) 
        row = cur.fetchall()
        result = '\n'.join([str(el[0])+'\t'+str(el[1]) for el in row])

    return result

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

#refactoring
def createNewDBinstance(conn, name, className):

    with conn:
        cur = conn.cursor()
        hash = hashlib.sha256(str(name).encode('utf-8')).hexdigest()[:16]
        sql = """INSERT INTO aliases VALUES (?, ?, ?)"""
        cur.execute(sql, (name, hash, className))

        sql2 = """INSERT INTO reagents VALUES (?, ?)"""
        cur.execute(sql2, (name, 0))

        conn.commit()