import sys
import socket
import threading

from queue import *
from commands import *


"""
import sys
import socket
import threading

from queue import *
from commands import *


messageQueue = Queue()

clientIndex = 0
currentClients: dict = {}
currentClientsLock = threading.Lock()


class Player:
    playerUsername: str = "NewUser"


def clientReceive(clientsocket):
    print("clientReceive running")
    clientValid = True
    while clientValid == True:
        try:
            data = clientsocket.recv(4096);

            currentClientsLock.acquire()
            msg = "client-" + str(currentClients[clientsocket]) + ":"
            msg += data.decode("utf-8")
            currentClientsLock.release()

            print("received client msg:"+str(data, "utf-8"))

            messageQueue.put(ClientMessage(clientsocket, msg))
        except socket.error:
            print("clientReceive - lost client")
            clientValid = False
            messageQueue.put(ClientLost(clientsocket))


def acceptClients(serversocket):
    print("acceptThread running")
    while True:
        (clientsocket, address) = serversocket.accept()
        messageQueue.put(ClientJoined(clientsocket))

        thread = threading.Thread(target=clientReceive, args=(clientsocket,))
        thread.start()


def handleClientLost(command):
    currentClientsLock.acquire()
    lostClient = currentClients[command.socket]
    print("Removing lost client: client-"+str(lostClient))

    for key in currentClients:
        if key != command.socket:
            key.send(bytes("client-"+str(lostClient) + " has left the chat room", 'utf-8'))

    del currentClients[command.socket]

    currentClientsLock.release()


def handleClientJoined(command):
    global clientIndex

    currentClientsLock.acquire()
    currentClients[command.socket] = clientIndex
    clientIndex += 1

    print("Client joined: client-" + str(currentClients[command.socket]))

    outputToUser = "Welcome to chat! What is your Username?\n"

    outputToUser += "You are: client-" + str(currentClients[command.socket]) +"\n"
    outputToUser += "Present in chat:\n"

    for key in currentClients:
        outputToUser += "client-" + str(currentClients[key]) + "\n"

    command.socket.send(bytes(outputToUser, 'utf-8'))

    for key in currentClients:
        if key != command.socket:
            key.send(bytes("client-"+str(currentClients[command.socket]) + " has joined the chat room", 'utf-8'))

    currentClientsLock.release()


def handleClientMessage(command):
    print("client message: "+command.message)

    currentClientsLock.acquire()
    for key in currentClients:
        try:
            key.send(bytes(command.message, 'utf-8'))
        except socket.error:
            messageQueue.put(ClientLost(key))

    currentClientsLock.release()


def main():
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        if len(sys.argv) > 1:
            serversocket.bind((sys.argv[1], 8222))
        else:
            serversocket.bind(("127.0.0.1", 8222))
    except socket.error:
        print("Can't start server, is another instance running?")
        exit()

    serversocket.listen(5)

    thread = threading.Thread(target=acceptClients,args=(serversocket,))
    thread.start()

    while True:

        if messageQueue.qsize() > 0:
            print("Processing client commands")
            command = messageQueue.get()

            if isinstance(command, ClientJoined):
                handleClientJoined(command)

            if isinstance(command, ClientLost):
                handleClientLost(command)

            if isinstance(command, ClientMessage):
                handleClientMessage(command)


if __name__ == "__main__":
    main()
"""

import socket
import time
import threading

#########
playerName: str
userInput: str
output: str = "null"
client = 0

serverIsRunning: bool = True

messageQueue = Queue()

clients = {}
clientsLock = threading.Lock()


######################## THREADING CODE ########################

def receiveThread(client):
    print("receiveThread running")
    canReceive = True
    while canReceive:
        try:
            data = client.recv(4096)
            text = ""
            text += data.decode("utf-8")

            messageQueue.put((client, text))

            #print("Receiving: " + text)

        except socket.error:
            canReceive = False
            print("receiveThread: Lost client!")

def acceptThread(serverSocket):
    print("acceptThread running")
    while True:
        new_client = serverSocket.accept()
        print("Added client!")
        clientsLock.acquire()
        clients[new_client[0]] = 0
        clientsLock.release()

        newReceiveThread = threading.Thread(target=receiveThread, args=(new_client[0],))
        newReceiveThread.start()


def sendingThread(serverSocket, clients):
    print("sendingThread running")
    while True:
        lostclients = []

        clientsLock.acquire()
        for client in clients:
            try:
                testString = str(clients[client]) + ":" + time.ctime()
                clients[client] += 1
                client.send(testString.encode())

                print("Sending: " + testString)

            except socket.error:
                lostclients.append(client)
                print("Sending: Lost client!")

        for client in lostclients:
            clients.pop(client)

        clientsLock.release()

        time.sleep(2)

if __name__ == '__main__':
    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    mySocket.bind(("127.0.0.1", 8222))
    mySocket.listen(5)

    acceptThread = threading.Thread(target=acceptThread, args=(mySocket, ))
    acceptThread.start()

    sendingThread = threading.Thread(target=sendingThread, args=(mySocket, clients))
    sendingThread.start()

    while serverIsRunning:
        while messageQueue.qsize() > 0:
            clientMessage = messageQueue.get()
            print(clientMessage[0])
            print(clientMessage[1])

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