import sqlite3
from passlib.hash import pbkdf2_sha256

class dataManager:
    def __init__(self):
        self.database = sqlite3.connect('ServerData.sql')
        #self.userDatabase = None
        self.cursor = self.database.cursor()

    def CreateNewDatabase(self):
        try:
            self.userDatabase = sqlite3.connect(self.database)
            self.cursor = self.userDatabase.cursor()
            self.cursor.execute('CREATE TABLE table_userAccounts (userName varchar(20), passWord varchar(20) )')

        except:
            print('failed to create DB')

    def OpenDatabase(self):
        try:
            self.userDatabase = sqlite3.connect(self.database)
            self.cursor = self.userDatabase.cursor()
        except:
            print('Failed to open DB')

    def AddAccount(self, userName, passWord):
        try:
            self.cursor.execute("select * from  Users where userName == '" + userName + "'")
            rows = self.cursor.fetchall()

            hash = pbkdf2_sha256.encrypt(passWord, rounds=200000, salt_size=16)

            if len(rows) == 0:
                self.cursor.execute('insert into Users(userName, passWord) values(?,?)',(userName,hash))
                self.database.commit()
                return True
            else:
                return False
        except:
            print('Failed to add to DB')
            return False

    def Login(self, userNameLogin, passWordLogin):
        try:
            self.cursor.execute("SELECT passWord FROM Users WHERE userName == '" + userNameLogin + "'")
            hash = self.cursor.fetchone()[0]

            if pbkdf2_sha256.verify(passWordLogin, hash):
                print("YOU HAVE LOGGED IN CONGRATS!")
                return True
            else:
                return False

        except:
            print('!ERROR WHEN TRYING TO LOGIN!')
            return False
