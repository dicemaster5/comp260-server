import sys
from queue import *
# from commands import *
import time
import socket
import threading
from client import client

#########
playerName: str
userInput: str
output: str = "null"
#clientID = 0

serverIsRunning: bool = True

globalInputQueue = Queue()
#outputQueue = Queue()

players = []
clients = {}
clientsLock = threading.Lock()

# ========================= THREADING CODE ====================== #

def acceptThread(serverSocket):
    print("acceptThread running")
    while True:
        newSocket = serverSocket.accept()[0]
        newClient = client(newSocket)

        clientsLock.acquire()
        players.append(newClient)
        clients[newClient.clientSocket] = 0
        clientsLock.release()

        print("Added client!")

# =================== INPUT PROCESSING ========================= #

# Check all the Inputs coming in or each player
def checkInputs():
    for player in players:
        if player.inputQueue.qsize() > 0:
            print("Checking Inputs")

            Input = player.inputQueue.get()

            if Input == "help":
                player.outputQueue.put("--HELP COMMAND--\n say [words] - to say something to every other player\n newname [name] - To change your name")

            else:
                Input = Input.split(" ", 1)
                if Input[0] == "say":
                    sendToEveryone(player.playerName + " said " + Input[1])

                elif Input[0] == "newname":
                    player.outputQueue.put("Your name was changed from " + player.playerName + " to " + Input[1])
                    player.playerName = Input[1]

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
        #while inputQueue.qsize() > 0:
        #   print("hi")

######################################

"""
def sendOutput(outPutMessage: str):
    print("Sending Output Message: " + "|" + outPutMessage + "|")
    client[0].send(outPutMessage.encode())


def recievedInput():
    data = client[0].recv(4096)
    global userInput
    userInput = (data.decode("utf-8"))
    print("Received Input Message: " + "|" + userInput + "|")


def go():
    sendOutput("which direction will you go in?:")
    sendOutput("NORTH/SOUTH/EAST/WEST")
    recievedInput()
    if userInput == "north":
        sendOutput("You enter the room to the north.")


def look():
    sendOutput("You are in a small room.")


def help():
    sendOutput ("*-------------------------------------------*\n"
                "Here is the List of commands you can enter\n"
                "go: to go to a new location/room\n"
                "look: to get a description of your environment\n"
                "help: to get a list of all the commands you can enter\n"
                "*-------------------------------------------*")


def idle():
    sendOutput("What do you do?:")
    recievedInput()
    if userInput == "go":
        # List rooms to go to function
        go()
        idle()

    elif userInput == "look":
        # Describe the room function
        look()
        idle()

    elif userInput == "help":
        help()
        idle()

    else:
        sendOutput("ERROR: incorrect input")
        idle()


if __name__ == '__main__':

    isRunning = True
    isConnected = False

    client = 0

    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    mySocket.bind(("127.0.0.1", 8222))
    mySocket.listen(5)

    while isRunning == True:
        if isConnected == False:
            print("Waiting for client ...")
            client = mySocket.accept()

            try:
                data = client[0].recv(4096)
                print(data.decode("utf-8"))

                isConnected = True
                print("Client connected")

                userInput = data.decode("utf-8")

            except socket.error:
                isConnected = False

        while isConnected == True:

            try:
                idle()

            except socket.error:
                isConnected = False
                client = None
                print("Client lost")
"""