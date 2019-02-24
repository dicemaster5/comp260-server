from queue import *
import threading
import socket
class client:


    # Init function
    def __init__(self, clientSocket):
        self.inputQueue = Queue()
        self.clientSocket = clientSocket
        self.clientID = ""
        self.playerName = "Roger"


        clientReceiveThread = threading.Thread(target=client.receiveThread, args=(self,))
        clientReceiveThread.start()

        clientSendingThread = threading.Thread(target=client.sendingThread, args=(self,))
        clientSendingThread.start()

# ========================= THREADING CODE ====================== #

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
                print("receiveThread: Lost client!")

    def sendingThread(self):
        print("sendingThread running")
        canSend = True
        while canSend:
            try:
                if self.inputQueue.qsize() > 0:
                    inputMeassage = self.inputQueue.get()

                    if inputMeassage == "help":
                        stringMessage = "--HELP COMMAND--"
                        self.clientSocket.send(stringMessage.encode())

                        print("Sending: " + stringMessage)

                    else:
                        stringMessage = (inputMeassage + ": Is not a valid Command!")
                        self.clientSocket.send(stringMessage.encode())

                        print("Sending: " + stringMessage)

            except socket.error:
                canSend = False
                print("sendingThread: Lost client!")