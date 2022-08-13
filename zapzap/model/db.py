import sqlite3
import os

from zapzap import DATABASE_FILE
from zapzap.controllers.main_window_components.builder_icon import SVG_DEFAULT
import zapzap.model.user as user


def connect_db():
    """Create connection to the database"""
    conn = sqlite3.connect(DATABASE_FILE)
    conn.execute("PRAGMA foreign_keys = on")
    return conn


def createDB():
    """Checks if the file exists and creates the database and soon after inserts the default user"""
    if(not os.path.isfile(DATABASE_FILE)):
        # Create table
        user.UserDAO.createTable()
        # Create default user
        user.UserDAO.add(user.User(name='', icon=SVG_DEFAULT))
