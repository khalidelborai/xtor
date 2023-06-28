import binascii
import hashlib
import os
import socket


def getTorPassHash(sectretPassword="passw0rd"):
    """
    This function is used to generate a hashed password for tor control port authentication.

        https://stackoverflow.com/a/67198518
    """
    # python v3  working
    # static 'count' value later referenced as "c"
    indicator = chr(96)
    # generate salt and append indicator value so that it
    salt = "%s%s" % (os.urandom(8), indicator)  # this will be working
    c = ord(indicator)
    # salt = "%s%s" % (codecs.encode(os.urandom(4), 'hex').decode(), indicator) #this will be working
    # c = ord(salt[8])
    # salt = "%s%s" % (codecs.encode(os.urandom(8), 'hex').decode(), indicator) #this will be working
    # c = ord(salt[16])
    # generate an even number that can be divided in subsequent sections. (Thanks Roman)
    EXPBIAS = 6
    count = (16 + (c & 15)) << ((c >> 4) + EXPBIAS)
    d = hashlib.sha1()
    # take the salt and append the password
    tmp = salt[:8] + sectretPassword
    # hash the salty password
    slen = len(tmp)
    while count:
        if count > slen:
            d.update(tmp.encode("utf-8"))
            count -= slen
        else:
            d.update(tmp[:count].encode("utf-8"))
            count = 0
    hashed = d.digest()
    saltRes = binascii.b2a_hex(salt[:8].encode("utf-8")).upper().decode()
    indicatorRes = binascii.b2a_hex(indicator.encode("utf-8")).upper().decode()
    torhashRes = binascii.b2a_hex(hashed).upper().decode()
    hashedControlPassword = "16:" + str(saltRes) + str(indicatorRes) + str(torhashRes)
    return hashedControlPassword


def checkPort(port: int, host:str) -> bool:
    """
    Check if port is in use
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((host, port))
    return result != 0
