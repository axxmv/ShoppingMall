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
            print("1. Add Item ")
            print("\n")
            print("2. View Customer Information ")
            print("\n")
            print("3. message ")
            print("\n")
            print("4. Exit")

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







class Customer(User): #Vincent was here from lines 66-138
    def __init__(self, name, password, address, paymentInfo, wishlistID):
        super().__init__(name, password)
        self.address = address
        self.paymentInfo = paymentInfo
        self.wishlistInfo = [] #changed from ID to wishlist ID
        self.orderHistory = [] #this is new I added this to track orders -Vincent

    #I'm adding this for the browsing and interacting with items part (Vincent)
    def browseItems(self, inv):
        if not inv.inventoryList:
            print("There are no items available in inventory.")
            return
        
        print("\n===== Available Items =====")
        for item in inv.inventoryList:
            print(f"{item.itemId}: {item.name} - ${item.price:.2f}")
        
        while True:
            try:
                choice = input("\nEnter Item ID to view details (or 'b' to go back): ")
                if choice.lower() == 'b':
                    return
                itemId = int(choice)
                selected_item = next((i for i in inv.inventoryList if i.itemId == itemId), None)
                if not selected_item:
                    print("Item not found. Please try again.")
                    continue
                
                print("\n" + str(selected_item))
                action = input("Would you like to (L)ike, (W)ishlist, (O)rder, or (B)ack? ").lower() #added order here -Vincent
                
                if action == 'l':
                    selected_item.likeCounter += 1
                    print(f"You liked {selected_item.name}! Total Likes: {selected_item.likeCounter}")
                
                elif action == 'w': #new stuff -Vincent
                    if selected_item not in self.wishlistInfo:
                        self.wishlistInfo.append(selected_item)
                        print(f"{selected_item.name} added to your wishlist!")
                    else:
                        print("This item is already in your wishlist.")
                
                elif action == 'o':
                    self.placeorder(selected_item)
                
                elif action == 'b':
                    return
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Please enter a valid item ID or 'b' to go back.")

    #Creating view wishlist
    def viewWishlist(self):
        if not self.wishlistInfo:
            print("Your wishlist is empty.")
        else:
            print("\n===== Your Wishlist =====")
            for item in self.wishlistInfo:
                print(f"- {item.name} (${item.price:.2f})")
    
    #Here is where I put in the order functions - Vincent
    def placeorder(self, item):
        """Stores a simple order record in the customer's orderHistory"""
        order_record = {
            "item": item.name,
            "status": "Processing" 
        }
        self.orderHistory.append(order_record)
        print(f"\nOrder placed for {item.name}! Status: processing")
    
    def vieworderStatus(self):
        if not self.orderHistory:
            print("You have no orders yet.")
        else:
            print("\n===== Your Orders =====")
            for order in self.orderHistory:
                print(f"Item: {order['item']} | Status: {order['status']}")

    def checkout(self, wishlistInfo):
        print("=========Checkout==========")
        for e in wishlistInfo:
            print(f"- {e.name} (${e.price:.2f})")

        con = ask_yes_no("Proceed to checkout with these items?: ")
        if con:
            print("=========Receipt=========")
            print("success! Order Placed")
            print("Order Completed With Card Payment: ")
            print(self.paymentInfo)

    #I decided to update the customerportal -Vincent
    def customerPortal(self, inv):
        run = True
        while run == True:
            print("\n=== Customer Portal ===")
            print("1. Browse Catalog")
            print("2. View Wishlist")
            print("3. View Order Status") #Just added this -Vincent
            print("4. Message (placeholder)")
            print("5. checkout")
            print("6. Exit")
           
            option = int(input("Enter Option: "))

            if option == 1:
                self.browseItems(inv)
            elif option == 2:
                self.viewWishlist()
            elif option == 3:
                self.vieworderStatus()
            elif option == 4:
                print("pretend you see messages")

            elif option == 5:
                q = ask_yes_no("Proceed to Checkout?: ")
                if not q:
                    run = True
                    continue
                if q:
                    self.checkout(self.wishlistInfo)

            elif option == 6:
                run = False
            else: 
                print("Invalid option. Please try again.")





class Ceo(User):
    def __init__(self, name, password, ceoID):
        super().__init__(name, password)
        self.ceoID = ceoID

    def ceoPortal(self):
        run = True
        while run == True:
            print("1. View Reports")
            print("\n")
            print("2. Exit")

            choice = int(input("Enter choice: "))
            if choice == 1:
                print("pretend you see reports")
            if choice == 2:
                run = False
                return





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


customer_info = [
    {"name": "alice", "password": "alice123", "role": "customer", "address": "123 Street", "paymentInfo": "Visa 1234", "wishlistID": 1},
    {"name": "Timmy", "password": "5678", "role": "customer", "address": "78 street", "paymentInfo": "visa 6789", "wishlistID": 34}

                 ]

