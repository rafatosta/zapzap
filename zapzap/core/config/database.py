import sqlite3
import os
from PyQt6.QtCore import QStandardPaths
from zapzap import __appname__


class Database:
    DATABASE_DIR = os.path.join(
        QStandardPaths.writableLocation(
            QStandardPaths.StandardLocation.AppLocalDataLocation
        ), 
        __appname__, 
        'db'
    )
    DATABASE_FILE = os.path.join(DATABASE_DIR, 'zapzap.db')

    @staticmethod
    def _ensure_directory_exists():
        """Ensure the database directory exists."""
        if not os.path.exists(Database.DATABASE_DIR):
            os.makedirs(Database.DATABASE_DIR, exist_ok=True)

    @staticmethod
    def connect_db():
        """Create a connection to the database, ensuring the directory exists."""
        Database._ensure_directory_exists()
        conn = sqlite3.connect(Database.DATABASE_FILE)
        conn.execute("PRAGMA foreign_keys = ON")  # Ensure foreign key constraints are enabled
        return conn
