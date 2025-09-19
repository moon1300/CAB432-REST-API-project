import mysql.connector

def get_db_connection():
    conn = mysql.connector.connect(
        host="localhost",
        user="root", 
        password="V8r$9tLq#2pX!mF7", 
        database="CAB432db"
    )
    return conn