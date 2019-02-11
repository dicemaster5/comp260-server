from Room import Room


class Dungeon:
    def __init__(self):
        self.currentRoom = 0
        self.rooms = {}

    def Init(self):
        print("init")

        self.rooms["room 0"] = Room("room 0", "You are standing in the entrance hall\nAll adventures start here", "room 1", "", "", "")
        self.rooms["room 1"] = Room("room 1", "You are in room 1","", "room 0", "room 3", "room 2")
        self.rooms["room 2"] = Room("room 2", "You are in room 2", "room 4", "", "", "")
        self.rooms["room 3"] = Room("room 3", "You are in room 3", "", "", "", "room 1")
        self.rooms["room 4"] = Room("room 4", "You are in room 4", "", "room 2", "room 5", "")
        self.rooms["room 5"] = Room("room 5", "You are in room 5", "", "room 1", "", "room 4")

        self.currentRoom = "room 0"

    def roomDesc(self):
        print(self.rooms[self.currentRoom].desc)

    def canMove(self, direction):
        return self.rooms[self.currentRoom].exits(direction)

    def movePlayer(self, direction):
        if self.canMove(direction):
            if direction == "north":
                self.currentRoom = self.rooms[self.currentRoom].north
                return

            if direction == "south":
                self.currentRoom = self.rooms[self.currentRoom].south
                return

            if direction == "east":
                self.currentRoom = self.rooms[self.currentRoom].east
                return

            if direction == "west":
                self.currentRoom = self.rooms[self.currentRoom].west
                return