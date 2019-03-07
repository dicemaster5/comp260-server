import sys
import socket
import threading
import time
import random
import numpy as np
from PIL import Image, ImageOps
from PyQt5 import QtCore, QtGui, uic, QtWidgets

clientIsRunning: bool = True

class ClientData:
    def __init__(self):
        self.serverSocket = None
        self.connectedToServer = False
        self.running = True
        self.incomingMessage = ""
        self.currentBackgroundThread = None
        self.currentReceiveThread = None


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

        # Setup timer
        #self.timer = QtCore.QTimer()
        #self.timer.timeout.connect(self.timerEvent)
        #self.timer.start(100)

        # Send startup message
        self.textDisplay.append("Window init!")

        generateSpaceShipImage()

        self.ShipView.setPixmap(QtGui.QPixmap("ShipParts/out.png"))


        # button Onclick
        self.InputButton.clicked.connect(lambda: self.EnterInputText())

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

def generateSpaceShipImage():
    cockPitPos = (32, 0)
    mainHaulPos = (32, 32)
    thrusterPos = (32, 64)
    wingPos1 = (0, 16)
    wingPos2 = (64 + 16, 16)

    shipPartsImg = Image.open("ShipParts/ShipParts.png")
    # w0, h0 = shipPartsImg.size

    newCockpit = shipPartsImg.crop((64, 0, 64 + 48, 0 + 32))
    # w, h = newCockpit.size

    newMainHull = shipPartsImg.crop((64, 48, 64 + 48, 48 + 32))
    newThruster = shipPartsImg.crop((64, 96, 64 + 48, 96 + 32))
    newWing1 = shipPartsImg.crop((0, 144, 0 + 32, 144 + 48))
    newWing2 = ImageOps.mirror(newWing1)

    newShip = Image.new('RGBA', (112, 112))
    newShip.paste(newCockpit, cockPitPos)
    newShip.paste(newMainHull, mainHaulPos)
    newShip.paste(newThruster, thrusterPos)
    newShip.paste(newWing1, wingPos1)
    newShip.paste(newWing2, wingPos2)

    block = (16, 16)
    x = block[0]
    y = block[1]

    cockPit = (x * 3, y * 2)
    mainHaul = (x * 3, y * 2)
    thruster = (x * 3, y * 2)
    wing = (x * 2, y * 3)

    # shipartsMatrix = np.zeros(shape=(int(h0 / y), int(w0 / x)))
    # newShipMatrix = np.zeros(shape=(int(h / y), int(w / x)))
    # print(newShipMatrix)

    newShip = newShip.resize((224, 224), Image.NEAREST)
    newShip.save("ShipParts/out.png")

def sendFunction(newInput):
    if clientData.connectedToServer:
        clientData.serverSocket.send(newInput.encode())
    else:
        window.DisplayText("ERROR - Client is not connected to a server")

# ========================= THREADING CODE ====================== #


def receiveThread(clientData):
    print("receiveThread running")

    while clientData.connectedToServer is True:
        try:
            data = clientData.serverSocket.recv(4096)
            text = ""
            text += data.decode("utf-8")
            clientDataLock.acquire()
            clientData.incomingMessage += text
            clientDataLock.release()
            print("Text Received: " + text)

            # Display text received to the UI text box
            window.DisplayText(text)

        except socket.error:
            print("Server lost")
            window.DisplayText("Server lost")
            clientData.connectedToServer = False
            clientData.serverSocket = None


def backgroundThread(clientData):
    print("backgroundThread running")
    clientData.connectedToServer = False

    while (clientData.connectedToServer is False) and (clientData.running is True):
        try:

            if clientData.serverSocket is None:
                clientData.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if clientData.serverSocket is not None:
                clientData.serverSocket.connect(("127.0.0.1", 8222))

            clientData.connectedToServer = True
            clientData.currentReceiveThread = threading.Thread(target=receiveThread, args=(clientData,))
            clientData.currentReceiveThread.start()

            print("connected")
            window.DisplayText("Server Connected")

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
