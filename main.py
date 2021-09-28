from cryptography.fernet import Fernet
from os.path import exists
import sqlite3
import getpass

def generate_key():
    """
    Generates key for encryption.
    """
    key = Fernet.generate_key()
    with open("pass.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    """
    Loads the key named `secret.key` from the current directory.
    """
    return open("pass.key", "rb").read()

def init_database():
    """
    Executed when passwords.db does not exist
    Creates new table and populates it with master password
    """
    con = sqlite3.connect('passwords.db')
    cur = con.cursor()
    cur.execute('''CREATE TABLE passwords
                (application text, email text, pwd text, key binary, master bool)''')
    pwd1 = 'a'
    pwd2 = 'b'
    while (pwd1 != pwd2):
        pwd1 = input("Enter new master password: ")
        pwd2 = input("Re-enter new master password: ")
        if (pwd1 == pwd2):
            generate_key()
            temp = load_key()
            cur.execute("INSERT INTO passwords VALUES (?, ?, ?, ?, ?)", ("n/a", "n/a", pwd1, temp, 1))
            return (con, cur)
        else:
            print("Passwords do not match.")

def check_for_app(app):
    """
    Helper method to locate row in database
    """
    if (app == "all"):
        return -1
    count = 0
    for row in cur.execute("SELECT * FROM passwords WHERE application=?", (app,)):
        count+=1
    else:
        return count

def lookup_pwd():
    # ask for application name as user input
    app = input("Enter application name (type all to show all passwords): ")
    if (check_for_app(app) == 1):
        # entry found in database
        for row in cur.execute("SELECT application, email, pwd FROM passwords WHERE application=?", (app,)):
            print(row)
    elif (check_for_app(app) == -1):
        # print all entries
        for row in cur.execute("SELECT application, email, pwd FROM passwords WHERE master!=1"):
            print(row)
    elif (check_for_app(app) == 0):
        # entry not found in database
        print("No entry found in database. Returning to main menu...")

def store_pwd():
    # ask for app name, password
    app = input("Enter application name: ")
    if (check_for_app(app) == 0):
        email = input("Enter email: ")
        pwd1 = input("Enter password: ")
        pwd2 = input("Re-enter password: ")
        if (pwd1 == pwd2):
            generate_key()
            temp = load_key()
            cur.execute("INSERT INTO passwords VALUES (?, ?, ?, ?, ?)", (app, email, pwd1, temp, 0))
        else:
            print("Passwords do not match. Returning to main menu...")
            return
    else:
        print("Entry for application already found in database. Returning to main menu...")

def update_pwd():
    # ask for app name and confirm
    app = input("Enter application name: ")
    if (check_for_app(app) == 1):
        print("What would you like to do with this application?")
        print("1. Update password\n2. Delete entry from database")
        intent = int(input("Enter number here: "))
        if (intent == 1):
            pwd1 = input("Enter new password: ")
            pwd2 = input("Re-enter password: ")
            if (pwd1 == pwd2):
                generate_key()
                temp = load_key()
                # sql update statement
                cur.execute("UPDATE passwords SET pwd=? WHERE application=?", (pwd1, app))
            else:
                print("Passwords do not match. Returning to main menu...")
                return
        elif (intent == 2):    
            cur.execute("DELETE FROM passwords WHERE application=?", (app,))
        else:
            print("Invalid input. Returning to main menu...")
    else:
        print("No entry found in database. Returning to main menu...")


def update_master():
    count = 0
    for row in cur.execute("SELECT * FROM passwords WHERE master=1"):
        count+=1
    if (count == 0):
        print("No master password found.")
        pwd1 = input("Enter new master password: ")
        pwd2 = input("Re-enter new master password: ")
        if (pwd1 == pwd2):
            generate_key()
            temp = load_key()
            cur.execute("INSERT INTO passwords VALUES (?, ?, ?, ?, ?)", ("n/a", "n/a", pwd1, temp, 1))
        else:
            print("Passwords do not match. Returning to main menu...")
            return
    else:
        master = input("Enter master password: ")
        cur.execute("SELECT pwd FROM passwords WHERE master=1")
        if (master == cur.fetchone()[0]):
            pwd1 = input("Enter new master password: ")
            pwd2 = input("Re-enter new master password: ")
            if (pwd1 == pwd2):
                generate_key()
                temp = load_key()
                cur.execute("UPDATE passwords SET pwd=? WHERE master=1", (pwd1,))
            else:
                print("Passwords do not match. Returning to main menu...")
        else:
            print("Incorrect master password. Returning to main menu...")

def save_and_exit():
    """
    Commit changes to database and exit program.
    """
    con.commit()
    con.close()
    quit()

def get_intent(a):
    """
    Method called to check user's intent
    """
    intent_dict = {
        1: lookup_pwd,
        2: store_pwd,
        3: update_pwd,
        4: update_master,
        5: save_and_exit
    }
    return intent_dict[int(a)]()

def main():
    print("PASSWORD MANAGER\n")
    master = getpass.getpass(prompt="Master password: ")
    cur.execute("SELECT pwd FROM passwords WHERE master=1")
    if (master != cur.fetchone()[0]):
        print("Incorrect master password. Exiting Password Manager...")
        quit()
    running = True
    while running:
        print("\nMAIN MENU -- Please select from the following options:")
        print("1. Look up password\n2. Store a new password\n3. Update an existing password\n4. Change master password\n5. Save and exit")
        intent = input("Enter number here: ")
        get_intent(intent)

if not exists('passwords.db'):
    db = init_database()
    con = db[0]
    cur = db[1]
    main()
else:
    con = sqlite3.connect('passwords.db')
    cur = con.cursor()
    main()