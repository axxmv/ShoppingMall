# Shopping Mall
import datetime
import time
import os
import subprocess
import platform
import mysql.connector as mysql
import random
mydb=mysql.connect(host='localhost',user='root',passwd='Gothmikasa88')
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
  shipping      VARCHAR(64) DEFAULT "Shipped",
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
    id INT AUTO_INCREMENT PRIMARY KEY,
    report_type VARCHAR(20),
    file_path VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);""")


def add_default_ceo_if_missing():
    # Check if CEO already exists
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='ceo';")
    count = cursor.fetchone()[0]

    if count == 0:

        # Default credentials (you can change them)
        ceo_id= 7989
        ceo_username = "admin_ceo"
        ceo_name= "Mr Troy"
        ceo_email = "ceo@shoppingmall.com"
        ceo_password = "ceo1234"       # store plain or hashed depending on your system
        ceo_role = "ceo"

        # Insert CEO
        cursor.execute("""
            INSERT INTO users (id,username,name, email, password_hash, role)
            VALUES (%s, %s, %s, %s,%s,%s);
        """, (ceo_id,ceo_username,ceo_name, ceo_email, ceo_password, ceo_role))

        mydb.commit()
    else:
        pass



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




def validate_card_details(card_number, exp_date, cvv, card_type):
    """
    Simple local validation for card number, expiry and CVV.
    This does NOT contact any real payment gateway.
    """

    # Normalize
    card_number = card_number.replace(" ", "")
    card_type = card_type.lower().strip()

    # 1) Card number basic checks
    if not card_number.isdigit():
        print("Card number must contain digits only.")
        return False

    if len(card_number) < 13 or len(card_number) > 19:
        print("Card number length is invalid.")
        return False

    # Very basic type hint (optional)
    if card_type == "credit" or card_type == "debit":
        # Example: you can enforce Visa starts with 4, MasterCard 5, etc.
        # For now we just accept any prefix to keep it simple.
        pass

    # 2) Expiry date: expected format mm/yyyy
    try:
        parts = exp_date.split("/")
        if len(parts) != 2:
            print("Expiry must be in MM/YYYY format.")
            return False

        month = int(parts[0])
        year = int(parts[1])

        if month < 1 or month > 12:
            print("Expiry month must be between 1 and 12.")
            return False

        # We consider expiry at end of the month
        now = datetime.datetime.now()
        # card expired if year < current year or same year but month < current month
        if year < now.year or (year == now.year and month < now.month):
            print("Card is expired.")
            return False
    except ValueError:
        print("Invalid expiry format.")
        return False

    # 3) CVV basic check
    if not cvv.isdigit():
        print("CVV must contain digits only.")
        return False

    if len(cvv) not in (3, 4):
        print("CVV must be 3 or 4 digits.")
        return False

    # Passed all simple checks
    return True


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

    def viewcustomerinfo(self):
        key = input("Enter customer username or email: ").strip()
        cursor.execute("SELECT id, username, email FROM users WHERE role='customer' AND (username=%s OR email=%s);", (key, key))
        user = cursor.fetchone()
        if not user:
            print("No customer found.")
            return
        _id,name,email=user
        print(f"\nCustomer: {name} ({email})")
        cursor.execute("SELECT id, total_amount, status, created_at, shipping FROM orders WHERE user_id=%s ORDER BY created_at DESC;", (_id,))
        orders = cursor.fetchall()
        print("\nOrders:")
        if not orders:
            print("  (none)")
        else:
            for o in orders:
                id_, amt, status,created_at, shp = o
                print(f"  Order #{id_} | ${float(amt):.2f} | {status} | {created_at} | {shp}")
        cursor.execute("""
            SELECT i.id, i.name, i.price FROM wishlists w
            JOIN items i ON i.id=w.item_id
            WHERE w.user_id=%s ORDER BY i.name;
        """, (_id,))
        wl = cursor.fetchall()
        print("\nWishlist:")
        if not wl:
            print("  (empty)")
        else:
            for it in wl:
                print(f"  {it['id']} | {it['name']} | ${float(it['price']):.2f}")

                
    def staff_message(self):
        cursor.execute("""
            SELECT m.id, u.username AS from_user, m.message, m.created_at
            FROM messages m JOIN users u ON u.id=m.customer_id
            AND m.status='unread' ORDER BY m.created_at ASC;
            """)
        msgs = cursor.fetchall()

        if not msgs:
            print("\nNo new messages.")
            return

        print("\nUnread messages:")
        for m in msgs:
            _id,user,body,created_at=m
            print(f"#{_id} from {user} at {created_at}\n{body}\n---")

        answer = ask_yes_no("Want to reply any message")
        while answer:
            
            mid = int(input("Enter message ID to reply: ").strip())
            reply = input("Reply: ").strip()
            cursor.execute("SELECT customer_id FROM messages WHERE id=%s ;", (mid,))
            orig = cursor.fetchone()
            cus_id=orig
            if not orig:
                print("Message not found or not addressed to you.")
                return
            
            cursor.execute("UPDATE messages SET status='read',reply=%s,replied_at = NOW() WHERE id=%s;", (reply,mid))
            mydb.commit()
            print("Reply sent & original marked read.")
            answer = ask_yes_no("Want to reply any message")
                

    def staffPortal(self, inv):

        run = True
        while run == True:
            print("1. View Inventory")
            print("2. Add Item ")
            print("3. Remove Item")
            print("4. Modify Item")
            print("5. Refill Inventory")
            print("6. View Customer Information ")
            print("7. Messages ")
            print("8. Exit")

            option = int(input("\nEnter Option: "))

            if option == 1:
                show_inventory()

            if option == 2:
                name = input("Enter the Item name: ")
                itemId = int(input("Enter the Item ID: "))
                description = input("Item Description: ")
                price = float(input("price: "))
                stock = int(input("Amount in stock: "))
                likeCounter = 0

                self._addItemtoInventory(itemId, name, description, price, stock, likeCounter)
                show_inventory()
                
            if option == 3:
                itemId = int(input("Enter the Item ID: "))
                self._removeItemfromInventory(itemId )
                show_inventory()

            if option == 4:
                itemId = int(input("Enter the Item ID: "))
                self._modifyIteminInventory(itemId)
                
                
            if option == 5:
                itemId = int(input("Enter the Item ID to update stocks: "))
                num= int(input("Enter the number of items to be added to stocks: "))#need to run a loop that stays on untill refilling is completed
                self._refillInventory(itemId,num)
                
            if option ==6:
                self.viewcustomerinfo()
            
            if option == 7:
                self.staff_message()
                
            if option == 8:
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
                choice = input("\nEnter Item ID to view details (or 'B' to go back):")
                if choice.lower() == 'b':
                    return
                itemId = int(choice)
                cursor.execute("SELECT * FROM items WHERE id=%s;", (itemId,))
                info= cursor.fetchone()
                
                if not info:
                    print("Item not found. Please try again.")
                    try_again = ask_yes_no("\nTry entering id again ?")
                    if not try_again:
                        return
                else:
                    id_, name, desc, price, stock, like_count = info
                    print(f"\nID: {id_}, Name: {name}, Description: {desc or 'N/A'}")
                    print(f"Price: ${price}, Stock: {stock}, Likes: {like_count} ")
                    action = input("\nWould you like to (L)ike, Add to (W)ishlist, or Go (B)ack? ")
                    if action.upper() == 'L':
                        cursor.execute("UPDATE items SET like_count = like_count + 1 WHERE id=%s;", (id_,))
                        mydb.commit()
                        print(f"You Liked {name}")
                        
                    elif action.upper() == 'W':
                        self. add_wishlist(id_)
                        #need to add double adding of wishlist to
                
                    elif action.upper() == 'B':
                        return
                    else:
                        print("Invalid choice.")
            except ValueError:
                    print("Please enter a valid item ID or 'b' to go back.")
                
    def print_receipt(self, order_id, lines, total, payment_type, last4):
        """
        Print a simple text receipt to the console after checkout.
        lines = list of (item_id, qty, price)
        total = final total (with tax if you used tax)
        """
        print("\nThank You for Shopping with Us. ")
        print("Your Order was successfully placed!")
        print("Order confirmation and receipt was sent to your email.")
        print("")
        print("\n========= RECEIPT =========")
        print(f"Order ID: {order_id}")
        print(f"Customer: {self.name} (ID: {self.user_id})")
        print(f"Email: {self.email}")
        print(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Payment: {payment_type.title()} card ending with {last4}")
        print("----------------------------")

        subtotal = 0.0

        for item_id, qty, price in lines:
            qty = int(qty)
            price = float(price)
            line_total = qty * price
            subtotal += line_total

            # fetch item name
            cursor.execute("SELECT name FROM items WHERE id=%s;", (item_id,))
            row = cursor.fetchone()
            if row:
                item_name = row[0]
            else:
                item_name = f"Item {item_id}"

            print(f"{item_name} x{qty} @ ${price:.2f} = ${line_total:.2f}")

        print("----------------------------")
        print(f"Subtotal: ${subtotal:.2f}")

        # If your total already includes tax, you can compute tax like this:
        tax = float(total) - subtotal
        if tax < 0:
            tax = 0.0
        print(f"Tax:      ${tax:.2f}")
        print(f"TOTAL:    ${float(total):.2f}")
        print("============================\n")

    
    def initiateCheckout(self,total,lines):
        
        print("=========Checkout==========")
        
        tax=10/100 # can change tax from here
        tax_amount=float(total)*(tax)
        total_tax= float(total)+ tax_amount
        
        print(f"Total amount: {total}")
        print(f"Tax: {tax_amount}")
        print(f"Total after Tax= {total_tax} ")

        ptype = input("Pay by (Credit/debit). Please Enter: 'credit' or 'Debit': ").strip().lower()
        if ptype not in ("credit", "debit"):
            print("Invalid payment type.")
            return
        card = input("Enter Card number (only last 4 stored): ").strip()
        exp_date= input("Enter expiration month and year (mm/yyyy): ")
        cvv= input ("Enter CVV : ")
        last4 = card[-4:] if len(card) >= 4 else "0000"
        if validate_card_details(card,exp_date,cvv,ptype): #validate_card_details
            cursor.execute("INSERT INTO orders (user_id, total_amount, status) VALUES (%s,%s,'paid');", (self.user_id, total_tax))
            oid = cursor.lastrowid
            for item_id, qty, price in lines:
                cursor.execute("INSERT INTO order_items (order_id, item_id, quantity, price) VALUES (%s,%s,%s,%s);", (oid, item_id, qty, price))
                cursor.execute("UPDATE items SET stock = stock - %s WHERE id=%s;", (qty, item_id))

            cursor.execute("INSERT INTO payments (order_id, card_type, last4, status) VALUES (%s,%s,%s,'captured');",
                        (oid, ptype, last4))
            cursor.execute("DELETE FROM wishlists WHERE user_id=%s;", (self.user_id,))
            mydb.commit()
            self.print_receipt(oid, lines, total_tax, ptype, last4)
            

        

    def remove_wishlist(self):
        item_id = input("Enter item ID to remove from wishlist: ").strip()

        while not item_id.isdigit():
            item_id = input("Enter item ID to remove from wishlist: ").strip()

        item_id = int(item_id)

##checks the order ID is valid

        if item_id > 5 or item_id < 1:
            print("No Item with that ID")
            return

        cursor.execute("DELETE FROM wishlists WHERE user_id=%s AND item_id=%s;", (self.user_id, item_id))
        mydb.commit()
        #add condition
        print("Removed from wishlist.")


        

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
        option = ""
        while option.upper() !="B":
            option=input("Want to initiate (C)heckout , (R)emove an item from wishlist or go (B)ack: ")
            if option.upper() == "C":
                if self.initiateCheckout(total,lines):
                    self.print_receipt(order_id, lines, total, payment_type, last4)
                
                return
            elif option.upper() == "R":
                self.remove_wishlist()

            elif option.upper()== "B":
                return
            else:
                print("Invalid Option.")


                
    def ask_for_help(self):
        #Customer sends a help message to staff.
        msg = input("\nEnter your message for staff: ").strip()
        if not msg:
            print("Message cannot be empty.")
            return

        sql = "INSERT INTO messages (customer_id, message) VALUES (%s, %s);"
        cursor.execute(sql, (self.user_id, msg))
        mydb.commit()

        print("✅ Your message has been sent. A staff member will reply soon.")
        
    
    def view_my_messages(self):
        #Customer views all their messages and replies.
        sql = """
            SELECT id, message, reply, status,created_at,replied_at FROM messages
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

            
    def view_order_status(self):
        oid = input("Enter your Order ID: ").strip()
        while not oid.isdigit():
            oid = input("Enter your Order ID: ").strip()

        int(oid)
        cursor.execute("SELECT id, user_id, status, created_at, total_amount,shipping  FROM orders WHERE id=%s; ", (oid,))
        o = cursor.fetchone()
