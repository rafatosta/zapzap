from zapzap.config.Database import Database


class User:
    _table_name = "users"
    _fields = {
        "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
        "name": "TEXT NOT NULL",
        "icon": "TEXT",
        "enable": "INTEGER DEFAULT 1",
        "zoomFactor": "REAL DEFAULT 1.0"
    }

    def __init__(self, id='', name='', icon='', enable=True, zoomFactor=1.0) -> None:
        self._id = id
        self.name = name
        self.icon = icon
        self.enable = enable
        self.zoomFactor = zoomFactor

    @property
    def id(self):
        return 'storage-whats' if self._id == 1 else self._id

    @id.setter
    def id(self, value):
        self._id = value

    @classmethod
    def _ensure_table_exists(cls):
        """Verifica se a tabela existe; cria-a se não existir."""
        try:
            conn = Database.connect_db()
            cursor = conn.cursor()
            fields_def = ", ".join([f'"{field}" {dtype}' for field, dtype in cls._fields.items()])
            SQL = f"""CREATE TABLE IF NOT EXISTS "{cls._table_name}" ({fields_def});"""
            cursor.execute(SQL)
            conn.commit()
        except Exception as e:
            print(f"Erro ao verificar/criar a tabela {cls._table_name}: {e}")
        finally:
            conn.close()

    @staticmethod
    def create(user):
        User._ensure_table_exists()  # Verifica a tabela antes de executar
        try:
            conn = Database.connect_db()
            cursor = conn.cursor()
            fields = ", ".join(["name", "icon"])
            placeholders = ", ".join(["?"] * 2)
            SQL = f"""INSERT INTO {User._table_name} ({fields}) VALUES ({placeholders});"""
            cursor.execute(SQL, [user.name, user.icon])
            conn.commit()
            id = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
            return User.select_by_id(id)
        except Exception as e:
            print(e)
        finally:
            conn.close()

    @staticmethod
    def update(user):
        User._ensure_table_exists()  # Verifica a tabela antes de executar
        try:
            conn = Database.connect_db()
            cursor = conn.cursor()
            fields = "name=?, icon=?, enable=?, zoomFactor=?"
            SQL = f"""UPDATE {User._table_name} SET {fields} WHERE id=?;"""
            cursor.execute(SQL, [user.name, user.icon, user.enable, user.zoomFactor, user.id])
            conn.commit()
        except Exception as e:
            print(e)
        finally:
            conn.close()

    @staticmethod
    def select(enable=True):
        User._ensure_table_exists()  # Verifica a tabela antes de executar
        users = []
        try:
            conn = Database.connect_db()
            cursor = conn.cursor()
            SQL = f"""SELECT * FROM {User._table_name} WHERE enable=1;""" if enable else f"""SELECT * FROM {User._table_name};"""
            cursor.execute(SQL)
            rows = cursor.fetchall()
            for row in rows:
                users.append(User(row[0], row[1], row[2], bool(row[3]), row[4]))
        except Exception as e:
            print(e)
        finally:
            conn.close()
        return users

    @staticmethod
    def select_by_id(id):
        User._ensure_table_exists()  # Verifica a tabela antes de executar
        try:
            conn = Database.connect_db()
            cursor = conn.cursor()
            SQL = f"""SELECT * FROM {User._table_name} WHERE id = ?;"""
            cursor.execute(SQL, [id])
            row = cursor.fetchone()
            if row:
                return User(row[0], row[1], row[2], bool(row[3]), row[4])
        except Exception as e:
            print(e)
        finally:
            conn.close()

    @staticmethod
    def delete(id):
        User._ensure_table_exists()  # Verifica a tabela antes de executar
        try:
            conn = Database.connect_db()
            cursor = conn.cursor()
            SQL = f"""DELETE FROM {User._table_name} WHERE id = ?;"""
            cursor.execute(SQL, [id])
            conn.commit()
        except Exception as e:
            print(e)
        finally:
            conn.close()
