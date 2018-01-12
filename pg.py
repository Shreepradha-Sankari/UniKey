import string
import secrets
import random

upperCase=string.ascii_uppercase
lowerCase=string.ascii_lowercase
digits=string.digits
punctuation=string.punctuation

def generatePassword(length,uc,lc,num,sc):

    charSet=[]
    if(uc=='y'):
        charSet.append(upperCase)
    if(lc=='y'):
        charSet.append(lowerCase)
    if(num=='y'):
        charSet.append(digits)
    if(sc=='y'):
        charSet.append(punctuation)
    else:
        print("Sorry! no password generated")


    pw=''.join([getChar(charSet) for _ in range(length)])
    return pw

def getChar(charSet):

    char=secrets.choice(secrets.choice(charSet))
    return char