#######
        if o is None:
            print("Order not found.")
            return
####### go back to menu if the order is not found
        _id, uid, status, created_at, amt, shp = o
        if not o:
            print("Order not found.")
            return
        if int(uid) != int(self.user_id):
            print("You can only view your own orders.")
            return

        print(f"\nOrder #{_id} | Status: {status} | Total: ${float(amt):.2f} | Placed: {created_at} | Tracking info: {shp}")

            
    def customerPortal(self, inv):
        run = True
        while run == True:
            print("\n=== Customer Portal ===")
            print("1. Browse Catalog")
            print("2. View Wishlist")
            print("3. View Order Status")
            print("4. HelpDesk")
            print("5. Exit")

            try:
                option = int(input("Enter Option: "))
            except ValueError:
                print("Invalid input. Please enter a number from 1–5.")
                continue  # restart menu


            if option == 1:
                self.browseItems(inv )
            elif option == 2:
                self.viewWishlist()
            elif option == 3:
                self.view_order_status()
            elif option == 4:
                option_2=0
                while option_2 != 3:
                    print("\n=== Help Desk ===")
                    print("1. Message Staff")
                    print("2. View my messages")
                    print("3. Back")
                    option_2 = input("Enter Option: ")
                    if not option_2.isdigit():
                        option_2 = input("Enter Option: ")

                    option_2 = int(option_2)


                    if option_2 == 1:
                        self.ask_for_help()
                    elif option_2 == 2:
                        self.view_my_messages()
                    elif option_2 == 3:
                        break
                    else:
                        print("Invalid option. Please try again.")
                
            elif option == 5:
                run = False
            else: 
                print("Invalid option. Please try again.")





