import mysql.connector
class Purchase:
    def __init__(self,host="localhost",user="root",password="root",database="bookstore"):
        self.connect=mysql.connector.connect(host=host,
                                             user=user,password=password,
                                             database=database)
        self.cursor = self.connect.cursor()
        self.userid = None

    def login(self, name, password):
        try:
            query = "Select *from users where username=%s and password=%s"
            self.cursor.execute(query, (name, password))
            result = self.cursor.fetchone()
            if (result):
                self.userid = result[0]  # store id to track purchase
                print("Login Successfully")
                return True
            else:
                print("Wrong username or password")
                return False
        except Exception as e:
            print(f"Error during login: {e}")
            return False

    def register(self, name, password):
        try:
            query="select *from users where username=%s"
            self.cursor.execute(query,(name,))
            result=self.cursor.fetchone()
            if result:
                print("username already exist.choose another name.")
                return False

            query="insert into users(username,password) values(%s,%s)"
            self.cursor.execute(query, (name,password))
            self.connect.commit()

            query = "SELECT id FROM users WHERE username=%s"
            self.cursor.execute(query, (name,))
            self.userid = self.cursor.fetchone()[0]
            print("Registered successfully. you r now logged in.")
            return True
        except Exception as e:
            print(f"error during registration: {e}")
            return False

    def update_user(self,userid,newname,newpassword):
        try:
            query="update users set username=%s,password=%s where id=%s"
            self.cursor.execute(query,(newname,newpassword,userid))
            self.connect.commit()
            print("user details updated successfully")
        except Exception as e:
            print(f"Error updating user details:{e}")

    def access(self, option):
        if (option == "login"):
            name = input("Enter your name :")
            password = input("Enter password :")
            return self.login(name, password)
        elif (option=="reg"):
            print("Enter your name and password to register")
            name = input("enter your name :")
            password = input("enter your password :")
            return self.register(name, password)
        else:
            return False

class Start(Purchase):
    def begin(self):
        print("\n\t\t\t\t\t Welcome to Online Book Purchasing\n\t\t\t\t\t\t Discount offers available")
        while True:
            option = input("Do you want to login or register? (login/reg): ").strip().lower()
            if option in ["login", "reg"]:
                success=self.access(option)
                if success:
                    return True
                else:
                    print("Failed ,Re Enter")
            else:
                print("Invalid input. Please try again.")

class Onlinebookstore(Purchase):
    def __init__(self, connection, cursor):
        super().__init__()
        self.connect = connection
        self.cursor = cursor
    def display_books(self):
        print("\nAvailable Books:")
        for book in books:
            print(f"{book['id']}. {book['title']} - ${book['price']:.2f}")
            conversion_rate = 85  # convert to rupee
            print(f"{book['id']}. {book['title']} - ₹{book['price'] * conversion_rate:.2f}")

    def apply_discount(self, total_cost):
        if total_cost >= 30:  # 20% discount
            discount_rate = 20
        elif total_cost >= 20:  # 10% discount
            discount_rate = 10
        else:  # No discount
            discount_rate = 0

        discount_amount = total_cost * (discount_rate / 100)
        final_price = total_cost - discount_amount
        return final_price, discount_rate

    def purchase_book(self,userid):
        if not userid:
            print("You must log in before purchasing a book.")
            return 0
        try:
            book_id = int(input("\nEnter the ID of the book you want to purchase: "))
            for book in books:
                if book["id"] == book_id:
                    print(f"You have chosen '{book['title']}' that cost is ${book['price']:.2f}")
                    # Apply discount to this book only
                    discounted_price, discount_rate = self.apply_discount(book["price"])

                    if discount_rate > 0:
                        print(f"Discount applied: {discount_rate}%")
                        print(f"Final price after discount: ${discounted_price:.2f}")
                    else:
                        print("No discount applied.")
                    query = "INSERT INTO purchases (userid, book_id, book_title, price) VALUES (%s, %s, %s, %s)"
                    self.cursor.execute(query, (userid, book["id"], book["title"], discounted_price))
                    self.connect.commit()
                    return discounted_price

            # invalid book
            print("Invalid book ID. Please try again.")
            return 0
        except ValueError:
            print("Please enter a valid number.")
            return 0

    def view_purchases(self, userid):
        try:
            query = "SELECT book_title, price FROM purchases WHERE userid=%s"
            self.cursor.execute(query, (userid,))
            purchases = self.cursor.fetchall()
            if purchases:
                print("\nYour Purchases:")
                for purchase in purchases:
                    print(f"Title: {purchase[0]}, Price: ${purchase[1]:.2f}")
            else:
                print("No purchases found.")
        except Exception as e:
            print(f"Error fetching purchases: {e}")

    def add_review(self, userid):
        try:
            book_id = int(input("Enter the ID of the book you want to review: "))
            query = "SELECT book_title FROM purchases WHERE userid=%s AND book_id=%s"
            self.cursor.execute(query, (userid, book_id))
            result = self.cursor.fetchone()
            if result:
                book_title = result[0]
                review = input(f"Enter your review for '{book_title}': ")
                query = "INSERT INTO reviews (userid, book_id, book_title, review) VALUES (%s, %s, %s, %s)"
                self.cursor.execute(query, (userid, book_id, book_title, review))
                self.connect.commit()
                print("Review added successfully.")
            else:
                print("You can only review books you have purchased.")
        except ValueError:
            print("Please enter a valid book ID.")
        except Exception as e:
            print(f"Error adding review: {e}")

    def main(self,userid):

        total_cost = 0

        while True:
            print("\n1. View Books")
            print("2. purchase Book")
            print("3. view purchases")
            print("4. review books")
            print("5. Update user details")
            print("6. Checkout and Exit")
            try:
                choice = int(input("Enter your choice: "))
                if choice == 1:
                    self.display_books()
                elif choice == 2:
                    total_cost += self.purchase_book(userid)
                elif choice == 3:
                    self.view_purchases(userid)
                elif choice==4:
                    self.add_review(userid)
                elif choice==5:
                    newname = input("Enter new username: ")
                    newpassword = input("Enter new password: ")
                    self.update_user(userid, newname, newpassword)
                elif choice == 6:
                    print(f"\nYour total cost is: ${total_cost:.2f}")
                    print(f"You have purchased the book for ${total_cost:.2f}")
                    print("Thank you for shopping ! Goodbye...")
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")

books = [
    {"id": 1, "title": "The Great Gatsby", "price": 10.99},
    {"id": 2, "title": "To Kill a Mockingbird", "price": 8.99},
    {"id": 3, "title": "1984", "price": 35.99},
    {"id": 4, "title": "Pride and Prejudice", "price": 9.99},
    {"id": 5, "title": "Moby Dick", "price": 20.99},
    {"id": 6, "title": "Dracula by Bram stoker", "price":25},
    {"id": 7, "title": "IT by stephen King", "price":11.9},
    {"id": 8, "title": "Frankenstein by mary shelley", "price":18.99},
    {"id": 9, "title": "The Twilight saga by stephenie meyer", "price":45.99},
    {"id": 10, "title": "The Bible", "price":15}
]
store=Start()
if store.begin():
    buy = Onlinebookstore(store.connect,store.cursor)
    buy.main(store.userid)
else:
    print("Failed authentication")
