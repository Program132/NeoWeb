import sqlite3
from typing import List, Dict

class DatabaseManager:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.connection = None

    def connect(self):
        try:
            self.connection = sqlite3.connect(self.db_path)
            self.connection.execute("PRAGMA journal_mode=WAL")
        except sqlite3.Error as e:
            print(f"Erreur de connexion à la base de données: {e}")
            self.connection = None

    def execute_query(self, query: str, params=None):
        if params is None:
            params = []
        cursor = self.connection.cursor()
        cursor.execute(query, params)
        self.connection.commit()
        return cursor.fetchall()

    def create_table(self, table_name: str, columns: Dict[str, str]):
        if not self.connection:
            raise ConnectionError("La connexion à la base de données n'est pas établie.")

        columns_definitions = ', '.join([f"{col} {dtype}" for col, dtype in columns.items()])
        query = f"CREATE TABLE IF NOT EXISTS {table_name} ({columns_definitions});"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query)
            self.connection.commit()
        except sqlite3.OperationalError as e:
            raise sqlite3.OperationalError(
                f"Erreur lors de la création de la table '{table_name}'."
            ) from e

    def add_entry(self, table: str, data: Dict[str, str]):
        if not self.connection:
            raise ConnectionError("La connexion à la base de données n'est pas établie.")

        columns = ', '.join(data.keys())
        placeholders = ', '.join(f":{key}" for key in data.keys())
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, data)
            self.connection.commit()
        except sqlite3.OperationalError as e:
            raise sqlite3.OperationalError(
                f"Erreur lors de l'insertion : la table '{table}' n'existe pas ou les colonnes sont incorrectes."
            ) from e

    def add_entries(self, table: str, entries: List[Dict[str, str]]):
        for entry in entries:
            self.add_entry(table, entry)

    def get_value_from_url(self, table: str, column: str, url: str):
        if not self.connection:
            raise ConnectionError("La connexion à la base de données n'est pas établie.")

        query = f"SELECT {column} FROM {table} WHERE url = {url}"
        cursor = self.connection.cursor()
        cursor.execute(query, (url,))
        result = cursor.fetchone()

        return result[0] if result else None

    def close(self):
        if self.connection:
            self.connection.close()
