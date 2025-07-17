import sqlite3
from colorama import Fore, Back, Style
import hashlib
import os

connection = sqlite3.connect("example.sqlite3")

DB_EXTENSION = ".sqlite3"

DATABASES_DICT = {
    "changelogs": """
    CREATE TABLE IF NOT EXISTS logs
        (
        Date TEXT NOT NULL CHECK(typeof(Date) = 'text'),
        Title TEXT NOT NULL CHECK(typeof(Title) = 'text'),
        Changes TEXT NOT NULL CHECK(typeof(Changes) = 'text'),
        ID INTEGER PRIMARY KEY AUTOINCREMENT
        )
    """,

    "users": """
    CREATE TABLE IF NOT EXISTS users
    (
        Username TEXT UNIQUE CHECK(typeof(Username) = 'text'),
        Password TEXT CHECK(typeof(Password) = 'text'),
        Checksum TEXT UNIQUE CHECK(typeof(checksum) = 'text')
    )
    """,

    "sessions": """
    CREATE TABLE IF NOT EXISTS sessions
    (
        ID TEXT UNIQUE NOT NULL CHECK(typeof(ID) = 'text'),
        Token TEXT UNIQUE NOT NULL CHECK(typeof(Token) = 'text'),
        Time INTEGER NOT NULL CHECK(typeof(Time) = 'integer')
    )
    """,
}

class CRUD():
    def __init__(self):
        self.createDatabases()
        self.initializeDatabases()

    def createDatabases(self):
        for database, _ in DATABASES_DICT.items():
            open(database + DB_EXTENSION, "a")

    def initializeDatabases(self):
        for database, initQuery in DATABASES_DICT.items():
            self.openConnection(database + DB_EXTENSION)
            self.cursor.execute(initQuery)
            self.closeConnection()

    def openConnection(self, db):
        ''' Open database connection '''
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()
    
    def closeConnection(self):
        ''' Save and close database connection '''
        self.connection.commit()
        self.connection.close()

    def create(self, database:str, table:str, values=(), columns=()):
        if columns == ():
            self.openConnection(database + DB_EXTENSION)
            secureQuery = f"INSERT INTO {table} VALUES ({self.GetValuesPlaceholder(values)})"
            self.ExecuteSecureQuery(secureQuery, values)
            self.closeConnection()
        else:
            self.openConnection(database + DB_EXTENSION)
            secureQuery = f"INSERT INTO {table} {columns} VALUES ({self.GetValuesPlaceholder(values)})"
            self.ExecuteSecureQuery(secureQuery, values)
            self.closeConnection()


    def read(self, database:str, table:str):
        self.openConnection(database + DB_EXTENSION)
        self.cursor.execute(f"SELECT * FROM {table}")
        result = self.cursor.fetchall()
        self.closeConnection()
        return result

    def update(self, database: str, table: str, columns, whereColumn: str, whereValue, values):
        self.openConnection(database + DB_EXTENSION)
    
        # Construct SET clause like: "col1 = ?, col2 = ?, col3 = ?"
        set_clause = ", ".join([f"{col} = ?" for col in columns])
        query = f"UPDATE {table} SET {set_clause} WHERE {whereColumn} = ?"
    
        # Add the WHERE value at the end of the values list
        parameters = values + [whereValue]
    
        self.ExecuteSecureQuery(query, parameters)
        self.closeConnection()


    def delete(self, database:str, table:str, whereColumn:str, whereValue):
        self.openConnection(database + DB_EXTENSION)
        query = f"DELETE FROM {table} WHERE {whereColumn} = ?"
        self.ExecuteSecureQuery(query, (whereValue,))
        self.closeConnection()

    def GetValuesPlaceholder(self, values, placeholder="?"):
        for i in range(0, len(values) - 1):
            placeholder += ",?"
        return placeholder

    def ExecuteSecureQuery(self, query, params=()):
        ''' Handle execution in a safe way '''
        try:
            self.cursor.execute(query, params)
            print(Fore.GREEN + "Secure query successful!" + Style.RESET_ALL)
        except sqlite3.Error as e:
            print(Fore.RED + f"Error while executing the following query: {query}\n{e}" + Style.RESET_ALL)
            return False

        return True
    
    def generateSessionToken(self):
        randomBytes = os.urandom(32)
        sha256 = hashlib.sha256(randomBytes)
        return sha256.hexdigest()

    def generateHash(self, username:str, password:str):
        combinedBytes = str(username + password).encode("utf-8")
        hashedBytes = hashlib.sha256(combinedBytes)
        return hashedBytes.hexdigest()
    
    def areCredsValid(self, enteredHash):
        allUsers = self.read("users", "Users")
        for username, password, storedHash in allUsers:
            if (enteredHash == storedHash):
                return True
        return False
    
    def isSessionValid(self, request):
        activeSessions = self.read("sessions", "sessions")
        print(activeSessions)
        enteredID = request.COOKIES.get("ID")
        enteredSessionToken = request.COOKIES.get("SESH_TOKEN")
        for id, token, time in activeSessions:
            if id == enteredID:
                if enteredSessionToken == token and time < int(time + 1800):
                    return True
                else:
                    print("attempting to delete session with ID: " + enteredID)
                    self.delete("sessions", "sessions", "ID", enteredID)
        return False
    

if __name__ == "__main__":
    db = CRUD()
    print("Direct exection. Registering new user.")
    username = input("Enter username > ")
    password = input("Enter password > ")
    db.create("users", "Users", (username, password, db.generateHash(username,password)))