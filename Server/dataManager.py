import sqlite3
import json
import ast

class dataManager:
    def __init__(self):
        self.database = sqlite3.connect('ServerData.sql')
        self.cursor = self.database.cursor()

# =================== Login/Accounts Functions ========================= #
    def AddAccount(self, userName, passWord, salt):
        try:
            self.cursor.execute("select * from  Users where userName == '" + userName + "'")
            rows = self.cursor.fetchall()

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


# =================== Player Management Functions ========================= #
    def ListPlayersOwned(self, username):
        try:
            self.cursor.execute("SELECT * FROM players WHERE owner == '" + username + "'")
            playersOwned = self.cursor.fetchall()
            return playersOwned

            #for row in self.cursor:
            #    playerName = self.cursor.getString(self.cursor.getColumnIndex('playerName'))

        except:
            print('!ERROR WHEN TRYING TO GET PLAYERS!')
            return False

    def CreateNewPlayer(self, username, playerName, startRoom):
        try:
            self.cursor.execute("SELECT * FROM players WHERE playerName == '" + playerName + "'")
            rows = self.cursor.fetchall()

            if len(rows) == 0:
                self.cursor.execute('insert into players(playerName, owner, currentRoom, playerInventory) VALUES(?,?,?,?)',
                                    (playerName, username, startRoom, json.dumps([])))
                self.database.commit()
                return True
            else:
                return False
        except Exception as err:
            print('!ERROR WHEN TRYING TO CREATE A NEW PLAYER!:  ' + err)
            return False

    def PickPlayer(self, username, playerName):
        try:
            self.cursor.execute("SELECT * FROM players WHERE playerName == '" + playerName + "'" + " AND owner == '"
                                + username + "'")
            player = self.cursor.fetchone()

            if player is not None:
                return player
            else:
                return None
        except:
            print('!ERROR WHEN TRYING TO CREATE A NEW PLAYER!')
            return False

    def GetCurrentRoom(self, playerName):
        try:
            self.cursor.execute("SELECT currentRoom FROM players WHERE playerName == '" + playerName + "'")
            playerRoom = self.cursor.fetchone()

            if playerRoom is not None:
                return playerRoom[0]
            else:
                return None
        except:
            print('!ERROR WHEN TRYING TO CREATE A NEW PLAYER!')
            return False

    def UpdatePlayerRoom(self, playerName, newRoom):
        try:
            self.cursor.execute("SELECT * FROM players WHERE playerName == '" + playerName + "'")
            player = self.cursor.fetchone()

            if player:
                self.cursor.execute("UPDATE players SET currentRoom = '" + newRoom + "'" + " WHERE playerName == '" + playerName + "'")
                self.database.commit()
            else:
                return None
        except:
            print('!ERROR WHEN TRYING TO CREATE A NEW PLAYER!')
            return False

    def GetRoomInventory(self, currentRoom):
        self.cursor.execute("SELECT roomInventory FROM rooms WHERE roomName == '" + currentRoom + "'")
        roomInventory = self.cursor.fetchone()
        return ast.literal_eval(roomInventory[0])

    def UpdateRoomInventory(self, currentRoom, newInventory):
        self.cursor.execute("SELECT * FROM rooms WHERE roomName == '" + currentRoom + "'")
        room = self.cursor.fetchone()
        if room:
            self.cursor.execute("UPDATE rooms SET roomInventory = '" + json.dumps(newInventory) + "'" + " WHERE roomName == '" + currentRoom + "'")
            self.database.commit()

    def GetPlayerInventory(self, playerName):
        self.cursor.execute("SELECT playerInventory FROM players WHERE playerName == '" + playerName + "'")
        playerInventory = self.cursor.fetchone()
        return ast.literal_eval(playerInventory[0])

    def UpdatePlayerInventory(self, currentRoom, newInventory):
        self.cursor.execute("SELECT * FROM players WHERE playerName == '" + currentRoom + "'")
        room = self.cursor.fetchone()
        if room:
            self.cursor.execute("UPDATE players SET playerInventory = '" + json.dumps(newInventory) + "'" + " WHERE playerName == '" + currentRoom + "'")
            self.database.commit()

    # ================================================================================= #
    def createDatabase(self):
        self.createUserTable()
        self.createPlayerTable()
        self.createSpaceShipTable()
        self.createRoomsTable()
        #self.createSetRooms()
        print("Database setup")

    def createSetRooms(self):
        self.createRoom("Cock Pit",
                        "You are in the main controls room.\n"
                        "The pilot seat is at the front with many control panels surrounding it.\n"
                        "From here you can control and navigate the ship.",
                        ["book", "shrimp crackers", "pilot's hat"]
                        )
        self.createRoom("Main Deck",
                        "You are standing in the main deck of the ship.\n"
                        "There are many terminals around you.",
                        ["dinosaur figure"]
                        )
        self.createRoom("Medical Room",
                        "You are in the Medical room.\n"
                        "There are medical kits, band aides and red syringes in the room alongside a operation table",
                        ["medical kit", "band aide", "red syringe"]
                        )
        self.createRoom("Cargo Haul",
                        "You are in the Cargo Haul of the ship.\n"
                        "There are all sorts of worthless treasures in here.",
                        ["old alien relic", "locked box", "moldy banana"]
                        )
        self.createRoom("Armory",
                        "You are in the Armory.\n"
                        "There are laser rifles and plasma guns hanging on the walls.\n"
                        "you also notice a box withe the words -CAUTION EXPLOSIVES- on the side of it.",
                        ["laser rifle", "plasma gun", "thermal detonator", "hunting knife"]
                        )

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
                                playerName TEXT,
                                playerInventory TEXT)
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
                            roomDescription TEXT,
                            roomInventory TEXT
                            )
                            ''')
        # commit the change
        self.database.commit()

    # Creates a room with specific values
    def createRoom(self, roomName, roomDescription, roomInventory):
        roomInventory = json.dumps(roomInventory)
        self.cursor.execute('INSERT OR REPLACE into rooms(roomName, roomDescription, roomInventory) VALUES(?,?,?)',
                            (roomName, roomDescription, roomInventory))
        self.database.commit()
