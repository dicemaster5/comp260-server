import array


class Player:
    def __init__(self):
        self.playerPos: array
        self.playerName: str
        self.userInput: str

    # function allows player to move to a different room
    def go(self):
        userInput = input("which direction will you go in?:")
        if userInput == "north":
            print("You enter the room to the north.")
        elif userInput == "south":
            print("You enter the room to the south.")
        elif userInput == "east":
            print("You enter the room to the east.")
        elif userInput == "west":
            print("You enter the room to the west.")
        else:
            print(userInput + " - is not a direction (Choose either: north, south, east, west)")

    # look function describes the room you are in
    def look(self):
        print("You are in a room!")

    # Help function tells you what commands you cam write
    def help(self):
        print("*-------------------------------------------*")
        print("Here is the List of commands you can enter")
        print("go: to go to a new location/room")
        print("look: to get a description of your environment")
        print("help: to get a list of all the commands you can enter")
        print("*-------------------------------------------*")

    # Idle function
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
        else:
            print("ERROR - invalid command (type 'help' for a list of commands)")
            self.idle()
