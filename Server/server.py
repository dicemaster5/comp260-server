import sys
import time
import socket
import threading
from commands import CommandBase
from client import client

import spaceShip

serverIsRunning: bool = True

players = []
clients = {}
clientsLock = threading.Lock()

# Main space Ship of the game
ship = spaceShip.ship
ship.generateShip(spaceShip.ship, "RF-42 Centaur Cargo Ship")

# Main commands class
commands = CommandBase(players, ship)

# ========================= acceptThread ====================== #
def acceptThread(serverSocket):
    print("acceptThread running")
    while serverIsRunning:
        newSocket = serverSocket.accept()[0]
        newClient = client(newSocket, ship)
        clientsLock.acquire()

        # Add the new client to the ship and current room [main deck by default]
        players.append(newClient)
        ship.players = players
        newClient.currentRoom.players.append(newClient)

        # Announce to everyone that a new player has joined the ship
        commands.sendToEveryone(newClient.playerName + " Has Joined the crew!")

        clients[newClient.clientSocket] = 0
        clientsLock.release()

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