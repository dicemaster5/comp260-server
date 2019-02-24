import sys
import socket
import threading
import time
from PyQt5 import QtCore, QtGui, uic, QtWidgets

clientIsRunning: bool = True
newInput: str

class ClientData:
    def __init__(self):
        self.serverSocket = None
        self.connectedToServer = False
        self.running = True
        self.incomingMessage = ""
        self.currentBackgroundThread = None
        self.currentReceiveThread = None
        self.currentSendThread = None
        self.userName = ""


clientData = ClientData()
clientDataLock = threading.Lock()

# ========================= PYQT WINDOW CODE ====================== #

# Get UI file and load as window.
qtCreatorFile = "DeisgnerWindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


# PyQT application.
class MyApp(QtWidgets.QMainWindow, Ui_MainWindow):
    def __init__(self, game):
        QtWidgets.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        # Setup timer
        #self.timer = QtCore.QTimer()
        #self.timer.timeout.connect(self.timerEvent)
        #self.timer.start(100)

        # Send startup message
        self.textDisplay.append("Window init.")

        # button Onclick
        self.InputButton.clicked.connect(lambda: self.EnterInputText())

        # When enter is pressed in input box.
        self.UserInputBox.returnPressed.connect(lambda: self.EnterInputText())


# Test function to print stuff ====== REMOVE LATER
    def PrintStuff(self):
        print("Clicking button")

    def EnterInputText(self):
        self.newInput = self.UserInputBox.text().lower()
        print("User input submitted")
        print(self.newInput)

        # Send to the server!!!
        sendFunction(self.newInput)

        self.DisplayText(self.newInput)
        self.UserInputBox.setText("")

    def DisplayText(self, text):
        self.textDisplay.append(text)

def sendFunction(newInput):
    clientData.serverSocket.send(newInput.encode())

# ========================= THREADING CODE ====================== #

def sendThread(clientData, MyApp):
    print("sendThread running")
    MyApp.EnterInputText()
    newInput = "poop!"
    clientData.serverSocket.send(newInput.encode())
    print("Sent: " + newInput + " To the server")

def receiveThread(clientData, MyApp):
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
            MyApp.DisplayText(text)

        except socket.error:
            print("Server lost")
            MyApp.DisplayText("Server lost")
            clientData.connectedToServer = False
            clientData.serverSocket = None


def backgroundThread(clientData, MyApp):
    print("backgroundThread running")
    clientData.connectedToServer = False

    while (clientData.connectedToServer is False) and (clientData.running is True):
        try:

            if clientData.serverSocket is None:
                clientData.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            if clientData.serverSocket is not None:
                clientData.serverSocket.connect(("127.0.0.1", 8222))

            clientData.connectedToServer = True
            clientData.currentReceiveThread = threading.Thread(target=receiveThread, args=(clientData, MyApp,))
            clientData.currentReceiveThread.start()

            print("connected")
            MyApp.DisplayText("Server Connected")

            while clientData.connectedToServer is True:
                time.sleep(1.0)


        except socket.error:
            print("no connection")
            time.sleep(1)
            clientDataLock.acquire()
            clientData.incomingMessage = "\nNoServer"
            clientDataLock.release()


# =================== MAIN ========================= #

if __name__ == "__main__":
    if clientIsRunning:
        # Create qtApplication
        app = QtWidgets.QApplication(sys.argv)

        # Create and show qtWindow
        window = MyApp(None)
        window.show()

        # main()
        clientData.currentBackgroundThread = threading.Thread(target=backgroundThread, args=(clientData, window))
        clientData.currentBackgroundThread.start()

        # Event loop
        sys.exit(app.exec_())

