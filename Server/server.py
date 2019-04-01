import sys
import time
import socket
import threading
import sqlite3
from commands import Commands
from player import player

import spaceShip

serverIsRunning: bool = True

players = []
users = {}
userLock = threading.Lock()

# Main space Ship of the game
ship = spaceShip.ship
ship.generateShip(spaceShip.ship, "RF-42 Centaur Cargo Ship")

# Main commands class
commands = Commands(players, ship)


# ========================= acceptThread ====================== #
def acceptThread(serverSocket):
    print("acceptThread running")
    while serverIsRunning:
        newSocket = serverSocket.accept()[0]
        newUser = player(newSocket, ship)
        userLock.acquire()

        # Add the new client to the ship and current room [main deck by default]
        players.append(newUser)

        newUser.loginStage = True

        # Login/new Account stage
        #while newClient.loginStage:
        newUser.addToOutQueue("WOULD YOU LIKE TO LOGIN OR CREATE AN ACCOUNT?\n"
                              "1: to login\n"
                              "2: to create a new account")

        ship.players = players
        newUser.currentRoom.players.append(newUser)

        # Announce to everyone that a new player has joined the ship
        commands.sendToEveryone(newUser.playerName + " Has Joined the crew!")

        users[newUser.clientSocket] = 0
        userLock.release()

        print("Added client!")


# =================== MAIN ========================= #
if __name__ == '__main__':
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    mySocket.bind(("127.0.0.1", 8222))
    mySocket.listen(5)

    acceptThread = threading.Thread(target=acceptThread, args=(mySocket, ))
    acceptThread.start()

    # Main Loop
    while serverIsRunning:
        commands.checkInputs()
