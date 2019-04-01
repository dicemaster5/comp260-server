from queue import *
import threading
import socket


class user:
    # ========================= Initialization CODE ====================== #
    def __init__(self, clientSocket):

        # User vars
        self.username = ""

        self.inputQueue = Queue()
        self.outputQueue = Queue()
        self.clientSocket = clientSocket

        self.states = ["Login", "Game", ""]
        self.currentUserState = ""
        self.loginStage = False
        self.gameStage = False

        self.clientID = ""

        self.canReceive = True
        self.canSend = True

        # clientReceiveThread starter
        clientReceiveThread = threading.Thread(target=user.receiveThread, args=(self,))
        clientReceiveThread.start()

        # clientSendingThread starter
        clientSendingThread = threading.Thread(target=user.sendingThread, args=(self,))
        clientSendingThread.start()

# ========================= PLAYER FUNCTIONS CODE ====================== #
    # adds a new message to the outPutQueue to be sent to the client of this player
    def addToOutQueue(self, message):
        self.outputQueue.put(message)

    # Moves the player to a new room
    def moveToRoom(self, newRoom):
        self.currentRoom = newRoom

# ========================= THREADING CODE ============================== #
    def receiveThread(self):
        print("receiveThread running")
        while self.canReceive:
            try:
                data = self.clientSocket.recv(4096)
                text = data.decode("utf-8")

                self.inputQueue.put(text)

            except socket.error:
                self.canReceive = False
                print("receiveThread: ERROR - Lost client")

    def sendingThread(self):
        print("sendingThread running")
        while self.canSend:
            try:
                if self.outputQueue.qsize() > 0:
                    # Get the output message to be sent
                    outputMeassage = self.outputQueue.get()

                    # Send message to the player
                    self.clientSocket.send(outputMeassage.encode("utf-8"))

                    print(self.username + ": " + outputMeassage)

            except socket.error:
                self.canSend = False
                print("sendingThread: ERROR - Lost client")