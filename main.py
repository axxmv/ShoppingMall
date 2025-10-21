# Shopping Mall


import random

class User:
    def __init__(self, name, password):
        self.name = name
        self.password = password



class Staff(User):
    def __init__(self, name, password, staffID):
        super().__init__(name, password)
        self.staffID = staffID

    def addItem(self, inventory, itemId, name, description, price, stock, likeCounter):
        inventory._addItemtoInventory(itemId, name, description, price, stock, likeCounter)

    def removeItem(self, inventory, itemId):
        inventory._removeItemfromInventory(itemId)

    def viewCustomerInformation(self):
        print(customer_info)

    def staffPortal(self, inv):

        run = True
        while run == True:
            print("1. Add Item "
                  "2. View Customer Information "
                  "3. message "
                  " 4. Exit")

            option = int(input("Enter Option: "))

            if option == 1:
                name = input("Enter the Item name: ")
                itemId = int(input("Enter the Item ID: "))
                description = input("Item Description: ")
                price = float(input("price: "))
                stock = int(input("Amount in stock: "))
                likeCounter = 0

                self.addItem(inv, itemId, name, description, price, stock, likeCounter)
            if option == 2:
                self.viewCustomerInformation()

            if option == 3:
                print("pretend you see messages")

            if option == 4:
                run = False
                return







class Customer(User):
    def __init__(self, name, password, address, paymentInfo, wishlistID):
        super().__init__(name, password)
        self.address = address
        self.paymentInfo = paymentInfo
        self.wishlistInfo = wishlistID

    def customerPortal(self):
        print("1. View Catalog"
              "2. View Wishlist"
              "3. message")
    #

class Ceo(User):
    def __init__(self, name, password, ceoID):
        super().__init__(name, password)
        self.ceoID = ceoID

    def ceoPortal(self):
        print("1. View Reports")




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


    def _addItemtoInventory(self, itemId, name, description, price, stock, likeCounter): #creates the item and adds it to inventory at the sane time
        item = Item(itemId, name, description, price, stock, likeCounter)
        self.inventoryList.append(item)

    def _removeItemfromInventory(self, itemId):
        for item in self.inventoryList:
            if item.itemId == itemId:
                self.inventoryList.remove(item)
                print(f"Item with ID {itemId} removed.")
                return
        print(f"No item found with ID {itemId}.")


user_db = [
    {"name": "bob", "password": "boblikeshotdogs", "role": "staff", "staffID": 12345},
    {"name": "alice", "password": "alice123", "role": "customer", "address": "123 Street", "paymentInfo": "Visa 1234", "wishlistID": 1},
    {"name": "boss", "password": "topsecret", "role": "ceo", "ceoID": 999}
] #for registration we just need to add the user information to this list


customer_info = [{"name": "alice", "password": "alice123", "role": "customer", "address": "123 Street", "paymentInfo": "Visa 1234", "wishlistID": 1}]

def register(user_db):
    print("__________Registration__________ ")
    username = input("Username: ")
    password = input("Password: ") #reenter password


    print("Choose Account Type: 1. Staff  2. Customer")
    accountType = int(input("New Account Type: "))

##restrict staff accounts
    if accountType == 1:
        role = "staff"
        staff_id = input("Enter a four digit Staff ID: ")
        newuserinfo = {"name": username, "password": password, "role": "staff", "staffID": staff_id}
        user_db.append(newuserinfo)
        print(user_db)

        return


    if accountType == 2:
        role = "customer"
        address = input("Enter Shipping Address: ")
        paymentInfo = input("Enter Card type and number (e.g. Visa 1234 5678: ")
        wishlistID = random.randint(100, 999) #add function to make sure the wishlist ID is unique here
        newuserinfo = {"name": username, "password": password, "role" : role, "address": address, "paymentInfo": paymentInfo, "wishlistID": wishlistID}
        user_db.append(newuserinfo)
        customer_info.append(newuserinfo)
        return


#the user inputs their desired role and it is assigned to them when it is added into the database.


def login(user_db):
    print("________Log In________")
    username = input("Enter your Username: ")
    password = input("Enter your Password: ")

    for data in user_db:
        if data["name"] == username and data["password"] == password:
            role = data["role"]
            # add input validation. add loop for invalid credentials.


            if role == "staff":
                return Staff(data["name"], data["password"], data["staffID"])
            elif role == "customer":
                return Customer(data["name"], data["password"], data["address"], data["paymentInfo"], data["wishlistID"])
            elif role == "ceo":
                return Ceo(data["name"], data["password"], data["ceoID"])



def main():
    inv = Inventory()

    ####################### just for testing
    staff1 = Staff("bob", "boblikeshotdogs", 12345)
    staff1.addItem(inv, 16374, "apple", "description", 2.95, 5, 0)
    staff1.addItem(inv, 85848, "grape", "description", 3.45, 5, 2)
    #######################
    print("You Just got Coconut Malled")
    condition = input("Do you have an account? Y or N: ")

    if condition.upper() == 'N':
        register(user_db)
        print("User Registered")




    currentUser = None
    while not currentUser:
        currentUser = login(user_db)  ##calls the login function and the returned value is now assigned to current user

    print(f"\nLogged in as {currentUser.name} ({currentUser.__class__.__name__})\n")

    if isinstance(currentUser, Staff):
        print("Staff Portal")
        currentUser.staffPortal(inv)
        condition = input("Would you like to log out? Y or N: ")
        while condition.upper() == "N":
            currentUser.staffPortal(inv)
            condition = input("Would you like to log out? Y or N: ")
        del currentUser
        login(user_db)




    elif isinstance(currentUser, Customer):
        print("Welcome to the Shopping Mall!")
        print("Browse Available Items: ")
        print("\n")
        print(inv)
        currentUser.customerPortal()
    elif isinstance(currentUser, Ceo):
        print("View Reports")
        currentUser.ceoPortal()





if __name__ == "__main__":
    main()

