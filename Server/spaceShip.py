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
        self.name: str
        self.position: (int, int)
        self.rooms = {}
        self.players = []

    def generateShip(self, ShipName):
        self.name = ShipName

        cockPit = room()
        cockPit.setRoom(
                        "Cock Pit",
                        {"back":"Main Deck"},
                        "You are in the main controls room.\n"
                        "from here you can control an navigate the ship.")

        mainDeck = room()
        mainDeck.setRoom(
                        "Main Deck",
                        {"front":"Cock Pit", "back":"Cargo Haul"},
                        "You are standing in the main deck of the ship.\n"
                        "There are many terminals around you.")

        cargoHaul = room()
        cargoHaul.setRoom(
                        "Cargo Haul",
                        {"front":"Main Deck"},
                        "You are in the Cargo Haul of the ship.\n"
                        "There are all sorts of worthless treasures in here.")

        self.rooms = {"Cock Pit": cockPit, "Main Deck": mainDeck, "Cargo Haul": cargoHaul}