class Ceo(User):
    def __init__(self, name, ceoID):
        super().__init__(name)
        self.ceoID = ceoID


    def generate_daily_report(self):
        today = datetime.date.today()
        date_str = today.strftime("%Y-%m-%d")

        # Fetch daily orders & sales
        sql = """
            SELECT i.name, SUM(oi.quantity) AS qty, SUM(oi.price * oi.quantity)
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN items i ON i.id = oi.item_id
            WHERE DATE(o.created_at) = %s
            GROUP BY i.name;
        """
        cursor.execute(sql, (today,))
        rows = cursor.fetchall()

        # Prepare content
        report_text = f"====== DAILY REPORT ({date_str}) ======\n\n"
        if not rows:
            report_text += "No sales today.\n"
        else:
            total_sales =0
            for r in rows:
                name,qty,amount=r
                amount = float(amount)
                total_sales += amount
                report_text += f"{name} | Qty: {qty} | Sales: ${amount:.2f}\n"
    
            report_text += f"\nTOTAL SALES: ${total_sales:.2f}\n"

        # Save file
        file_name = f"daily_report_{date_str}.txt"
        file_path = os.path.join("reports", file_name)

        os.makedirs("reports", exist_ok=True)

        with open(file_path, "w") as f:
            f.write(report_text)

        # Save to database
        cursor.execute("INSERT INTO reports (report_type, file_path) VALUES (%s,%s)",
                       ("daily", file_path))
        mydb.commit()

        print(f"\nDaily report generated: {file_path}")

        
    def generate_monthly_report(self):
        year = int(input("Enter year (YYYY): "))
        month = int(input("Enter month (1–12): "))

        start_date = datetime.date(year, month, 1)
        if month == 12:
            end_date = datetime.date(year + 1, 1, 1)
        else:
            end_date = datetime.date(year, month + 1, 1)

        sql = """
            SELECT i.name, SUM(oi.quantity) AS qty, SUM(oi.price * oi.quantity)
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            JOIN items i ON i.id = oi.item_id
            WHERE o.created_at >= %s AND o.created_at < %s
            GROUP BY i.name;
        """
        cursor.execute(sql, (start_date, end_date))
        rows = cursor.fetchall()

        report_text = f"====== MONTHLY REPORT ({year}-{month:02d}) ======\n\n"

        if not rows:
            report_text += "No sales recorded.\n"
        else:
            total_sales = 0
            for r in rows:
                name, qty, amount = r
                amount = float(amount)
                total_sales += amount
                report_text += f"{name} | Qty: {qty} | Sales: ${amount:.2f}\n"

            report_text += f"\nTOTAL SALES: ${total_sales:.2f}\n"

        file_name = f"monthly_report_{year}_{month:02d}.txt"
        file_path = os.path.join("reports", file_name)

        os.makedirs("reports", exist_ok=True)

        with open(file_path, "w") as f:
            f.write(report_text)

        cursor.execute("INSERT INTO reports (report_type, file_path) VALUES (%s,%s)",
                   ("monthly", file_path))
        mydb.commit()

        print(f"\nMonthly report generated: {file_path}")




    def run_report_scheduler():
        print("Report scheduler started. Will run daily/monthly reports at 21:00 (9 PM).")
        last_daily_run = None          # store last date daily ran
        last_monthly_run = None        # store (year, month) of last monthly run

        while True:
            now = datetime.now()
            today = now.date()

            # Check if it's 9:00 PM (21:00)
            if now.hour == 21 and now.minute == 0:
                # ---- DAILY REPORT ----
                if last_daily_run != today:
                    print(f"[{now}] Running DAILY report for {today}...")
                    generate_daily_report_for_date(today)
                    last_daily_run = today

                # ---- MONTHLY REPORT ----
                month_key = (today.year, today.month)
                if last_monthly_run != month_key:
                    print(f"[{now}] Running MONTHLY report for {today.year}-{today.month:02d}...")
                    generate_monthly_report_for(today.year, today.month)
                    last_monthly_run = month_key

                # Sleep a bit so we don’t run multiple times within the same minute
                time.sleep(60)

            # Check every 30 seconds
            time.sleep(30)

    def view_reports(self):
        cursor.execute("SELECT id, report_type, file_path, created_at FROM reports ORDER BY created_at DESC")
        rows = cursor.fetchall()

        if not rows:
            print("\nNo reports found.")
            return

        print("\n=== Reports List ===\n")
        for r in rows:
            rid, rtype, path, created = r
            print(f"[{rid}] {rtype.upper()} | Created: {created} | File: {path}")

        choice = input("\nEnter report ID to view (or 0 to go back): ")

        if not choice.isdigit() or int(choice) == 0:
            return

        report_id = int(choice)

        cursor.execute("SELECT file_path FROM reports WHERE id=%s", (report_id,))
        rp = cursor.fetchone()

        if not rp:
            print("Invalid report ID.")
            return

        file_path = rp[0]

        if not os.path.exists(file_path):
            print("Report file not found.")
            return

        print(f"\nOpening: {file_path}")
    
        # Open file cross-platform
        if platform.system() == "Darwin":       # macOS
            subprocess.call(["open", file_path])
        elif platform.system() == "Windows":
            os.startfile(file_path)             # Windows only
        else:                                   # Linux
            subprocess.call(["xdg-open", file_path])
    
    
    def ceoPortal(self):
        run = True
        while run == True:
            print("\n1. Generate Daily Reports")
            print("2. Generate Monthly Reports")
            print("3. View Daily Report")
            print("4. View Monthly Report")
            print("5. Exit")

            choice = int(input("Enter choice: "))
            if choice == 1:
                self.generate_daily_report()
            if choice == 2:
                self.generate_monthly_report()
            if choice == 3:
                self.view_reports()
            if choice == 4:
                continue
            if choice == 5:
                run = False
                return


    

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
    ###########################################






    username = input("Username: ")
    name= input("Name: ")
    email= input("Email: ")
    password = input("Password: ") #reenter password

    print("Choose Account Type: 1. Staff  2. Customer")
    accountType = input("New Account Type: ")

    while not accountType.isdigit():
        print("Choose Account Type: 1. Staff  2. Customer")
        accountType = input("New Account Type: ")

    accountType = int(accountType)



    if accountType == 1:
        code = input("Enter Staff Account Code: ")
        while not code:
            print("Code cannot be empty.")
            code = input("Enter Staff Account Code: ").strip()
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

    else:
        print("Invalid Input. Please enter 1 or 2: ")



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
                return Ceo(name,user_id)




def main():
    inv=Inventory()
    add_default_ceo_if_missing()


    while True:
        print("Welcome to the Shopping Mall")
        print("_____________________________")
        print("\n")
        has_account = ask_yes_no("Do you have an account?")
        print("\n")
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
                    break #exit login loop


            if not currentUser:
                continue  #if there isnt a currentUser just return to the top




            # print(f"\nLogged in as {currentUser.name} ({currentUser.__class__.__name__})\n") #this will happen if a currentUser is recognized

        if isinstance(currentUser, Staff):
            print("\nStaff Portal")
            currentUser.staffPortal(inv)
            condition = input("Would you like to log out? Y or N: ")

            while condition.upper() == "N":
                currentUser.staffPortal(inv)
                condition = input("Would you like to log out? Y or N: ")
            del currentUser
            continue

        elif isinstance(currentUser, Customer):
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


if __name__ == "__main__":
    main()
    
