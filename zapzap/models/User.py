class User():
    def __init__(self, id='', name='', icon='', enable=True, zoomFactor=1.0) -> None:
        self.id = id
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

    @staticmethod
    def select():
        # Simulando dados retornados do SELECT
        data = [
            (1, "Alice", "icon1.png", 1, 1.2),
            (2, "Bob", "icon2.png", 0, 1.0),
            (3, "Charlie", None, 1, 1.1),
            (4, "Diana", "icon4.png", 1, 1.3),
            (5, "Eve", None, 0, 1.0),
        ]

        # Convertendo para objetos User
        users = [User(id=row[0], name=row[1], icon=row[2], enable=bool(
            row[3]), zoomFactor=row[4]) for row in data]
        return users
