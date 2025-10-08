# Shopping Mall

class User:
    def __init__(self, name, password):
        self.name = name
        self.password = password



class Staff(User):
    def __init__(self, name, password, staffID):
        super().__init__(name, password)
        self.staffID = staffID

class Customer(User):
    def __init__(self, name, password, address, paymentInfo, wishlistID):
        super().__init__(name, password)
        self.address = address
        self.paymentInfo = paymentInfo
        self.wishlistInfo = wishlistID

class Ceo(User):
    def __init__(self, name, password, ceoID):
        super().__init__(name, password)
        self.ceoID = ceoID


class Item:
    def __init__(self, itemId, name, description, price, stock, likeCounter):
        self.itemId = itemId
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.likeCounter = likeCounter

    def __str__(self): #to view item details. used when "viewing" an item
        return (f"Item ID: {self.itemId}\n"
                f"Name: {self.name}\n"
                f"Description: {self.description}\n"
                f"Price: ${self.price:.2f}\n"
                f"Stock: {self.stock}\n"
                f"Likes: {self.likeCounter}\n")

class Inventory:
    def __init__(self):
        self.inventoryList = []

    def __str__(self):
        if not self.inventoryList:
            return "Inventory is empty."
        return "\n".join([f" {item.name}" for item in self.inventoryList]) # "\n".join([str(item) for item in self.inventoryList]) to print details


    def addItemtoInventory(self, itemId, name, description, price, stock, likeCounter): #creates the item and adds it to inventory at the sane time
        item = Item(itemId, name, description, price, stock, likeCounter)
        self.inventoryList.append(item)

    def removeItemfromInventory(self, itemId):
        for item in self.inventoryList:
            if item.itemId == itemId:
                self.inventoryList.remove(item)
                print(f"Item with ID {itemId} removed.")
                return
        print(f"No item found with ID {itemId}.")



def main():
    inv = Inventory()
    inv.addItemtoInventory(1234, "apple","food", 1.25, 3, 1)
    inv.addItemtoInventory(5678, "banana", "food", 1.25, 4, 2)
    print(inv)




if __name__ == "__main__":
    main()

