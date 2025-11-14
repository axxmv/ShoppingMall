# Shopping Mall

import mysql.connector as mysql
import random
mydb=mysql.connect(host='localhost',user='root',passwd='MeghP169')
cursor=mydb.cursor()


##Creating Databse
cursor.execute("CREATE DATABASE IF NOT EXISTS shopping_mall")
cursor.execute("USE shopping_mall")


##Creating ALL TABLES
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
  id              BIGINT PRIMARY KEY,
  username        VARCHAR(64)  NOT NULL UNIQUE,
  name            CHAR(64) NOT NULL,
  email           VARCHAR(255) NOT NULL UNIQUE,
  password_hash   VARCHAR(255) NOT NULL,
  role            ENUM('customer','staff','ceo') NOT NULL DEFAULT 'customer'
  )""")  
cursor.execute("""CREATE TABLE IF NOT EXISTS items(
  id          BIGINT PRIMARY KEY AUTO_INCREMENT,
  name        VARCHAR(128) NOT NULL UNIQUE,
  description TEXT,
  price       DECIMAL(10,2) NOT NULL,
  stock       INT NOT NULL DEFAULT 0,
  like_count  INT NOT NULL DEFAULT 0
  )""")
cursor.execute("""CREATE TABLE IF NOT EXISTS like_items(
  user_id     BIGINT NOT NULL,
  item_id     BIGINT NOT NULL,
  PRIMARY KEY (user_id, item_id),
  CONSTRAINT fk_like_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_like_item FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
  )""")
cursor.execute("""CREATE TABLE IF NOT EXISTS wishlists (
  user_id     BIGINT NOT NULL,
  item_id     BIGINT NOT NULL,
  quantity    BIGINT NOT NULL DEFAULT 0,
  PRIMARY KEY (user_id, item_id),
  CONSTRAINT fk_w_user FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
  CONSTRAINT fk_w_item FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id BIGINT NOT NULL,
    staff_id BIGINT NULL,
    message TEXT NOT NULL,
    reply TEXT NULL,
    status ENUM('unread','read') NOT NULL DEFAULT 'unread',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    replied_at TIMESTAMP NULL,
    FOREIGN KEY (customer_id) REFERENCES users(id),
    FOREIGN KEY (staff_id) REFERENCES users(id)
);""")
cursor.execute("""CREATE TABLE IF NOT EXISTS orders (
  id            BIGINT PRIMARY KEY AUTO_INCREMENT,
  user_id       BIGINT NOT NULL,
  total_amount  DECIMAL(10,2) NOT NULL,
  status        ENUM('processing','paid','shipped','delivered','cancelled') NOT NULL DEFAULT 'paid',
  created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_order_user FOREIGN KEY (user_id)
    REFERENCES users(id) ON DELETE CASCADE
)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS order_items (
  order_id     BIGINT NOT NULL,
  item_id      BIGINT NOT NULL,
  quantity     INT NOT NULL,
  price        DECIMAL(10,2) NOT NULL,  -- snapshot price at purchase time
  PRIMARY KEY (order_id, item_id),
  CONSTRAINT fk_oi_order FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
  CONSTRAINT fk_oi_item FOREIGN KEY (item_id) REFERENCES items(id) ON DELETE CASCADE
)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS payments (
  id         BIGINT PRIMARY KEY AUTO_INCREMENT,
  order_id   BIGINT NOT NULL UNIQUE,
  card_type  ENUM('credit','debit') NOT NULL,
  last4      CHAR(4) NOT NULL,
  status     ENUM('authorized','captured','failed') NOT NULL DEFAULT 'captured',
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  CONSTRAINT fk_payment_order FOREIGN KEY (order_id)
    REFERENCES orders(id) ON DELETE CASCADE
)""")
cursor.execute("""CREATE TABLE IF NOT EXISTS reports (
  id           BIGINT PRIMARY KEY AUTO_INCREMENT,
  report_type  ENUM('daily','monthly') NOT NULL,
  period_start DATE NOT NULL,
  period_end   DATE NOT NULL,
  file_ref     VARCHAR(255) NOT NULL,
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
)""")


#For random but Uniqe user ids
def get_unique_random_id():
    while True:
        rid = random.randint(10000, 99999)
        cursor.execute("SELECT 1 FROM users WHERE id=%s;", (rid,))
        if not cursor.fetchone():
            return rid


STARTER_ITEMS = [
    ("Wireless Mouse", "Ergonomic 2.4 GHz wireless mouse", 19.99, 25),
    ("Mechanical Keyboard", "RGB backlit mechanical keyboard", 59.99, 10),
    ("USB-C Cable", "1m fast-charging cable", 9.99, 100),
    ("Noise Cancelling Headphones", "Over-ear ANC headphones", 129.99, 5),
    ("Smartwatch", "Water-resistant fitness tracker", 99.00, 15),]

#Adding items to inventory when if empty
def seed_items_if_empty():
    try:
        # Is the table empty?
        cursor.execute("SELECT COUNT(*) FROM items;")
        (cnt,) = cursor.fetchone()
        if cnt and cnt > 0:
            return  # already seeded

        # Insert starter items
        cursor.executemany(
            "INSERT INTO items (name, description, price, stock) VALUES (%s, %s, %s, %s);",STARTER_ITEMS )
        mydb.commit()
        print(f"Seeded {cursor.rowcount} starter items.")
    finally:
        pass

#Shows current Inventory   
def show_inventory():
    print("\n===== Available Items =====")
    cursor.execute("SELECT * FROM items ORDER BY like_count DESC, id ASC")
    inventry=cursor.fetchall()

    if not inventry:
        print("\n No items found in the inventory.")
    else:
        print("\n Current Inventory:\n")
        for item in inventry:
            id_, name, desc, price, stock, like_count = item
            print(f"ID: {id_}, Name: {name}")
            print("-" * 40)  # separator line

    

class User:
    def __init__(self, name):
        self.name = name

        
class Staff(User):
    def __init__(self, name, staffID):
        super().__init__(name)
        self.staffID = staffID
    
    def _addItemtoInventory(self, itemId, name, description, price, stock, likeCounter): #creates the item and adds it to inventory at the sane time
        sql = "INSERT INTO items (id,name, description, price, stock, like_count) VALUES (%s, %s, %s, %s,%s,%s);"
        cursor.execute(sql,(itemId,name,description,price,stock,likeCounter))
        mydb.commit()

    def _removeItemfromInventory(self, itemId):
        cursor.execute("DELETE FROM items WHERE id=%s;", (itemId,))
        mydb.commit()
        print('item deleted')

    def _modifyIteminInventory(self, itemId):
        cursor.execute("SELECT * FROM items WHERE id=%s;", (itemId,))
        info= cursor.fetchone()
        id_, name, desc, price, stock, like_count = info
        print("Original Item Info")
        print(f"ID: {id_}, Name: {name}, Description: {desc or 'N/A'}")
        print(f"Price: ${price}, Stock: {stock}, Likes: {like_count} ")
        print("** N to keep the original ** ")
        name_new= input("Enter the new Name : ")
        desc_new= input("Enter the new description : ")
        price_new= float(input("Enter New Price : "))
        sql = "UPDATE items SET name=%s, description=%s, price=%s WHERE id=%s;"
        cursor.execute(sql,(name_new, desc_new, price_new, id_))
        mydb.commit()
        cursor.execute("SELECT * FROM items WHERE id=%s;", (itemId,))
        info= cursor.fetchone()
        id_, name, desc, price, stock, like_count = info
        print("Updated Item Info")
        print(f"ID: {id_}, Name: {name}, Description: {desc or 'N/A'}")
        print(f"Price: ${price}, Stock: {stock}, Likes: {like_count} ")
        print("** N to keep the original ** ")
        
    def _refillInventory(self, itemId, num):
        cursor.execute("SELECT stock FROM items WHERE id=%s;", (itemId,))
        info= cursor.fetchone()
        addon= num + info[0]
        sql= "UPDATE items SET stock=%s WHERE id=%s;"
        cursor.execute(sql,(addon,itemId))
        mydb.commit()
                

    def staffPortal(self, inv):

        run = True
        while run == True:
            print("1. Add Item ")
            print("2. Remove Item")
            print("3. Modify Item")
            print("4. Refill Inventory")
            print("5. View Customer Information ")
            print("6. message ")
            print("7. Exit")

            option = int(input("Enter Option: "))

            if option == 1:
                name = input("Enter the Item name: ")
                itemId = int(input("Enter the Item ID: "))
                description = input("Item Description: ")
                price = float(input("price: "))
                stock = int(input("Amount in stock: "))
                likeCounter = 0

                self._addItemtoInventory(itemId, name, description, price, stock, likeCounter)
                show_inventory()
                
            if option == 2:
                itemId = int(input("Enter the Item ID: "))
                self._removeItemfromInventory(itemId )
                show_inventory()

            if option == 3:
                itemId = int(input("Enter the Item ID: "))
                self._modifyIteminInventory(itemId)
                
                
            if option == 4:
                itemId = int(input("Enter the Item ID to update stocks: "))
                num= int(input("Enter the number of items to be added to stocks: "))#need to run a loop that stays on untill refilling is completed
                self._refillInventory(itemId,num)
                
            if option ==5:
                continue
            
            if option == 6:
                continue
                
            if option == 7:
                run = False
                return







class Customer(User): 
    def __init__(self, name, user_id, email):
        super().__init__(name)
        self.user_id = user_id
        self.email = email

    def add_wishlist(self, item_id):
        
        # ensure in stock
        cursor.execute("SELECT stock FROM items WHERE id=%s;", (item_id,))
        row = cursor.fetchone()
        if not row:
            print("Item not found.")
        elif int(row[0]) <= 0:
            print("This item is out of stock and cannot be added to your wishlist.")
        else:
            quantity= int(input("Enter number of items to add: "))
            cursor.execute("INSERT IGNORE INTO wishlists (user_id, item_id, quantity) VALUES (%s,%s,%s);", (self.user_id, item_id,quantity), quantity)
            mydb.commit()
            print("Added to wishlist.")

    #I'm adding this for the browsing and interacting with items part (Vincent)
    def browseItems(self, inv):
        
        show_inventory()

        
        while True:
            try:
                choice = input("Enter Item ID to view details (or 'B' to go back): ")
                if choice.lower() == 'b':
                    return
                itemId = int(choice)
                cursor.execute("SELECT * FROM items WHERE id=%s;", (itemId,))
                info= cursor.fetchone()
                
                if not info:
                    print("Item not found. Please try again.")
                    try_again = ask_yes_no("Try entering id again ?")
                    if not try_again:
                        return
                else:
                    id_, name, desc, price, stock, like_count = info
                    print(f"ID: {id_}, Name: {name}, Description: {desc or 'N/A'}")
                    print(f"Price: ${price}, Stock: {stock}, Likes: {like_count} ")
                    action = input("Would you like to (L)ike, Add to (W)ishlist, or Go (B)ack? ")
                    if action == 'L':
                        cursor.execute("UPDATE items SET like_count = like_count + 1 WHERE id=%s;", (id_,))
                        mydb.commit()
                        print(f"You Liked {name}")
                        
                    elif action == 'W':
                        self. add_wishlist(id_)
                        #need to add double adding of wishlist to
                        """if selected_item not in self.wishlistInfo: 
                            self.wishlistInfo.append(selected_item)
                            print(f"{selected_item.name} added to your wishlist!")
                        else:
                            print("This item is already in your wishlist.")"""
                
                    elif action == 'b':
                        return
                    else:
                        print("Invalid choice.")
            except ValueError:
                    print("Please enter a valid item ID or 'b' to go back.")
                

    def initiateCheckout(self,total,lines):
        print("=========Checkout==========")
        ptype = input("Pay by (credit/debit): ").strip().lower()
        if ptype not in ("credit", "debit"):
            print("Invalid payment type.")
            return
        card = input("Enter Card number (only last 4 stored): ").strip()
        exp_date= input("Enter expiration month and year (mm/yyyy): ")
        cvv= input ("Enter CVV : ")
        last4 = card[-4:] if len(card) >= 4 else "0000"

        cursor.execute("INSERT INTO orders (user_id, total_amount, status) VALUES (%s,%s,'paid');", (self.user_id, total))
        oid = cursor.lastrowid
        for item_id, qty, price in lines:
            cursor.execute("INSERT INTO order_items (order_id, item_id, quantity, price) VALUES (%s,%s,%s,%s);", (oid, item_id, qty, price))
            mydb.commit()
            cursor.execute("UPDATE items SET stock = stock - %s WHERE id=%s;", (qty, item_id))
            mydb.commit()

        cursor.execute("INSERT INTO payments (order_id, card_type, last4, status) VALUES (%s,%s,%s,'captured');",
                 (oid, ptype, last4))
        mydb.commit()
        cursor.execute("DELETE FROM wishlists WHERE user_id=%s;", (self.user_id,))
        mydb.commit()

        print("=========Receipt=========")
        print("success! Order Placed")
        print("Order Completed With Card Payment: ")
        

    #Creating view wishlist
    def viewWishlist(self):
        cursor.execute("""SELECT i.id, i.name, i.description, i.price, w.quantity
        FROM wishlists w JOIN items i ON i.id = w.item_id
        WHERE w.user_id=%s ORDER BY i.name ASC; """, (self.user_id,))
        rows = cursor.fetchall()
        total=0
        lines=[]
        if not rows:
            print("\nNo items in Wishlist.")
            return
        print("\nYour Wishlist:\n")
        for r in rows:
            _id, itemname, desc, price, quan= r
            print(f"ID: {_id} | {itemname} | {desc} | ${float(price):.2f} | Quanity added: {quan}")
            total+=(price*quan)
            lines.append((_id, quan, price))
        print("-" * 40)

        
        tax=10/100 # can change tac from here
        tax_amount=float(total)*(tax)
        total_tax= float(total)+ tax_amount
        print(f"Total amount: {total}")
        print(f"Tax: {tax_amount}")
        print(f"Total after Tax= {total_tax} ")
        option=input("Want to initiate (C)heckout or go (B)ack: ")
        if option == "C":
            self.initiateCheckout(total_tax,lines)
        elif option =="B":
            return
        else:
            print("Invalid Option.")


        
                
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
                
    def ask_for_help(self):
        """Customer sends a help message to staff."""
        msg = input("\nEnter your message for staff: ").strip()
        if not msg:
            print("Message cannot be empty.")
            return

        sql = "INSERT INTO messages (customer_id, message) VALUES (%s, %s);"
        cursor.execute(sql, (self.user_id, msg))
        mydb.commit()

        print("✅ Your message has been sent. A staff member will reply soon.")
    
    def view_my_messages(self):
        """Customer views all their messages and replies."""
        sql = """
            SELECT id, message, reply, status FROM messages
            WHERE customer_id = %s
            ORDER BY created_at DESC;
        """
        cursor.execute(sql, (self.user_id,))
        rows = cursor.fetchall()

        if not rows:
            print("\nYou have no messages.")
            return

        print("\n--- Your Messages & Replies ---\n")
        for r in rows:
            # r is a tuple: (id, message, reply, status, created_at, replied_at)
            mid,msg,rep,status,created_at,replied_at = r

            print(f"ID: {mid} | Status: {status} | Sent: {created_at}")
            print(f"Message: {msg}")
            if rep:
                print(f"Reply at {replied_at}: {rep}")
            else:
                print("Reply: (no reply yet)")
            print("-" * 40)
            
        
    #I decided to update the customerportal -Vincent
    def customerPortal(self, inv):
        run = True
        while run == True:
            print("\n=== Customer Portal ===")
            print("1. Browse Catalog")
            print("2. View Wishlist")
            print("3. HelpDesk")
            print("4. Exit")
           
            option = int(input("Enter Option: "))

            if option == 1:
                self.browseItems(inv )
            elif option == 2:
                self.viewWishlist()
            elif option == 3:
                print("\n=== Help Desk ===")
                print("1. Message Staff")
                print("2. View my messages")
                print("3. Back")
                option_2 = int(input("Enter Option: "))
                while option_2 != 3:
                    if option_2 == 1:
                        self.ask_for_help()
                    elif option_2 == 2:
                        self.view_my_messages()
                    else:
                        print("Invalid option. Please try again.")
                
            elif option == 4:
                run = False
            else: 
                print("Invalid option. Please try again.")





class Ceo(User):
    #def __init__(self, name, password, ceoID):
    #   super().__init__(name, password)
    #  self.ceoID = ceoID

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
    
    seed_items_if_empty()
    
    
    def __str__(self):
        if not self.inventoryList:
            return "Inventory is empty."
        return "\n".join([f" {item.name}" for item in self.inventoryList]) # "\n".join([str(item) for item in self.inventoryList]) to print details


    def _addItemtoInventory(self, itemId, name, description, price, stock, likeCounter): #creates the item and adds it to inventory at the sane time
        sql = "INSERT INTO items (id,name, description, price, stock, like_count) VALUES (%s, %s, %s, %s,%s,%s);"
        cursor.execute(sql,(itemId,name,description,price,stock,likeCounter))
        mydb.commit()

    def _removeItemfromInventory(self, itemId):
        cursor.execute("DELETE FROM items WHERE id=%s;", (itemId,))
        mydb.commit()
        print('item deleted')

    def _modifyIteminInventory(self, itemId):
        cursor.execute("SELECT * FROM items WHERE id=%s;", (itemId,))
        info= cursor.fetchone()
        id_, name, desc, price, stock, like_count = info
        print("Original iItem Info")
        print(f"ID: {id_}, Name: {name}, Description: {desc or 'N/A'}")
        print(f"Price: ${price}, Stock: {stock}, Likes: {like_count} ")
        print("** N to keep the original ** ")
        name_new= input("Enter the new Name : ")
        desc_new= input("Enter the new description : ")
        price_new= float(input("Enter New Price : "))
        sql = "UPDATE items SET name=%s, description=%s, price=%s WHERE id=%s;"
        cursor.execute(sql,(name_new, desc_new, price_new, id_))
        mydb.commit()
                
        



                 

def register():
    print("__________Registration__________ ")
    username = input("Username: ")
    name= input("Name: ")
    email= input("Email: ")
    password = input("Password: ") #reenter password

    print("Choose Account Type: 1. Staff  2. Customer")
    accountType = int(input("New Account Type: "))


    if accountType == 1:
        code = input("Enter Staff Account Code: ")
        STAFF_REGISTRATION_CODE = "2467"
        if code == STAFF_REGISTRATION_CODE:
            role = "staff"
            staff_id = get_unique_random_id()
            cursor.execute("INSERT INTO users values('{}','{}','{}','{}','{}','{}') ".format(staff_id,username,name,email,password,role))
            mydb.commit()

        else:
            print("Could Not create Staff Account")
            return False
        return True


    if accountType == 2:
        role = "customer"
        customer_id = get_unique_random_id()
        cursor.execute("INSERT INTO users values('{}','{}','{}','{}','{}','{}') ".format(customer_id,username,name,email,password,role))
        mydb.commit()
        return True


#the user inputs their desired role and it is assigned to them when it is added into the database.

def ask_yes_no(prompt):
    #Ask the user a Y/N question and return True for Yes, False for No.
    choice = input(prompt + " (Y/N): ").strip().upper()
    while choice not in ['Y', 'N']:
        choice = input("Invalid input. Please enter Y or N: ").strip().upper()
    return choice == 'Y'





def login():
    print("________Log In________")
    username = input("Enter your Username: ")
    
    sql = "SELECT * FROM users WHERE username=%s;"
    cursor.execute(sql, (username,))
    user = cursor.fetchone()
    if not user:
        print("Invalid Username. Try Again.")
        return False
    else:
        password = input("Enter your Password: ")
        sql = "SELECT * FROM users WHERE password_hash=%s;"
        cursor.execute(sql, (password,))
        pw = cursor.fetchone()
        if not pw:
            print("Invalid Password. Try Again.")
            return False
        else:
            sql="SELECT * FROM users WHERE username=%s;"
            cursor.execute(sql,(username,))
            data = cursor.fetchone()
            user_id, uname, name, email, pw_hash, role = data
            if role == "staff":
                return Staff(name, user_id)
            elif role == "customer":
                return Customer(name, user_id, email)
            else:
                return Ceo()




def main():

    inv = Inventory()


    while True:
        print("Welcome to the Shopping Mall")
        print("_____________________________")
        print("\n")
        has_account = ask_yes_no("Do you have an account?")

        if has_account:
            pass  #skips to login below
        else:
            success = register()
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
            currentUser = login()

            if currentUser:
                break  #exit loop if there is a currentUser

            attempts += 1
            print("\nLogin Failed. Incorrect username or password.")

            if attempts >= max_attempts:
                print("too many failed attempts\n")
                break

            wants_register = ask_yes_no("Register as a new user?")

            if wants_register:
                success = register()
                if success:
                    print("registration is now complete\n")
                    currentUser = login()
                    if currentUser:
                        break
                else:
                    print("Registration failed. Please try again later.\n")
            else:
                retry = ask_yes_no("Try logging in again?")
                if not retry:
                    print("Returning to main menu...\n")
                    break #exit login loop"""


            if not currentUser:
                continue  #if there isnt a currentUser just return to the top




            # print(f"\nLogged in as {currentUser.name} ({currentUser.__class__.__name__})\n") #this will happen if a currentUser is recognized

        if isinstance(currentUser, Staff):
            print("Staff Portal")
            show_inventory()
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


    #if currentUser:
        #print(f"\nLogged in as {currentUser.name} ({currentUser.__class__.__name__})\n")



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
