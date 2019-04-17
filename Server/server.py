import sys
import time
import socket
import threading
import sqlite3

from commands import Commands
from dataManager import dataManager
from user import user
from player import player
import spaceShip

serverIsRunning: bool = True

players = []
users = []
userLock = threading.Lock()

# Main space Ship of the game
ship = spaceShip.ship
ship.generateShip(spaceShip.ship, "RF-42 Centaur Cargo Ship")

# Main commands class
commands = Commands(users, ship)
dataManager = dataManager()

# ========================= acceptThread ====================== #
def acceptThread(serverSocket):
    print("acceptThread running")
    while serverIsRunning:
        newSocket = serverSocket.accept()[0]
        newUser = user(newSocket, ship)
        userLock.acquire()

        # Add the new client to the ship and current room [main deck by default]
        users.append(newUser)

        players.append(newUser.currentPlayer)

        newUser.addToOutQueue("You are connected to the server!\n"
                              "Please use the Login Panel to either login or create a new account.")

        userLock.release()

        print("Added client!")


# =================== MAIN ========================= #
if __name__ == '__main__':
    dataManager.createDatabase()

    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    mySocket.bind(("127.0.0.1", 8222))
    mySocket.listen(5)

    acceptThread = threading.Thread(target=acceptThread, args=(mySocket, ))
    acceptThread.start()

    # Main Loop
    while serverIsRunning:
        commands.checkInputs()
