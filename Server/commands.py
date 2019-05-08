from dataManager import dataManager

class Commands:
    def __init__(self, users, spaceShip):
        self.users = users
        self.currentUser = None
        self.currentPlayer = None
        self.Input = None
        self.SqlData = dataManager()

        self.ship = spaceShip

        self.gameCommands = {"help": lambda: self.helpCommand(self.currentUser),
                             "look": lambda: self.lookCommand(self.currentUser),
                             # "newname": lambda: self.newNameCommand(self.currentUser, self.Input),
                             "move": lambda: self.moveCommand(self.currentUser, self.Input),
                             "say": lambda: self.sayInRoomCommand(self.Input),
                             "radio": lambda: self.radioCommand(self.Input),
                             "shipname": lambda: self.shipNameCommand(self.currentUser),
                             "take": lambda: self.takeItemCommand(self.currentUser, self.Input),
                             "drop": lambda: self.dropItemCommand(self.currentUser, self.Input),
                             "inventory": lambda: self.showInventoryCommand(self.currentUser),
                             "items": lambda: self.showItemsInRoom(self.currentUser)
                             }

        self.playerSelectCommands = {
                              "newplayer": lambda: self.CreateNewPlayer(self.currentUser, self.Input),
                              "pick": lambda: self.PickPlayer(self.currentUser, self.Input),
                              "joingame": lambda: self.JoinGame(self.currentUser)
                              }

        self.loginCommands = {"--!SaltCheck": lambda: self.saltCheck(self.currentUser, self.Input),
                              "--!Login": lambda: self.loginCommand(self.currentUser, self.Input),
                              "--!NewAccount": lambda: self.newAccountCommand(self.currentUser, self.Input)
                              }

# =================== INPUT PROCESSING ========================= #
    # Check all the Inputs coming in of each player to activate commands accordingly
    def checkInputs(self):
        for user in self.users:
            if user.clientIsConnected:
                self.currentUser = user
                self.currentPlayer = user.currentPlayer

                # Check to see if an input has actually been sent
                if user.inputQueue.qsize() > 0:

                    # ----- Login/Account commands ------
                    if user.state == user.STATE_LOGIN:
                        # splits up the input
                        self.Input = user.inputQueue.get()
                        self.Input = self.Input.split("#")

                        if self.Input[0] in self.loginCommands:
                            self.loginCommands[self.Input[0]]()

                        # If any input doesn't exist as a command
                        else:
                            user.addToOutQueue("ERROR --INVALID COMMAND--")

                    # ----- Player Selection commands ------
                    elif user.state == user.STATE_PLAYERSELECT:
                        # splits up the input and makes it all lower case
                        self.Input = user.inputQueue.get().lower().split(" ", 1)

                        if self.Input[0] in self.playerSelectCommands:
                            try:
                                self.playerSelectCommands[self.Input[0]]()
                            except Exception as err:
                                print(err)
                                user.addToOutQueue("ERROR --MISSING AN EXTRA INPUT--")

                        # If any input doesn't exist as a command
                        else:
                            user.addToOutQueue("ERROR --INVALID COMMAND--")

                    # ------ Game Commands -------
                    elif user.state == user.STATE_INGAME:
                            # splits up the input and makes it all lower case
                            self.Input = user.inputQueue.get().lower().split(" ", 1)

                            if self.Input[0] in self.gameCommands:
                                try:
                                    self.gameCommands[self.Input[0]]()
                                except Exception as err:
                                    user.addToOutQueue("ERROR --MISSING AN EXTRA INPUT--")
                                    print(err)

                            # If any input doesn't exist as a command
                            else:
                                user.addToOutQueue("ERROR --INVALID COMMAND--")
            else:
                self.users.remove(user)
                self.sendToEveryoneInGame(user.username + " Has Disconnected.")
                print(user.username + " Has Disconnected.")


# =================== Multi-Use Functions ========================= #
    # Send a message to every player in Game
    def sendToEveryoneInGame(self, message):
        for user in self.users:
            if user.state == user.STATE_INGAME:
                user.addToOutQueue(message)

    # Send a message to every client User
    def sendToEveryone(self, message):
        for user in self.users:
            user.addToOutQueue(message)

    # Send a message to every player in the same room
    def sendToEveryoneInRoom(self, message, PlayersInCurrentRoom):
        for player in PlayersInCurrentRoom:
            player.user.addToOutQueue(message)

