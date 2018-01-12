
import binascii
import hashlib
import sqlite3
import os,platform
import getpass
import pg,enc_dec

conn=sqlite3.connect('VAULT.db')
cursor=conn.cursor()

def clear():
    if(platform.system()=="Windows"):
        os.system('cls')
    else:
        os.system('clear')


def hash_password(password):
    salt=os.urandom(16)
    password=password.encode()
    dk=hashlib.pbkdf2_hmac('sha256',password,salt,300000)
    salt=binascii.hexlify(salt)
    dk=binascii.hexlify(dk)
    return salt,dk

def check_password(hashed_password,salt,user_password):
    user_password=user_password.encode()
    ck=hashlib.pbkdf2_hmac('sha256',user_password,salt,300000)

    if hashed_password==ck:
        return 0
    else:
        return -1

def signup(username,email,password):

    salt,dk=hash_password(password)

    conn.execute("INSERT INTO userdata(username,email,salt,password) values(?,?,?,?)",[username,email,salt,dk]);
    conn.commit()
    print("account created")

def authenticate(upassword):
    #upassword=getpass.getpass("ENTER MASTER PASSWORD:")
    cursor=conn.execute( "SELECT salt,password FROM userdata where pType=?",('0'));
    result=cursor.fetchall()
    for  salt,password in result:
        dbSalt=binascii.unhexlify(salt)
        dbPass=binascii.unhexlify(password)
        chk=check_password(dbPass,dbSalt,upassword)  #check password using check_password fn

    cursor=conn.execute( "SELECT salt,password FROM userdata where pType=?",('1'));
    result=cursor.fetchall()
    for  salt,password in result:
        dbSalt=binascii.unhexlify(salt)
        dbPass=binascii.unhexlify(password)
        chk1=check_password(dbPass,dbSalt,upassword)

    if(chk==0):
        return 0,0
    elif(chk1==0):
        return 0,1
    else:
        return -1,-1


def user_exists():

    #check if new user
    query="CREATE TABLE IF NOT EXISTS userdata(user_id INTEGER PRIMARY KEY AUTOINCREMENT,username varchar(25) NOT NULL,email varchar(25) NOT NULL,salt varchar(255) NOT NULL,password varchar(255) NOT NULL,pType tinyint default 0) "
    conn.execute(query);
    conn.commit()
    cursor=conn.execute("select * from userdata")
    result=cursor.fetchone()
    if(result is None):
        return 0
    else:
        return 1

def addItem(acc_source,acc_login,acc_password,pType):
    query="CREATE TABLE IF NOT EXISTS vault(aid INTEGER PRIMARY KEY AUTOINCREMENT,user_id INTEGER NOT NULL,acc_source varchar(100) NOT NULL,acc_login varchar(255) NOT NULL,iv varchar(255) ,acc_password varchar(500) NOT NULL,pType tinyint NOT NULL,foreign key(user_id) references userdata(user_id),foreign key(pType) references userdata(pType))"
    conn.execute(query);
    conn.commit()

    cursor=conn.execute("SELECT user_id,password FROM userdata where pType=?",(pType,))
    for row in cursor:
        uid=row[0]
        key=row[1]

    if(pType==0):
        substr=key[0:32]                        #use master password substring as key for encrypting pass
        ct,iv=enc_dec.encrypt(substr,acc_password)
        ct=binascii.hexlify(ct)
        iv=binascii.hexlify(iv)

        conn.execute("INSERT INTO vault(user_id,acc_source,acc_login,iv,acc_password,pType) values(?,?,?,?,?,?)",[uid,acc_source,acc_login,iv,ct,pType]);
        conn.commit()
        print("Added")
    elif(pType==1):
        conn.execute("INSERT INTO vault(user_id,acc_source,acc_login,acc_password,pType) values(?,?,?,?,?)",[uid,acc_source,acc_login,acc_password,pType]);
        conn.commit()
        print("d")

def updateMaster(new_password):
    new_salt,new_password=hash_password(new_password)

    conn.execute("""UPDATE userdata SET salt=? ,password=? WHERE pType= ?""",(new_salt,new_password,'0'))
    conn.commit()
    print("\n updated")


def updateEscPin(pin):
    salt,dk=hash_password(pin)
    cursor=conn.execute("select * from userdata where pType=1")
    result=cursor.fetchone()
    if(result is None):
        cursor=conn.execute("SELECT username,email FROM userdata where pType=0")
        for row in cursor:
            username=row[0]
            email=row[1]
        cursor=conn.execute("INSERT INTO userdata(username,email,salt,password,pType) values(?,?,?,?,?)",[username,email,salt,dk,1]);
        conn.commit()
    else:
        conn.execute("UPDATE userdata SET salt=?,password=? where pType=?",(salt,dk,1));
        conn.commit()

def getList(string,ptype):

    if string=="search":
        cursor=conn.execute("SELECT distinct acc_source from vault where pType=?",(ptype,))
        acc=cursor.fetchall()
        length=len(acc)
        return acc,length
    elif string=="delete":
        cursor=conn.execute("SELECT acc_source,acc_login from vault where pType=?",(ptype,))
        acc=cursor.fetchall()
        length=len(acc)
        return acc,length

def searchItem(source,pType):
    if(pType==0):
        login_list=[]
        iv_list=[]
        ct_list=[]
        pt_list=[]
        cursor=conn.execute("SELECT user_id,acc_login,iv,acc_password from vault where acc_source=? and pType=?",(source,pType))
        result=cursor.fetchall()
        number_of_acc=len(result)
        print(number_of_acc)
        for row in result:
            user_id=row[0]
            acc_login=row[1]
            iv=row[2]
            acc_password=row[3]

            login_list.append(acc_login)
            iv_list.append(binascii.unhexlify(iv))
            ct_list.append(binascii.unhexlify(acc_password))

        cursor=conn.execute("SELECT password from userdata where user_id=? and pType=?",(user_id,pType))
        for password in cursor.fetchone():
            mpass=password
            key=mpass[0:32]
        plain_text=[]
        for i in range(number_of_acc):
            pt=enc_dec.decrypt(key,iv_list[i],ct_list[i])
            plain_text.append(pt.rstrip('\x00'))
        items=list(zip(login_list,plain_text))
        return items



    elif(pType==1):
        cursor=conn.execute("SELECT acc_login,acc_password from vault where acc_source=? and pType=?",(source,pType))
        items=[dict(zip(['acc_login','acc_password'],row)) for row in cursor.fetchall()]
    return items

def deleteItem(source,login,pType):
    cursor=conn.execute("DELETE from vault where acc_source=? and acc_login=? and pType=?",(source,login,pType))
    conn.commit()
    clear()



if __name__ == '__main__':
