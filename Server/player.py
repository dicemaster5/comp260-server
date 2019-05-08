
class player:
    # ========================= Initialization CODE ====================== #
    def __init__(self, user, spaceShip):

        # Player game vars
        self.user = user
        self.playerName = "Roger"
        self.currentSpaceShip = spaceShip
        self.currentRoom = self.currentSpaceShip.rooms["Main Deck"]
        self.health = 100
        self.inventory = []

# ========================= PLAYER FUNCTIONS CODE ====================== #
    # Moves the player to a new room
    def moveToRoom(self, newRoom):
        self.currentRoom = newRoom

    def addItemToinventory(self, item):
        self.inventory.append(item)

    def removeItemFrominventory(self, item):
        self.inventory.remove(item)
