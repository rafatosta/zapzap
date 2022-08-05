import sqlite3
import os

from zapzap import DATABASE_FILE
from zapzap.controllers.main_window_components.builder_icon import SVG_DEFAULT
import zapzap.model.user as user


def connect_db():
    # cria a conexão
    conn = sqlite3.connect(DATABASE_FILE)
    conn.execute("PRAGMA foreign_keys = on")
    return conn


def createDB():
    # sempre ao abrir verifica e cria as tabelas caso necessário
    if(not os.path.isfile(DATABASE_FILE)):
        conn = connect_db()
        cursor = conn.cursor()
        user.createTable(cursor)
        conn.commit()
        conn.close()
        #create default user
        user.UserDAO.add(user.User(0,'User 1',SVG_DEFAULT,True))
