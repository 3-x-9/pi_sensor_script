import sqlite3, datetime, os

class DatabaseManager:
    def __init__(self, db_path="ph_data.db"):
        self.db_path = os.path.abspath(db_path)
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sensorId TEXT,
                    phvalue REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    synced INTEGER DEFAULT 0)
                    ''')
        self.conn.commit()

    def save_locally(self, device_id, ph_value):
        self.cursor.execute('''INSERT INTO readings (sensorId, phvalue) VALUES (?, ?)''', (device_id, ph_value))
        self.conn.commit()

    def get_unsynced(self):
        self.cursor.execute("SELECT * FROM readings WHERE synced = 0")
        return self.cursor.fetchall()

    def sync_change(self, id_list):
        if not id_list:
            return
        placeholder = ",".join("?" * len(id_list))
        query = f"UPDATE readings SET synced = 1 WHERE id IN ({placeholder})"
        self.cursor.execute(query, id_list)
        self.conn.commit()

    def close_conn(self):
        self.conn.close()