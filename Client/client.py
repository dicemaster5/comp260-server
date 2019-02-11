import socket
import time

localUserInput: str = "First Time Connection"

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