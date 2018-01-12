

import getpass,re
import vault,pg

def getResponse(pType):
 while True:
    print("CHOOSE ACTION")
    print("1.Generate password")
    print("2.add account")
    print("3.search account")
    print("4.delete account")
    if pType==0:
        print("5.others")

    response=int(input())
    if response==1:
        length=int(input("\n Enter password length:"))
        uc=input("\n Include uppercase?(y/n):")
        lc=input("\n Include lowercase?(y/n):")
        num=input("\n Include numbers?(y/n):")
        sc=input("\n Include special chars?(y/n):")
        new_pass=pg.generatePassword(length,uc,lc,num,sc)
        print(new_pass)
    elif response==2:
        print("\n Add item")
        acc_source=input("Enter Title/URL: ")
        acc_login=input("Enter Username/Email: ")
        acc_password=getpass.getpass("Enter Password:")
        vault.addItem(acc_source,acc_login,acc_password,pType)

    elif response==3:
        print("Search item")
        items,length=vault.getList("search",pType)
        i=0
        print("NO\tACC_SOURCE")
        while(i<length):
            print(i+1,"\t",items[i][0])
            i+=1


        choice=int(input())

        source="".join(items[choice-1])
        acc=vault.searchItem(source,pType)
        if(pType==0):
            print("Username/Email\tPassword")
            for i in acc:
                print(i[0],'\t\t',i[1])

        elif(pType==1):
            print("Username/Email\t Password")
            for i in acc:
                print("{}\t \t{}".format(i['acc_login'],i['acc_password']))

    elif response==4:
        print("delete")
        items,length=vault.getList("delete",pType)
        i=0
        print("NO\tACC_SOURCE\t login")
        while(i<length):
            print(i+1,"\t",items[i][0],"\t\t",items[i][1])
            i+=1
        choice=int(input())
        source="".join(items[choice-1][0])
        login="".join(items[choice-1][1])
        vault.deleteItem(source,login,pType)

    elif response==5:
        print("\n 1.Update master password\n 2.update escape pin")
        ch=int(input())
        if ch==1:
            new_password=getpass.getpass("\n Enter new password")
            vault.updateMaster(new_password)
        else:
            pin=getpass.getpass("Enter escape pin")
            vault.updateEscPin(pin)
    elif response not in [1,5]:
        print("quit")
        break

if __name__ == '__main__':
    print("--------------PASSWORD VAULT--------------")
    status=vault.user_exists() #check if new user
    if(status==0):
        print("Create account to get Started!")            #default uname=sss and mpass=123
        username=input("USERNAME>")
        email=input("EMAIL>")
        password=getpass.getpass("MASTER PASSWORD>")
        vault.signup(username,email,password)
    elif(status==1):

        upassword=getpass.getpass("\n Enter master password\n")
        chk,pType=vault.authenticate(upassword)

        #authenticate user
        if chk == 0 :
            print("LOGIN SUCCESSFUL")
            getResponse(pType)
        else:
            print("SORRY!")