"""
import sys
import PyQt5.QtCore
import PyQt5.QtWidgets

from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5 import QtCore

import socket
import threading
import time


class ClientData:
    def __init__(self):
        self.serverSocket = None
        self.connectedToServer = False
        self.running = True
        self.incomingMessage = ""
        self.currentBackgroundThread = None
        self.currentReceiveThread = None
        self.userName = ""


clientData = ClientData()
clientDataLock = threading.Lock()


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
            print(text)
        except socket.error:
            print("Server lost")
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

            while clientData.connectedToServer is True:
                time.sleep(1.0)

        except socket.error:
            print("no connection")
            time.sleep(1)
            clientDataLock.acquire()
            clientData.incomingMessage = "\nNoServer"
            clientDataLock.release()


class Example(QWidget):

    def __init__(self):
        super().__init__()

        self.chatOutput = 0
        self.userInput = 0

        self.initUI()

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.timerEvent)
        self.timer.start(100)

    def timerEvent(self):
        if clientData.incomingMessage != "":
            clientDataLock.acquire()
            self.chatOutput.appendPlainText(clientData.incomingMessage)
            clientData.incomingMessage = ""
            clientDataLock.release()

    def userInputOnUserPressedReturn(self):
        entry = self.userInput.text()
        print("User entry: "+entry)
        clientData.serverSocket.send(bytes(entry, 'utf-8') )
        self.userInput.setText("")

    def initUI(self):
        self.userInput = QLineEdit(self)
        self.userInput.setGeometry(10, 360, 580, 30)
        self.userInput.returnPressed.connect(self.userInputOnUserPressedReturn)

        self.chatOutput = QPlainTextEdit(self)
        self.chatOutput.setGeometry(10, 10, 580, 300)
        self.chatOutput.setReadOnly(True)

        self.setGeometry(300, 300, 600, 400)
        self.setWindowTitle('Client Game Window')
        self.show()

    def closeEvent(self, event):

        if clientData.serverSocket is not None:
            clientData.serverSocket.close()
            clientData.serverSocket = None
            clientData.connectedToServer = False
            clientData.running = False

            if clientData.currentReceiveThread is not None:
                clientData.currentReceiveThread.join()

            if clientData.currentBackgroundThread is not None:
                clientData.currentBackgroundThread.join()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    clientData.ex = Example()

    clientData.currentBackgroundThread = threading.Thread(target=backgroundThread, args=(clientData,))
    clientData.currentBackgroundThread.start()

    sys.exit(app.exec_())
"""
"""
import socket
import time
import threading

from queue import *
messageQueue = Queue()

isRunning = True
isConnected = False
mySocket = None

clientUserInput: str = "First Time Connection"

def receiveThread(serverSocket):
    global isConnected

    while isRunning:
        if isConnected:
            try:
                messageQueue.put(mySocket.recv(4096).decode("utf-8"))
            except socket.error:
                isConnected = False
                print("lost server")
        else:
            print("no server")
            time.sleep(5.0)


if __name__ == '__main__':

    mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    mySocket.connect(("127.0.0.1", 8222))
    isConnected = True

    myThread = threading.Thread(target=receiveThread, args=(mySocket,))
    myThread.start()

    testString = "this is a test from the python client"

    mySocket.send(testString.encode())

    while isRunning:
        time.sleep(1.0)

        while messageQueue.qsize()> 0:
            print(messageQueue.get())

        clientUserInput = input().lower()
        mySocket.send(clientUserInput.encode())


if __name__ == '__main__':

    isConnected = False
    mySocket = None

    isRunning = True

    while isRunning == True:
        while isConnected == False:

            if mySocket is None:
                mySocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

                try:
                    mySocket.connect(("127.0.0.1", 8222))
                    isConnected = True
                except socket.error:
                    isConnected = False

            if(isConnected == True):
                try:
                    mySocket.send(localUserInput.encode())

                except:
                    isConnected = False
                    mySocket = None

                    if isConnected == False:
                        print("No server")
                        time.sleep(1.0)

        while isConnected == True:
            try:
                data = mySocket.recv(4096)
                print(data.decode("utf-8"))

                localUserInput = input().lower()
                mySocket.send(localUserInput.encode())

                data = mySocket.recv(4096)
                print(data.decode("utf-8"))
                time.sleep(1)

            except:
                isConnected = False
                mySocket = None 
"""