def register(user_db):
    print("__________Registration__________ ")
    username = input("Username: ")
    password = input("Password: ") #reenter password


    print("Choose Account Type: 1. Staff  2. Customer")
    accountType = int(input("New Account Type: "))


    if accountType == 1:
        code = input("Enter Staff Account Code: ")
        STAFF_REGISTRATION_CODE = "2467"
        if code == STAFF_REGISTRATION_CODE:
            role = "staff"
            staff_id = input("Enter a four digit Staff ID: ")
            newuserinfo = {"name": username, "password": password, "role": "staff", "staffID": staff_id}
            user_db.append(newuserinfo)
            print(user_db)

        else:
            print("Could Not create Staff Account")
            return False



        return True


    if accountType == 2:
        role = "customer"
        address = input("Enter Shipping Address: ")
        paymentInfo = input("Enter Card type and number (e.g. Visa 1234 5678:) ") #added missing parentheses here -Vincent
        wishlistID = random.randint(100, 999) #add function to make sure the wishlist ID is unique here
        newuserinfo = {"name": username, "password": password, "role" : role, "address": address, "paymentInfo": paymentInfo, "wishlistID": wishlistID}
        user_db.append(newuserinfo)
        customer_info.append(newuserinfo)
        return True


#the user inputs their desired role and it is assigned to them when it is added into the database.

def ask_yes_no(prompt):
    #Ask the user a Y/N question and return True for Yes, False for No.
    choice = input(prompt + " (Y/N): ").strip().upper()
    while choice not in ['Y', 'N']:
        choice = input("Invalid input. Please enter Y or N: ").strip().upper()
    return choice == 'Y'





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

    # test inventory setup (unchanged)
    staff1 = Staff("bob", "boblikeshotdogs", 12345)
    staff1.addItem(inv, 16374, "apple", "description", 2.95, 5, 0)
    staff1.addItem(inv, 85848, "grape", "description", 3.45, 5, 2)
    staff1.addItem(inv, 78493, "cranberry", "description", 5.97, 6, 4)
    staff1.addItem(inv, 45672, "oranges", "description", 3.26, 4, 5)
    staff1.addItem(inv, 34567, "watermelon", "description", 4.25, 3, 5)


    while True:
        print("Welcome to the Shopping Mall")
        print("_____________________________")
        print("\n")
        has_account = ask_yes_no("Do you have an account?")

        if has_account:
            pass  #skips to login below
        else:
            success = register(user_db)
            if success:
                print("User Registered")
            else:
                print("Registration failed")
                try_again = ask_yes_no("Try registering again?")
                # if false it'll restart main menu
                if not try_again:
                    continue


        max_attempts = 4
        attempts = 0
        currentUser = None

        while not currentUser and attempts < max_attempts: #currentUser not always defined?
            currentUser = login(user_db)

            if currentUser:
                break  #exit loop if there is a currentUser

            attempts += 1
            print("\nLogin Failed. Incorrect username or password.")

            if attempts >= max_attempts:
                print("too many failed attempts\n")
                break

            wants_register = ask_yes_no("Register as a new user?")

            if wants_register:
                success = register(user_db)
                if success:
                    print("registration is now complete\n")
                    currentUser = login(user_db)
                    if currentUser:
                        break
                else:
                    print("Registration failed. Please try again later.\n")
            else:
                retry = ask_yes_no("Try logging in again?")
                if not retry:
                    print("Returning to main menu...\n")
                    break #exit login loop


            if not currentUser:
                continue  #if there isnt a currentUser just return to the top




            print(f"\nLogged in as {currentUser.name} ({currentUser.__class__.__name__})\n") #this will happen if a currentUser is recognized

        if isinstance(currentUser, Staff):
            print("Staff Portal")
            currentUser.staffPortal(inv)
            condition = input("Would you like to log out? Y or N: ")

            while condition.upper() == "N":
                currentUser.staffPortal(inv)
                condition = input("Would you like to log out? Y or N: ")
            del currentUser
            continue

        elif isinstance(currentUser, Customer):
            print("Welcome to the Shopping Mall!")
            print("\n")
            currentUser.customerPortal(inv)
            x = input("Would you like to log out? Y or N: ")

            while x.upper() == "N":
                currentUser.customerPortal(inv)
                x = input("Would you like to log out? Y or N: ")
            del currentUser
            continue


        elif isinstance(currentUser, Ceo):
            print("View Reports")
            currentUser.ceoPortal()
            y = input("Would you like to log out? Y or N: ")

            while y.upper() == "N":
                currentUser.ceoPortal()
                y = input("Would you like to log out? Y or N: ")
            del currentUser
            continue



        back_to_menu = ask_yes_no("Return to main menu?") #ask if logged out user wnats to go back to main menu
        if not back_to_menu:
            print("Goodbye!")
            break  #exit outer loop
################ :/ idk yall but ill fix it.


    if currentUser:
        print(f"\nLogged in as {currentUser.name} ({currentUser.__class__.__name__})\n")



    if isinstance(currentUser, Staff):
        print("Staff Portal")
        currentUser.staffPortal(inv)
        condition = input("Would you like to log out? Y or N: ")


        while condition.upper() == "N":
            currentUser.staffPortal(inv)
            condition = input("Would you like to log out? Y or N: ")
        del currentUser





    elif isinstance(currentUser, Customer):
        print("Welcome to the Shopping Mall!")
        print("\n")
        currentUser.customerPortal(inv)
        x = input("Would you like to log out? Y or N: ")
    elif isinstance(currentUser, Ceo):
        print("View Reports")
        currentUser.ceoPortal()





if __name__ == "__main__":
    main()

