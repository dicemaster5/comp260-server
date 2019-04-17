from queue import *
import threading
import socket
from player import player


class user:
    STATE_LOGIN = 0
    STATE_INGAME = 1
    # ========================= Initialization CODE ====================== #
    def __init__(self, clientSocket, ship):

        # User vars
        self.clientID = ""
        self.username = "USERNAME"
        self.currentPlayer = player(self, ship)

        self.inputQueue = Queue()
        self.outputQueue = Queue()
        self.clientSocket = clientSocket

        # User states
        self.state = user.STATE_LOGIN
        #self.loginState = False
        #self.gameState = False

        self.canReceive = True
        self.canSend = True

        # clientReceiveThread starter
        clientReceiveThread = threading.Thread(target=user.receiveThread, args=(self,))
        clientReceiveThread.start()

        # clientSendingThread starter
        clientSendingThread = threading.Thread(target=user.sendingThread, args=(self,))
        clientSendingThread.start()

# ========================= USER FUNCTIONS CODE ====================== #
    # adds a new message to the outPutQueue to be sent to the client of this user
    def addToOutQueue(self, message, cmdBool = False):
        if cmdBool:
            self.outputQueue.put("cmd:" + message)
        else:
            self.outputQueue.put("dis:" + message)

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
                    self.clientSocket.send(outputMeassage.encode())

                    print(self.username + ": " + outputMeassage)

            except socket.error:
                self.canSend = False
                print("sendingThread: ERROR - Lost client")
