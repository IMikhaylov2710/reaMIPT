import hashlib

def hashUser(userID):
    hash = hashlib.sha256(str(userID).encode('utf-8')).hexdigest()
    return hash
