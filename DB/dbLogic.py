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

#done
def handleRequest(callbackData, conn, organizationID):

    with conn:
        callDataSplit = callbackData.split('|')
        hash = callDataSplit[1]
        toDo = callDataSplit[0]
        cur = conn.cursor()
        if toDo == 'reapush':
            sql = """UPDATE reagents SET quantity = quantity + 1 
                    WHERE reagentID = (?)
                    AND organizationID = (?)
                    """
            cur.execute(sql, (hash, organizationID))
            conn.commit()

        elif toDo == 'reapull':
            sql = """UPDATE reagents SET quantity = quantity - 1 
                    WHERE reagentID = (?)
                    AND organizationID = (?)
                    """
            cur.execute(sql, (hash, organizationID))
            conn.commit()

        else:

            return 'Этого реагента пока нет в базе'

#done   
def handleRequestInfo(conn, callbackData, userID):

    callDataSplit = callbackData.split('|')
    hash = callDataSplit[1]
    hashedID = hashUser(userID)
    with conn:
        cur = conn.cursor()
        sqlResult = """SELECT * FROM reagents INNER JOIN users ON users.organizationID = reagents.organizationID WHERE reagentID = (?) AND userID = (?)"""
        cur.execute(sqlResult, (hash, hashedID))
        row = cur.fetchall()

    return row

#done
def getClasses(conn, userID):

    hashedID = hashUser(userID)

    cur = conn.cursor()
    sql = """SELECT DISTINCT classes.className, classes.classID FROM classes INNER JOIN reagents ON reagents.classID = classes.classID INNER JOIN users ON reagents.organizationID = users.organizationID WHERE users.userID = (?) ORDER BY classes.className"""
    cur.execute(sql, (hashedID))
    row = cur.fetchall()

    return row

#done
def getQuantityByClass(conn, classForFetch, userID):

    hashedID = hashUser(userID)

    cur = conn.cursor()
    sql = """SELECT name, quantity FROM reagents INNER JOIN classes ON classes.classID = reagents.classID INNER JOIN users ON users.organizationID = reagents.organizationID WHERE className = (?) and reagents.userID = (?) """
    cur.execute(sql, (classForFetch, hashedID))
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

def getMyOrganization(conn, userID):
    with conn:
        cur = conn.cursor()
        sql = """SELECT organizationID FROM users WHERE userHash = (?)"""
        cur.execute(sql, (hashUser(userID)))
        row = cur.fetchall()
        print(row)

    return row

def getUsers(conn, organization):
    with conn:
        cur = conn.cursor()
        sql = """SELECT * from USERS where organizationID = (?)"""
        cur.execute(sql)
        row = cur.fetchall()
        print(row)
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

def checkInvitationLink(conn, link, userID):

    with conn:
        cur = conn.cursor()
        hash = hashUser(userID)

        sql = """SELECT EXISTS(SELECT * FROM quotes WHERE welcomeLink=(?))"""
        cur.execute(sql, (link, ))

        result = cur.fetchone()

        if result[0] == 1:
            return True
        else:
            return False
        
def checkUserValidity(conn, userID):

    with conn:
        cur = conn.cursor()
        hash = hashUser(userID)

        sql = """SELECT EXISTS(SELECT * FROM users WHERE userID=(?))"""
        cur.execute(sql, (hash, ))

        result = cur.fetchone()[0]

        if result == 1:
            return True
        else:
            return False
        
def checkAdminRights(conn, userID):

    hash = hashUser(userID)

    with conn:

        cur = conn.cursor()
        sql = """SELECT EXISTS(SELECT * FROM users WHERE userID=(?))"""
        cur.execute(sql, (hash, ))
        result = cur.fetchone()[0]
        print(sql, hash, result)

        if result == 1:
            sql2 = """SELECT userRights FROM users WHERE userID = (?)"""
            cur.execute(sql2, (hash, ))
            print(sql2, hash)

            result = cur.fetchone()[0]
            print(result)
            if result == 'admin':
                return 'admin'
            elif result == 'user':
                return 'user'
            else:
                return 'none'
        else:
            return 'none'