# =================== Login Command Functions ========================= #
    def saltCheck(self, user, input):
        if self.SqlData.DoesUserAccountExist(input[1]):
            # Send salt back to client
            user.addToOutQueue("salt#" + self.SqlData.GetSalt(input[1]), True)
        else:
            user.addToOutQueue("Failed to login!\n"
                               "UserAccount: " + input[1] + " does not exist.")

    def loginCommand(self, user, input):
        alreadyLoggedIn = False

        for u in self.users:
            if u.username == input[1]:
                alreadyLoggedIn = True

        # Check username and password
        if self.SqlData.Login(input[1], input[2]):
            if not alreadyLoggedIn:

                user.addToOutQueue("YOU Have Logged in!")
                user.addToOutQueue("loginAccepted", True)
                user.username = input[1]
                user.addToOutQueue("updateUserName#" + user.username, True)
                self.EnterPlayerSelect(user)

            else:
                user.addToOutQueue("Failed to login!\n"
                                   "There is already a user logged in with this account.")
        else:
            user.addToOutQueue("Failed to login!\n"
                               "Incorrect username or password.")

    def newAccountCommand(self, player, input):
        player.addToOutQueue("YOU ARE TRYING TO CREATE A NEW ACCOUNT")

        if self.SqlData.AddAccount(input[1], input[2], input[3]):
            player.addToOutQueue("You have created an account")
        else:
            player.addToOutQueue("Failed to create an account.\n"
                                 "This user account might already exist")

# =================== Player Select Command Functions ========================= #
    def EnterPlayerSelect(self, user):
        user.state = user.STATE_PLAYERSELECT
        user.addToOutQueue("Welcome to the player creation and selection section\n"
                           "\nTo create a new player type the command: newPlayer [NameOfPlayer]\n"
                           "\nOr pick a currently existing player with the command: pick [NameOfPlayer]\n")

        self.DisplayAvailablePlayers(user)

    def DisplayAvailablePlayers(self, user):
        user.addToOutQueue("These are the players you have created and can pick from to play with:")
        playerList = self.SqlData.ListPlayersOwned(user.username)

        if len(playerList) < 1:
            user.addToOutQueue("\n- You do not yet own any players.\n"
                               "Create a new player with: newPlayer [NameOfPlayer]")
        else:
            for player in playerList:
                user.addToOutQueue("- " + str(player[3]) + " in " + str(player[2]))

    def CreateNewPlayer(self, user, input):
        user.addToOutQueue("\nCreating new player...")
        if self.SqlData.CreateNewPlayer(user.username, input[1], "Main Deck"):
            user.addToOutQueue("New player " + input[1] + " has been created!")
        else:
            user.addToOutQueue("ERROR - There is already a player that exists with that name.")

        self.DisplayAvailablePlayers(user)

    def PickPlayer(self, user, input):
        player = user.currentPlayer
        pickedPlayer = self.SqlData.PickPlayer(user.username, input[1])

        if pickedPlayer:
            user.addToOutQueue("Player " + str(pickedPlayer[3]) + " is selected\n"
                               "Enter: joingame to start")
            player.playerName = str(pickedPlayer[3])
            user.addToOutQueue("updatePlayerName#" + user.currentPlayer.playerName, True)

        elif pickedPlayer is None:
            user.addToOutQueue("This player doesn't exist")
        else:
            user.addToOutQueue("!-ERROR-!")

    def JoinGame(self, user):
        user.addToOutQueue("\nYOU ARE JOINING THE GAME...")
        user.state = user.STATE_INGAME
        nameOfSavedRoom = self.SqlData.GetCurrentRoom(user.currentPlayer.playerName)

        # add user to the ship
        user.currentPlayer.currentRoom = user.currentPlayer.currentSpaceShip.rooms[nameOfSavedRoom]
        user.currentPlayer.currentRoom.players.append(user.currentPlayer)
        user.addToOutQueue("updateRoom#" + user.currentPlayer.currentRoom.name, True)
        user.currentPlayer.inventory = self.SqlData.GetPlayerInventory(user.currentPlayer.playerName)


        # notifies everyone in game that a new player has joined
        self.sendToEveryoneInGame(user.currentPlayer.playerName + " has joined the crew!")


