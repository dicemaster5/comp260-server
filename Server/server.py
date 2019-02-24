import sys
# from queue import *
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

#inputQueue = Queue()
#outputQueue = Queue()

clients = {}
clientsLock = threading.Lock()

players = {}

# ========================= THREADING CODE ====================== #

def acceptThread(serverSocket):
    print("acceptThread running")
    while True:


        newSocket = serverSocket.accept()[0]
        newClient = client(newSocket)

        print("Added client!")
        #clientsLock.acquire()
        #clients[newClient.clientSocket] = 0
        #clientsLock.release()


# =================== INPUT PROCESSING ========================= #

#def InputCommands(Input, client):
#    if Input == "Help":



# =================== MAIN ========================= #

if __name__ == '__main__':
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    mySocket.bind(("127.0.0.1", 8222))
    mySocket.listen(5)

    acceptThread = threading.Thread(target=acceptThread, args=(mySocket, ))
    acceptThread.start()

    # Main Loop
    #while serverIsRunning:
        #while inputQueue.qsize() > 0:
            #clientMessage = inputQueue.get()
            #print(clientMessage)

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