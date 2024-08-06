import redis

redis_db = redis.StrictRedis(host='localhost', port=6379, db=0)

def flushRedis(hashedId):
    
    redis_db.set(f'newReagentAddition_{hashedId}', False)
    redis_db.set(f'newClass_{hashedId}', '')
    redis_db.set(f'newUserAddition_{hashedId}', False)
    redis_db.set(f'newUserRole_{hashedId}', '')

    return True