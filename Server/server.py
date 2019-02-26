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
ship.generateShip(spaceShip.ship, "SpaceShipGOGO")


# ========================= THREADING CODE ====================== #

def acceptThread(serverSocket):
    print("acceptThread running")
    while True:
        newSocket = serverSocket.accept()[0]
        newClient = client(newSocket, ship)

        clientsLock.acquire()
        players.append(newClient)
        ship.players = players
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

            if Input == "help":
                player.outputQueue.put(
                                        "----------- COMMANDS LIST -----------\n"
                                        "help - lists all the commands\n"
                                        "say [words] - to say something to every other players\n"
                                        "newname [name] - To change your name\n"
                                        "look - to get a description of the room you are currently in\n"
                                        "move [front, back, left, right] - to move in the room in the corresponding "
                                        "direction\n"
                                        "-------------------------------------\n"
                                       )
            elif Input == "look":
                player.outputQueue.put(player.currentRoom.description)

            elif Input == "shipname":
                player.outputQueue.put(player.currentSpaceShip.name)

            else:
                Input = Input.split(" ", 1)
                if Input[0] == "say":
                    sendToEveryone(player.playerName + " said: " + Input[1])

                elif Input[0] == "newname":
                    player.outputQueue.put("Your name was changed from " + player.playerName + " to " + Input[1])
                    player.playerName = Input[1]

                elif Input[0] == "move":
                    directions = ["front", "back", "left", "right"]
                    player.moveToRoom(directions.index(Input[1]))
                    player.outputQueue.put("You have moved to: " + player.currentRoom.name)

                    #print(player.currentRoom.connectedRooms)


                else:
                    player.outputQueue.put("--INVALID COMMAND--")


# Send a message to every player
def sendToEveryone(message):
    for player in players:
        player.outputQueue.put(message)


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