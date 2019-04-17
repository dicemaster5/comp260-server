import sqlite3

class dataManager:
    def __init__(self):
        self.database = sqlite3.connect('ServerData.sql')
        self.cursor = self.database.cursor()

    def AddAccount(self, userName, passWord, salt):
        try:
            self.cursor.execute("select * from  Users where userName == '" + userName + "'")
            rows = self.cursor.fetchall()

            #hash = pbkdf2_sha256.encrypt(passWord, rounds=200000, salt_size=16)

            if len(rows) == 0:
                self.cursor.execute('insert into Users(userName, passWord, salt) VALUES(?,?,?)', (userName, passWord, salt))
                self.database.commit()
                return True
            else:
                return False
        except:
            print('Failed to add to DB')
            return False

    def DoesUserAccountExist(self, userNameLogin):
        try:
            self.cursor.execute("SELECT userName FROM users WHERE userName == '" + userNameLogin + "'")
            storedUserName = self.cursor.fetchone()[0]

            if userNameLogin == storedUserName:
                return True

            else:
                return False

        except:
            print('!ERROR WHEN TRYING TO LOGIN!')
            return False

    def GetSalt(self, userNameLogin):
        try:
            self.cursor.execute("SELECT salt FROM users WHERE userName == '" + userNameLogin + "'")
            storedSalt = self.cursor.fetchone()[0]
            return storedSalt

        except:
            print('!ERROR WHEN TRYING TO LOGIN!')
            return False

    def Login(self, userNameLogin, passWordLogin):
        try:
            self.cursor.execute("SELECT passWord FROM users WHERE userName == '" + userNameLogin + "'")
            storedPassword = self.cursor.fetchone()[0]

            if passWordLogin == storedPassword:
                return True

            else:
                return False

        except:
            print('!ERROR WHEN TRYING TO LOGIN!')
            return False

# ================================================================================= #
    def createDatabase(self):
        self.createUserTable()
        self.createPlayerTable()
        self.createSpaceShipTable()
        self.createRoomsTable()
        print("Database setup")


    # Create table to store all users
    def createUserTable(self):
        self.cursor.execute('''
                        CREATE TABLE IF NOT EXISTS users(
                        userName TEXT PRIMARY KEY, 
                        passWord TEXT, 
                        salt TEXT)
                        ''')
        # commit the change
        self.database.commit()

    # Create table to store all players
    def createPlayerTable(self):
        self.cursor.execute('''
                        CREATE TABLE IF NOT EXISTS players(
                        id INTEGER PRIMARY KEY, 
                        owner TEXT, 
                        currentRoom TEXT, 
                        playerName TEXT)
                        ''')
        # commit the change
        self.database.commit()

    # Create table to store all players
    def createSpaceShipTable(self):
        self.cursor.execute('''
                        CREATE TABLE IF NOT EXISTS spaceShip(
                        shipName TEXT PRIMARY KEY,
                        ShipHealth Int,
                        shipPosition INT,
                        PlayersInShip INT
                        )
                        ''')
        # commit the change
        self.database.commit()

    # Create table to store all players
    def createRoomsTable(self):
        self.cursor.execute('''
                            CREATE TABLE IF NOT EXISTS rooms(
                            roomName TEXT PRIMARY KEY,
                            roomDescription TEXT
                            )
                            ''')
        # commit the change
        self.database.commit()