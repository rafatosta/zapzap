from zapzap.config.Database import Database
from zapzap.services.SettingsManager import SettingsManager


class User:

    USER_DEFAULT = 'storage-whats'

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
        self._name = name
        self._icon = icon
        self._enable = enable
        self._zoomFactor = zoomFactor

    @property
    def id(self):
        return User.USER_DEFAULT if self._id == 1 else self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = value
        self._persist()

    @property
    def icon(self):
        return self._icon

    @icon.setter
    def icon(self, value):
        self._icon = value
        self._persist()

    @property
    def enable(self):
        return self._enable

    @enable.setter
    def enable(self, value):
        self._enable = value
        self._persist()

    @property
    def zoomFactor(self):
        return self._zoomFactor

    @zoomFactor.setter
    def zoomFactor(self, value):
        self._zoomFactor = value
        self._persist()

    def __str__(self):
        return f"User(id={self.id}, name={self.name}, enable={self.enable}, zoomFactor={self.zoomFactor})"

    def _persist(self):
        """Persistir as alterações no banco de dados."""
        if self._id:
            self.update(self)

    def save(self):
        if self._id:
            User.update(self)  # Se o ID existir, faz o update
        else:
            # Caso contrário, faz o create (inserção)
            new_user = User.create(self)
            self._id = new_user.id  # Atualiza o ID com o valor gerado pelo banco

    def remove(self):
        if self._id:
            User.delete(self._id)

    @classmethod
    def _ensure_table_exists(cls):
        """Verifica se a tabela existe; cria-a se não existir."""
        try:
            conn = Database.connect_db()
            cursor = conn.cursor()
            fields_def = ", ".join(
                [f'"{field}" {dtype}' for field, dtype in cls._fields.items()])
            SQL = f"""CREATE TABLE IF NOT EXISTS "{
                cls._table_name}" ({fields_def});"""
            cursor.execute(SQL)
            conn.commit()
        except Exception as e:
            print(f"Erro ao verificar/criar a tabela {cls._table_name}: {e}")
        finally:
            conn.close()

    @staticmethod
    def create(user):
        User._ensure_table_exists()
        try:
            conn = Database.connect_db()
            cursor = conn.cursor()
            fields = ", ".join(["name", "icon", "enable", "zoomFactor"])
            placeholders = ", ".join(["?"] * 4)
            SQL = f"""INSERT INTO {User._table_name}
                ({fields}) VALUES ({placeholders});"""
            cursor.execute(SQL, [user.name, user.icon,
                           int(user.enable), user.zoomFactor])
            conn.commit()
            id = cursor.execute("SELECT last_insert_rowid()").fetchone()[0]
            return User.select_by_id(id)
        except Exception as e:
            print(e)
        finally:
            conn.close()

    @staticmethod
    def update(user):
        User._ensure_table_exists()
        try:
            id = 1 if user._id == 'storage-whats' else user._id
            conn = Database.connect_db()
            cursor = conn.cursor()
            fields = "name=?, icon=?, enable=?, zoomFactor=?"
            SQL = f"""UPDATE {User._table_name} SET {fields} WHERE id=?;"""
            cursor.execute(SQL, [user.name, user.icon, int(
                user.enable), user.zoomFactor, id])
            conn.commit()
        except Exception as e:
            print(e)
        finally:
            conn.close()

    @staticmethod
    def select():
        User._ensure_table_exists()
        users = []
        try:
            conn = Database.connect_db()
            cursor = conn.cursor()
            SQL = f"""SELECT * FROM {User._table_name} ;"""
            cursor.execute(SQL)
            rows = cursor.fetchall()
            for row in rows:
                users.append(
                    User(row[0], row[1], row[2], bool(row[3]), row[4]))
        except Exception as e:
            print(e)
        finally:
            conn.close()
        return users

    @staticmethod
    def select_by_id(id):
        User._ensure_table_exists()
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
        User._ensure_table_exists()
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

    @staticmethod
    def count_users():
        """Retorna a quantidade de usuários salvos no banco de dados."""
        User._ensure_table_exists()
        try:
            conn = Database.connect_db()
            cursor = conn.cursor()
            SQL = f"""SELECT COUNT(*) FROM {User._table_name};"""
            cursor.execute(SQL)
            count = cursor.fetchone()[0]
            return count
        except Exception as e:
            print(f"Erro ao contar os usuários: {e}")
            return 0
        finally:
            conn.close()

    @staticmethod
    def create_new_user(name='', icon=None):
        """
        Cria e retorna um novo usuário se o limite de usuários cadastrados não for excedido.
        O ícone é gerado automaticamente se não for fornecido.

        Args:
            name (str): Nome do usuário. Padrão é string vazia.
            icon (str): Ícone SVG para o usuário. Gerado automaticamente se None.
            LIMITE_USERS (int): Limite máximo de usuários permitidos. Padrão é 10.

        Returns:
            User | None: Retorna o novo usuário se criado; caso contrário, retorna None.
        """
        # Verifica o número de usuários cadastrados
        from zapzap import LIMITE_USERS
        if User.count_users() >= int(SettingsManager.get("users/size", LIMITE_USERS)):
            print(f"""Limite de {
                  SettingsManager.get("users/size", LIMITE_USERS)} usuários atingido. Não é possível criar mais usuários.""")
            return None

        # Define o ícone, se necessário
        if icon is None:
            from zapzap.resources.UserIcon import UserIcon
            icon = UserIcon.get_new_icon_svg()

        # Cria e salva o novo usuário
        new_user = User(name=name, icon=icon)
        new_user.save()
        return new_user
