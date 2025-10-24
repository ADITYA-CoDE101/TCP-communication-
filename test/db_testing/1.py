import mysql.connector
from mysql.connector import Error

def connect_db():
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234")
        
        if conn.is_connected():
            print("Successfully connected to MySQL database")
            cursor = conn.cursor()
            try:
                cursor.execute("USE chat;")
                conn.commit()
            except:
                print("database 'chat' does not exist")
                conn.close()

    except:
        print("failer!")
        if conn.is_connected():
            conn.close()

connect_db()