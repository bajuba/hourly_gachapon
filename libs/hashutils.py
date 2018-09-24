import hashlib
import random
import string

def make_salt():
    return ''.join([random.choice(string.ascii_letters) for x in range(5)])

def make_pw_hash(password, salt=None):
    if not salt:
        salt = make_salt()
    hash = hashlib.sha256(unicode(password+salt)).hexdigest()
    #hash = hashlib.sha256(str.encode(password+salt)).hexdigest()
    return '{0},{1}'.format(salt,hash)


def check_pw_hash(password, hash):
    salt = hash.split(',')[0]
    if make_pw_hash(password, salt) == hash:
        return True
    return False
