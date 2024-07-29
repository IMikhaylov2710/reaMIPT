import hashlib
import emoji

def hashUser(userID):
    hash = hashlib.sha256(str(userID).encode('utf-8')).hexdigest()
    print(hash)
    return hash

def isEmoji(text):
    if emoji.is_emoji(text):
        return True
    else:
        return False
    
def makeTextFromEmoji(text):
    return emoji.demojize(text)

def makeEmojiFromText(text):
    return emoji.emojize(text)