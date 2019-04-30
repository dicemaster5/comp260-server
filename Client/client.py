import sys
import json
import socket
import threading
import time
import bcrypt
from PyQt5 import QtCore, QtGui, uic, QtWidgets

from base64 import b64decode, b64encode
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

clientIsRunning: bool = True

class ClientData:
    def __init__(self):
        self.serverSocket = None
        self.connectedToServer = False
        self.running = True

        self.incomingMessage = ""
        self.currentBackgroundThread = None
        self.currentReceiveThread = None

        self.encryptionKey = b"HELLOWORLDEEEEEE"


clientData = ClientData()
clientDataLock = threading.Lock()

# ========================= PYQT WINDOW CODE ====================== #

# Get UI file and load as window.
qtCreatorFile = "DeisgnerWindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

# PyQT application.
class QtWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Hide the login panel
        self.loginWidget.hide()

        # Send startup message
        self.textDisplay.append("Window init!")

        # buttons Onclick
        self.InputButton.clicked.connect(lambda: self.EnterInputText())

        self.LoginButton.clicked.connect(lambda: self.TryLogin())
        self.NewAccountButton.clicked.connect(lambda: self.TryNewAccount())

        # When enter is pressed in input box.
        self.UserInputBox.returnPressed.connect(lambda: self.EnterInputText())

    def closeEvent(self, event):
        clientData.serverSocket.close()
        clientData.serverSocket = None
        clientData.running = False
        clientData.currentBackgroundThread.join()

    def EnterInputText(self):
        self.newInput = self.UserInputBox.text()
        print("User input submitted")

        self.DisplayText(self.newInput)
        self.UserInputBox.setText("")

        # Send to the server!!!say
        sendFunction(self.newInput)

    def DisplayText(self, text):
        self.textDisplay.append(text)
        self.textDisplay.moveCursor(QtGui.QTextCursor.End)

    # ----- LOGIN PANEL FUNCTIONS ----- #
    def ShowLoginPanel(self):
        self.loginWidget.show()

    def TryLogin(self):
        if len(self.UserNameInput.text()) > 3 and len(self.PassWordInput.text()) > 3:
            username = self.UserNameInput.text()
            password = self.PassWordInput.text()

            # Send Username and password across for checking
            sendFunction("--!SaltCheck#" + username + "#" + password)

        else:
            self.DisplayText("-- ERROR Please input a Username and Password that is longer than 3 chars --")

    def SendSaltedPassword(self, recSalt):
        username = self.UserNameInput.text()
        password = self.PassWordInput.text().encode('utf-8')
        salt = recSalt.encode('utf-8')

        password = bcrypt.hashpw(password, salt)
        password = password.decode()

        # Send Username and password across for checking
        sendFunction("--!Login#" + username + "#" + password)


    def TryNewAccount(self):
        if len(self.UserNameInput.text()) > 3 and len(self.PassWordInput.text()) > 3:
            username = self.UserNameInput.text()
            password = self.PassWordInput.text()
            salt = bcrypt.gensalt(12)

            password = password.encode('utf-8')
            password = bcrypt.hashpw(password, salt)
            password = password.decode()
            salt = salt.decode()

            sendFunction("--!NewAccount#" + username + "#" + password + "#" + salt)

            self.UserNameInput.clear()
            self.PassWordInput.clear()

            #self.DisplayText("-- ACCOUNT ACCEPTED! --")
        else:
            self.DisplayText("-- ERROR Please input a Username and Password that is longer than 3 chars --")


# ================================ FUNCTIONS ===================================== #
def encryptData(data):
    print("Encrypting DATA")

    dataa = data.encode()
    key = clientData.encryptionKey
    cipher = AES.new(key, AES.MODE_CBC)
    ct_bytes = cipher.encrypt(pad(dataa, AES.block_size))
    iv = b64encode(cipher.iv).decode('utf-8')
    ct = b64encode(ct_bytes).decode('utf-8')

    result = json.dumps({'iv':iv, 'ciphertext':ct})
    return result

