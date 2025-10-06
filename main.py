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
        self.paymentInfo = paymentInfo
        self.wishlistInfo = wishlistID

class Ceo(User):
    def __init__(self, name, password, ceoID):
        super().__init__(name, password)
        self.ceoID = ceoID

