import sys
from queue import *
# from commands import *
import time
import socket
import threading
from client import client

import spaceShip

#########
playerName: str
userInput: str
output: str = "null"
#clientID = 0

serverIsRunning: bool = True

#globalInputQueue = Queue()
#outputQueue = Queue()

players = []
clients = {}
clientsLock = threading.Lock()

# Main space Ship of the game
ship = spaceShip.ship
ship.generateShip(spaceShip.ship, "RF-42 Centaur Cargo Ship")


# ========================= THREADING CODE ====================== #

def acceptThread(serverSocket):
    print("acceptThread running")
    while True:
        newSocket = serverSocket.accept()[0]
        newClient = client(newSocket, ship)

        clientsLock.acquire()
        players.append(newClient)
        ship.players = players

        newClient.currentRoom.players.append(newClient)
        sendToEveryone(newClient.playerName + " Has Joined the crew!")

        clients[newClient.clientSocket] = 0
        clientsLock.release()

        print("Added client!")

# =================== INPUT PROCESSING ========================= #


# Check all the Inputs coming in or each player
def checkInputs():
    for player in players:
        if player.inputQueue.qsize() > 0:
            print("Checking Inputs")

            Input = player.inputQueue.get().lower()
            Input = Input.split(" ", 1)

            if Input[0] == "help":
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
            elif Input[0] == "look":
                player.addToOutQueue(player.currentRoom.description)

            elif Input[0] == "shipname":
                player.addToOutQueue(player.currentSpaceShip.name)

            #------ Double input check ----------#
            elif len(Input) < 2 or Input[1] is "":
                player.addToOutQueue("ERROR -- this command needs more input")

            elif Input[0] == "say":
                talkInRoom(player.playerName + " said: " + Input[1], player.currentRoom.players)

            elif Input[0] == "radio":
                sendToEveryone("[" + player.playerName + " RADIOTALK]: " + Input[1] + " - over")

            elif Input[0] == "newname":
                player.addToOutQueue("Your name was changed from " + player.playerName + " to " + Input[1])
                player.playerName = Input[1]

            elif Input[0] == "move":
                if Input[1] in player.currentRoom.connectedRooms:
                    oldRoom = player.currentRoom
                    newRoom = player.currentRoom.connectedRooms[Input[1]]

                    # removes the player from the current room
                    player.currentRoom.players.remove(player)

                    # announce that a player has left the current room
                    talkInRoom(player.playerName + " has left the room", oldRoom.players)

                    # Move the player to the new Room
                    player.moveToRoom(ship.rooms[newRoom])
                    player.addToOutQueue("You have moved to: " + player.currentRoom.name)

                    # announce that a player has entered a new room
                    talkInRoom(player.playerName + " entered the room", player.currentRoom.players)

                    # adds the player to the new room
                    player.currentRoom.players.append(player)

                else:
                    player.addToOutQueue("-- There is no room to move to in this direction --")
            else:
                player.addToOutQueue("--INVALID COMMAND--")


# Send a message to every player
def sendToEveryone(message):
    for player in players:
        player.addToOutQueue(message)

# Send a message to every player in the same room
def talkInRoom(message, PlayersInCurrentRoom):
    for player in PlayersInCurrentRoom:
        player.addToOutQueue(message)

# =================== MAIN ========================= #

if __name__ == '__main__':
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    mySocket.bind(("127.0.0.1", 8222))
    mySocket.listen(5)

    acceptThread = threading.Thread(target=acceptThread, args=(mySocket, ))
    acceptThread.start()

    # Main Loop
    while serverIsRunning:
        checkInputs()