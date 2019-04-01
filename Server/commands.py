class Commands:
    def __init__(self, players, spaceShip):
        self.players = players
        self.currentPlayer = None
        self.Input = None

        self.ship = spaceShip

        self.gameCommands = {"help": lambda: self.helpCommand(self.currentPlayer),
                             "look": lambda: self.lookCommand(self.currentPlayer),
                             "newname": lambda: self.newNameCommand(self.currentPlayer, self.Input),
                             "move": lambda: self.moveCommand(self.currentPlayer, self.Input),
                             "say": lambda: self.sayInRoomCommand(self.currentPlayer, self.Input),
                             "radio": lambda: self.radioCommand(self.Input),
                             "shipname": lambda: self.shipNameCommand(self.currentPlayer)
                             }

        self.loginCommands = {"1": lambda: self.loginCommand(self.currentPlayer),
                              "2": lambda: self.newAccountCommand(self.currentPlayer)
                              }

# =================== INPUT PROCESSING ========================= #
    # Check all the Inputs coming in of each player to activate commands accordingly
    def checkInputs(self):
        for player in self.players:
            self.currentPlayer = player

            if player.inputQueue.qsize() > 0:

                # splits up the input
                self.Input = player.inputQueue.get().lower().split(" ", 1)

                # Login/Account commands
                if player.loginStage and self.Input[0] in self.loginCommands:
                    self.loginCommands[self.Input[0]]()

                # Game Commands
                elif player.gameStage and self.Input[0] in self.gameCommands:
                    try:
                        self.gameCommands[self.Input[0]]()
                    except:
                        player.addToOutQueue("ERROR --MISSING AN EXTRA INPUT--")

                # If any input doesn't exist as a command
                else:
                    player.addToOutQueue("ERROR --INVALID COMMAND--")

# =================== Multi-Use Functions ========================= #
    # Send a message to every player in the spaceship
    def sendToEveryone(self, message):
        for player in self.players:
            player.addToOutQueue(message)

    # Send a message to every player in the same room
    def sendToEveryoneInRoom(self, message, PlayersInCurrentRoom):
        for player in PlayersInCurrentRoom:
            player.addToOutQueue(message)

# =================== Login Command Functions ========================= #
# Help command displays all the commands the player can write
    def loginCommand(self, player):
        player.addToOutQueue("YOU ARE TRYING TO LOGIN")
        player.addToOutQueue("YOU Have Logged in!")
        player.loginStage = False
        player.gameStage = True

    def newAccountCommand(self, player):
        player.addToOutQueue("YOU ARE TRYING TO CREATE A NEW ACCOUNT")

# =================== Game Command Functions ========================= #
    # Help command displays all the commands the player can write
    def helpCommand(self, player):
        player.addToOutQueue(
            "----------- COMMANDS LIST -----------\n"
            "help - lists all the commands\n"
            "say [words] - to say something to every other in the same room as you\n"
            "radio [words] - to say something to every other players\n"
            "newname [name] - To change your name\n"
            "look - to get a description of the room you are currently in\n"
            "move [front, back, left, right] - to move in the room in the corresponding "
            "direction\n"
            "shipname - will return the name of the Space ship\n"
            "-------------------------------------\n"
        )

    # Command that tells the player the name of the ship
    def shipNameCommand(self, player):
        player.addToOutQueue(player.currentSpaceShip.name)

    # Command that allows the player to get a description of the room they are in
    def lookCommand(self, player):
        player.addToOutQueue(player.currentRoom.description)

    # Command that allows the player to rename themselves
    def newNameCommand(self, player, Input):
        player.addToOutQueue("Your name was changed from " + player.playerName + " to " + Input[1])
        player.playerName = Input[1]

    # Send a message to every player in the same room
    def sayInRoomCommand(self, thisPlayer, Input):
        for player in thisPlayer.currentRoom.players:
            player.addToOutQueue(thisPlayer.playerName + " said: " + Input[1])

    # Send a message to every player in the spaceship using the radio
    def radioCommand(self, Input):
        for player in self.players:
            player.addToOutQueue("[" + player.playerName + " RADIOTALK]: " + Input[1] + " - over")

    # Command that allows the player to move around the different rooms in the ship
    def moveCommand(self, player, Input):
        if Input[1] in player.currentRoom.connectedRooms:
            oldRoom = player.currentRoom
            newRoom = player.currentRoom.connectedRooms[Input[1]]

            # removes the player from the current room
            player.currentRoom.players.remove(player)

            # announce that a player has left the current room
            self.sendToEveryoneInRoom(player.playerName + " has left the room", oldRoom.players)

            # Move the player to the new Room
            player.moveToRoom(self.ship.rooms[newRoom])
            player.addToOutQueue("You have moved to: " + player.currentRoom.name)

            # announce that a player has entered a new room
            self.sendToEveryoneInRoom(player.playerName + " entered the room", player.currentRoom.players)

            # adds the player to the new room
            player.currentRoom.players.append(player)

        else:
            player.addToOutQueue("-- There is no room to move to in this direction --")

