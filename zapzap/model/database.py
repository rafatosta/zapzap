import sqlite3
from PyQt6.QtCore import QStandardPaths

def connect():  # conexão do banco de dados
    # cria a conexão
    path_data = QStandardPaths.writableLocation(
        QStandardPaths.StandardLocation.AppLocalDataLocation)
    return sqlite3.connect(path_data+'/db.sqlite')


def createDB():
    conn = connect()
    cursor = conn.cursor()
    #cursor.execute(user.tableUser())
    conn.commit()
    conn.close()
