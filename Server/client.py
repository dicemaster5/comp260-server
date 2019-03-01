from queue import *
import threading
import socket

class client:

# ========================= Initialization CODE ====================== #
    def __init__(self, clientSocket, spaceShip):
        self.inputQueue = Queue()
        self.outputQueue = Queue()
        self.clientSocket = clientSocket

        self.clientID = ""
        self.playerName = "Roger"
        self.currentSpaceShip = spaceShip
        self.currentRoom = self.currentSpaceShip.rooms["Main Deck"]

        self.health = 100
        self.inventory = {}

        # clientReceiveThread starter
        clientReceiveThread = threading.Thread(target=client.receiveThread, args=(self,))
        clientReceiveThread.start()

        # clientSendingThread starter
        clientSendingThread = threading.Thread(target=client.sendingThread, args=(self,))
        clientSendingThread.start()

# ========================= PLAYER FUNCTIONS CODE ====================== #

    # adds a new message to the outPutQueue to be sent to the client of this player
    def addToOutQueue(self, message):
        self.outputQueue.put(message)

    # Moves the player to a new room
    def moveToRoom(self, room):
        self.currentRoom = room

# ========================= THREADING CODE ============================== #

    def receiveThread(self):
        print("receiveThread running")
        canReceive = True
        while canReceive:
            try:
                data = self.clientSocket.recv(4096)
                text = data.decode("utf-8")

                self.inputQueue.put(text)

            except socket.error:
                canReceive = False
                print("receiveThread: ERROR - Lost client")

    def sendingThread(self):
        print("sendingThread running")
        canSend = True
        while canSend:
            try:
                if self.outputQueue.qsize() > 0:
                    # Get the output message to be sent
                    outputMeassage = self.outputQueue.get()

                    # Send message to the player
                    self.clientSocket.send(outputMeassage.encode("utf-8"))

                    print(self.playerName + " is Sending: " + outputMeassage)

            except socket.error:
                canSend = False
                print("sendingThread: ERROR - Lost client")