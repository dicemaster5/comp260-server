class Player:
    playerName: str
    userInput: str

    def go(self):
        userInput = input("which direction will you go in?:")
        if userInput == "north":
            print("You enter the room to the north.")

    def look(self):
        print("You are in a small room.")

    def help(self):
        print("*-------------------------------------------*")
        print("Here is the List of commands you can enter")
        print("go: to go to a new location/room")
        print("look: to get a description of your environment")
        print("help: to get a list of all the commands you can enter")
        print("*-------------------------------------------*")

    def idle(self):
        userInput = input("What do you do?:").lower()
        if userInput == "go":
            # List rooms to go to function
            self.go()
            self.idle()

        elif userInput == "look":
            # Describe the room function
            self.look()
            self.idle()

        elif userInput == "help":
            self.help()
            self.idle()