def decryptData(data, key):
    #print("Decrypting DATA: " + data.decode())
    #try:
    b64 = json.loads(data)
    iv = b64decode(b64['iv'])
    ct = b64decode(b64['ciphertext'])
    cipher = AES.new(key, AES.MODE_CBC, iv)

    result = unpad(cipher.decrypt(ct), AES.block_size)
    #print("The Encrypted text was: " + result.decode('utf-8'))
    return result.decode('utf-8')

    #except Exception as err:
    #   print("Error decrypting!" + err)

def sendFunction(newInput):
    if clientData.connectedToServer:
        newInput = encryptData(newInput)
        clientData.serverSocket.send(newInput.encode())
    else:
        window.DisplayText("ERROR - Client is not connected to a server")

def CheckReceivedData(data):
    messageList = data.split(":", 1)

    if messageList[0] == "dis":
        # Display text received to the UI text box
        window.DisplayText(messageList[1])

    elif messageList[0] == "cmd":
        commandlist = messageList[1].split("#",1)
        if commandlist[0] == "salt":
            window.SendSaltedPassword(commandlist[1])

        if commandlist[0] == "loginAccepted":
            window.loginWidget.hide()

        if commandlist[0] == "updateUserName":
            window.userNameBox.setText("USERNAME: " + commandlist[1])

        if commandlist[0] == "updatePlayerName":
            window.playerNameBox.setText("PLAYER NAME: " + commandlist[1])

        if commandlist[0] == "updateRoom":
            window.currentRoomBox.setText("CURRENT ROOM: " + commandlist[1])
    else:
        print(messageList)

# ========================= THREADING CODE ====================== #

def receiveThread(clientData):
    print("receiveThread running")

    while clientData.connectedToServer is True:
        try:
            dataRecv = clientData.serverSocket.recv(4)

            payloadSize = int.from_bytes(dataRecv, byteorder='little')

            payloadData = clientData.serverSocket.recv(payloadSize)
            print(str(payloadSize))

            payloadData = decryptData(payloadData, clientData.encryptionKey)

            data = json.loads(payloadData)

            print("New Data received:" + data['time'] + "\nDATA:[" + data['message'] + "]")

            # Decrypts the data and checks the result
            CheckReceivedData(data['message'])

        except socket.error:
            print("Server lost")
            window.DisplayText("Server lost")
            clientData.connectedToServer = False
            clientData.serverSocket = None

def backgroundThread(clientData):
    print("backgroundThread running")
    clientData.connectedToServer = False

    # -- CODE TO CONNECT TO THE SERVER -- #
    while (clientData.connectedToServer is False) and (clientData.running is True):
        try:

            if clientData.serverSocket is None:
                clientData.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if clientData.serverSocket is not None:
                clientData.serverSocket.connect(("127.0.0.1", 8222))
                #clientData.serverSocket.connect(("46.101.56.200", 9111))

            clientData.connectedToServer = True
            clientData.currentReceiveThread = threading.Thread(target=receiveThread, args=(clientData,))
            clientData.currentReceiveThread.start()

            print("connected")
            window.DisplayText("Client: Server Connected\n")

            window.ShowLoginPanel()

            while clientData.connectedToServer is True:
                time.sleep(1.0)


        except socket.error:
            print("no connection")
            time.sleep(1)
            clientDataLock.acquire()
            clientData.incomingMessage = "\nNoServer"
            clientDataLock.release()


# ========================= MAIN ========================== #

if __name__ == "__main__":
    if clientIsRunning:
        # Create qtApplication
        app = QtWidgets.QApplication(sys.argv)

        # Create and show qtWindow
        window = QtWindow()
        window.show()

        # main()
        clientData.currentBackgroundThread = threading.Thread(target=backgroundThread, args=(clientData,))
        clientData.currentBackgroundThread.start()

        # Event loop
        sys.exit(app.exec_())