# =================== Game Command Functions ========================= #
    # Help command displays all the commands the player can write
    def helpCommand(self, player):
        player.addToOutQueue(
            "\n"
            "------------ COMMANDS LIST ------------\n"
            "help - lists all the commands\n"
            "say [words] - to say something to every other in the same room as you\n"
            "radio [words] - to say something to every other players\n"
            "look - to get a description of the room you are currently in\n"
            "move [front, back, left, right] - to move in the room in the corresponding direction\n"
            "shipname - will return the name of the Space ship\n"
            "take [item] - will take the item and put it in your inventory\n"
            "drop [item] - will drop the item from your inventory on to the floor of the room you are in\n"
            "inventory - will show you what you are holding in your inventory\n"
            "items - will show you what items you can pick up from the room\n"
            "--------------------------------------\n"
        )

    # Command that tells the player the name of the ship
    def shipNameCommand(self, player):
        player.addToOutQueue(self.currentPlayer.currentSpaceShip.name)

    # Command that allows the player to get a description of the room they are in
    def lookCommand(self, player):
        player.addToOutQueue(self.currentPlayer.currentRoom.description)

    # Command that allows the player to rename themselves
    def newNameCommand(self, player, Input):
        player.addToOutQueue("Your name was changed from " + self.currentPlayer.playerName + " to " + Input[1])
        self.currentPlayer.playerName = Input[1]

        player.addToOutQueue("updatePlayerName#" + player.currentPlayer.playerName, True)

    # Send a message to every player in the same room
    def sayInRoomCommand(self, Input):
        for player in self.currentPlayer.currentRoom.players:
            player.user.addToOutQueue(self.currentPlayer.playerName + " said: " + Input[1])

    # Send a message to every player in the spaceship using the radio
    def radioCommand(self, Input):
        for player in self.users:
            player.addToOutQueue("[" + self.currentPlayer.playerName + " RADIOTALK]: " + Input[1] + " - over")

    # Command that allows the player to move around the different rooms in the ship
    def moveCommand(self, user, Input):
        if Input[1] in self.currentPlayer.currentRoom.connectedRooms:
            oldRoom = self.currentPlayer.currentRoom
            newRoom = self.currentPlayer.currentRoom.connectedRooms[Input[1]]

            # removes the player from the current room
            self.currentPlayer.currentRoom.players.remove(self.currentPlayer)

            # announce that a player has left the current room
            self.sendToEveryoneInRoom(self.currentPlayer.playerName + " has left the room", oldRoom.players)

            # Move the player to the new Room
            self.currentPlayer.moveToRoom(self.ship.rooms[newRoom])
            self.SqlData.UpdatePlayerRoom(self.currentPlayer.playerName, self.currentPlayer.currentRoom.name)
            user.addToOutQueue("You have moved to: " + self.currentPlayer.currentRoom.name)

            # announce that a player has entered a new room
            self.sendToEveryoneInRoom(self.currentPlayer.playerName + " entered the room", self.currentPlayer.currentRoom.players)

            # adds the player to the new room
            self.currentPlayer.currentRoom.players.append(self.currentPlayer)

            # update room textbox on client
            user.addToOutQueue("updateRoom#" + user.currentPlayer.currentRoom.name, True)

        else:
            user.addToOutQueue("-- There is no room to move to in this direction --")

    def takeItemCommand(self, user, Input):
        print("YOU TOOK AN ITEM!")
        player = user.currentPlayer

        playerInventory = self.SqlData.GetPlayerInventory(player.playerName)
        roomInventory = self.SqlData.GetRoomInventory(player.currentRoom.name)
        if Input[1] in roomInventory:
            player.addItemToinventory(Input[1])
            roomInventory.remove(Input[1])
            self.SqlData.UpdateRoomInventory(player.currentRoom.name, roomInventory)
            playerInventory = player.inventory
            self.SqlData.UpdatePlayerInventory(player.playerName, playerInventory)

            user.addToOutQueue("You picked up the " + Input[1] + " and put it in your inventory")
        else:
            user.addToOutQueue("No such thing as a " + Input[1] + " in this room")


    def dropItemCommand(self, user, Input):
        print("player dropped AN ITEM!")
        player = user.currentPlayer

        playerInventory = self.SqlData.GetPlayerInventory(player.playerName)
        roomInventory = self.SqlData.GetRoomInventory(player.currentRoom.name)
        if Input[1] in player.inventory:
            player.removeItemFrominventory(Input[1])
            player.currentRoom.addItemToRoom(Input[1])
            roomInventory.append(Input[1])

            self.SqlData.UpdateRoomInventory(player.currentRoom.name, roomInventory)
            playerInventory = player.inventory
            self.SqlData.UpdatePlayerInventory(player.playerName, playerInventory)

            user.addToOutQueue("You dropped the " + Input[1] + " onto the floor")
        else:
            user.addToOutQueue("No such thing as a " + Input[1] + " in your inventory")

    def showInventoryCommand(self, user):
        print("Showing inventory to player " + self.currentPlayer.playerName)
        player = user.currentPlayer

        if len(player.inventory) > 0:
            user.addToOutQueue("The items you hold in your inventory:" + str(self.currentPlayer.inventory))
        else:
            user.addToOutQueue("Your inventory is currently empty :(")

    def showItemsInRoom(self, user):
        player = user.currentPlayer
        roomItems = self.SqlData.GetRoomInventory(player.currentRoom.name)
        user.addToOutQueue("The items in the room that you can take are: " + str(roomItems))

