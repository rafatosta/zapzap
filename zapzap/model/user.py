
import zapzap.model.db as db


def createTable(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS "users" (
        "id" INTEGER,
        "name" TEXT NOT NULL,
        "icon" TEXT,
        "enable" INTEGER DEFAULT 1,
        PRIMARY KEY("id" AUTOINCREMENT)
    );
    """)

#SALVAR A IMAGEM COMO TEXTO PARA PODER MANIPULAR DEPOIS 
#COLOCAR UMA COR ALEATÓRIA 

class User():
    def __init__(self, id, name, icon, enable) -> None:
        self.id = id
        self.name = name
        self.icon = icon
        self.enable = enable

    def data(self):
        return [self.name, self.icon, self.enable]


class UserDAO():

    def add(user: User) -> User:
        try:
            conn = db.connect_db()
            cursor = conn.cursor()
            SQL = """INSERT INTO users (name, icon, enable) VALUES (?,?,?);"""
            cursor.execute(SQL, user.data())
            conn.commit()
        except Exception as e:
            print(e)
        else:
            id = cursor.execute("select last_insert_rowid()").fetchall()[0][0]
            return UserDAO.selectID(id)
        finally:
            conn.close()
    
    def update(user):
        # atualiza todos os campos de um contato
        try:
            conn = db.connect_db()
            cursor = conn.cursor()
            sql = """UPDATE users SET name=?, icon=?,enable=? WHERE id=?;"""
            l = user.data()
            # insere o id no final da lista para ficar igual a sequência do SQL
            l.append(user.id)
            cursor.execute(sql, l)
            conn.commit()
        except Exception as e:
            print(e)
        finally:
            conn.close()

    def select():
        list = []
        try:
            conn = db.connect_db()
            cursor = conn.cursor()
            SQL = """SELECT * FROM users;"""
            cursor.execute(SQL)
            temp_list = cursor.fetchall()
            for i in temp_list:
                list.append(User(i[0], i[1], i[2], i[3]))
        finally:
            conn.close()
        return list

    def selectID(id):
        try:
            conn = db.connect_db()
            cursor = conn.cursor()
            SQL = """SELECT * FROM users WHERE id = ?;"""
            cursor.execute(SQL, [id])
            u = cursor.fetchall()[0]
            return User(u[0], u[1], u[2], u[3])
        finally:
            conn.close()

    
    def delete(id):
        # deleta um contato a partir do seu id
        try:
            conn = db.connect_db()
            cursor = conn.cursor()
            sql = """DELETE FROM users WHERE id = ?;"""
            cursor.execute(sql, [id])
            conn.commit()
        except Exception as e:
            print(e)
        finally:
            conn.close()
