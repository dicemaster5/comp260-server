from queue import *
import time
import json
import threading
import socket
from player import player

from base64 import b64decode, b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

class user:
    STATE_LOGIN = 0
    STATE_INGAME = 1
    STATE_PLAYERSELECT = 2
    # ========================= Initialization CODE ====================== #
    def __init__(self, clientSocket, ship):

        # User vars
        self.clientID = ""
        self.encryptionKey = b"HELLOWORLDEEEEEE"
        self.username = "USERNAME"
        self.currentPlayer = player(self, ship)

        self.inputQueue = Queue()
        self.outputQueue = Queue()
        self.clientSocket = clientSocket
        self.clientIsConnected = True

        # User states
        self.state = user.STATE_LOGIN

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

# ========================= ENCRYPTION CODE ====================== #
    def encryptData(self, data):
        print("Encrypting DATA")

        dataa = data
        key = self.encryptionKey
        cipher = AES.new(key, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(dataa, AES.block_size))
        iv = b64encode(cipher.iv).decode('utf-8')
        ct = b64encode(ct_bytes).decode('utf-8')

        result = json.dumps({'iv': iv, 'ciphertext': ct})
        print(data)
        return result

        #decryptData(result, key)

    def decryptData(self, data, key):
        print("Decrypting DATA")

        try:
            b64 = json.loads(data.decode())
            iv = b64decode(b64['iv'])
            ct = b64decode(b64['ciphertext'])
            cipher = AES.new(key, AES.MODE_CBC, iv)

            result = unpad(cipher.decrypt(ct), AES.block_size)
            print("The Encrypted text was: " + result.decode('utf-8'))
            return result.decode('utf-8')

        except Exception as err:
            print("Error decrypting!" + err.args[0])

# ========================= THREADING CODE ============================== #
    def receiveThread(self):
        print("receiveThread running")
        while self.canReceive:
            try:
                data = self.clientSocket.recv(4096)
                decryptedData = self.decryptData(data, self.encryptionKey)
                text = decryptedData

                self.inputQueue.put(text)

            except socket.error:
                self.canReceive = False
                self.clientIsConnected = False
                print("receiveThread: ERROR - Lost client")

    def sendingThread(self):
        print("sendingThread running")
        while self.canSend:
            dataDict = {"time": time.ctime(), "message": ""}

            try:
                if self.outputQueue.qsize() > 0:
                    # Get the output message to be sent
                    outputMeassage = self.outputQueue.get()

                    dataDict['message'] = outputMeassage
                    jsonPacket = json.dumps(dataDict)


                    data = jsonPacket.encode()
                    print(self.username + ": " + outputMeassage)
                    encryptedData = self.encryptData(data).encode("utf-8")

                    header = len(encryptedData).to_bytes(2, byteorder='little')

                    # Send data packets to the player
                    self.clientSocket.send(header)
                    self.clientSocket.send(encryptedData)
                    time.sleep(0.3)

            except socket.error:
                self.canSend = False
                self.clientIsConnected = False
                print("sendingThread: ERROR - Lost client")

