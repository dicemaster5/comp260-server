class room:
    def __init__(self):
        self.name = ""
        self.description = ""
        self.players = []
        self.interactables = {}
        self.connectedRooms = {}

    def setRoom(self, roomName, rooms, description):
        self.name = roomName
        self.connectedRooms = rooms
        self.description = description

class ship:
    def __init__(self):
        self.name = ""
        self.position: (int, int)
        self.rooms = {}
        self.players = []

    # Creates a ship made of defined rooms
    def generateShip(self, ShipName):
        self.name = ShipName

        cockPit = room()
        cockPit.setRoom(
                        "Cock Pit",
                        {"back": "Main Deck"},
                        "You are in the main controls room.\n"
                        "The pilot seat is at the front with many control panels surrounding it.\n"
                        "From here you can control and navigate the ship.")

        mainDeck = room()
        mainDeck.setRoom(
                        "Main Deck",
                        {"front": "Cock Pit", "back":"Cargo Haul", "left":"Medical Room", "right":"Armory"},
                        "You are standing in the main deck of the ship.\n"
                        "There are many terminals around you.")

        cargoHaul = room()
        cargoHaul.setRoom(
                        "Cargo Haul",
                        {"front": "Main Deck"},
                        "You are in the Cargo Haul of the ship.\n"
                        "There are all sorts of worthless treasures in here.")

        medicRoom = room()
        medicRoom.setRoom(
                        "Medical Room",
                        {"right": "Main Deck"},
                        "You are in the Medical room.\n"
                        "There are medical kits and beds in the room.")

        Armory = room()
        Armory.setRoom(
                        "Armory",
                        {"left": "Main Deck"},
                        "You are in the Armory.\n"
                        "There are laser rifles and plasma guns hanging on the walls.\n"
                        "you also notice a box withe the word -CAUTION EXPLOSIVES- on the side of it.")

        self.rooms = {"Cock Pit": cockPit, "Main Deck": mainDeck, "Cargo Haul": cargoHaul, "Medical Room":medicRoom, "Armory":Armory}
