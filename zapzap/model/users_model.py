import sqlite3
import os
from PyQt6.QtCore import QStandardPaths
import zapzap


# Path database
DATABASE_DIR = QStandardPaths.writableLocation(
    QStandardPaths.StandardLocation.AppLocalDataLocation)+'/'+zapzap.__appname__+'/db.sqlite'

# print(DATABASE_DIR)


def connect_db():
    conn = sqlite3.connect(DATABASE_DIR)
    return conn


def createDB():
    if os.path.isfile(DATABASE_DIR) == False:
        conn = connect_db()
        cursor = conn.cursor()
        createTableUsers(cursor)
        conn.commit()
        conn.close()
        insert('Default')


def createTableUsers(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS "users" (
        "id"	INTEGER,
        "name"	TEXT NOT NULL,
        PRIMARY KEY("id" AUTOINCREMENT)
    );
    """)


def insert(name):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        SQL = """INSERT INTO users (name) VALUES (?);"""
        cursor.execute(SQL, [name])
        conn.commit()
    finally:
        conn.close()


def update(id, name):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        SQL = """UPDATE users SET name = ? WHERE id = ?"""
        cursor.execute(SQL, [name, id])
        conn.commit()
    finally:
        conn.close()


def delete(id):
    try:
        conn = connect_db()
        cursor = conn.cursor()
        SQL = """DELETE FROM users WHERE id = ?;"""
        cursor.execute(SQL, [id])
        conn.commit()
    except Exception as e:
        print(e)
    finally:
        conn.close()


def selectAll():
    user_list = []
    try:
        conn = connect_db()
        cursor = conn.cursor()
        SQL = """SELECT * FROM users;"""
        cursor.execute(SQL)
        user_list = cursor.fetchall()
    finally:
        conn.close()
    return user_list
