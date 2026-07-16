# database/db_manager.py
import sqlite3
import json
from datetime import datetime

class DBManager:
    def __init__(self, db_path="disaster_log.db"):
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._create_table()

    def _create_table(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS disasters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                location TEXT,
                disaster_type TEXT NOT NULL,
                severity_level INTEGER,
                description TEXT,
                measures TEXT,
                sensor_data TEXT,
                image_path TEXT
            )
        ''')
        self.conn.commit()

    def log_disaster(self, location, disaster_type, severity, description, measures, sensor_data, image_path=None):
        ts = datetime.now().isoformat()
        sensor_json = json.dumps(sensor_data, ensure_ascii=False)
        self.conn.execute('''
            INSERT INTO disasters 
            (timestamp, location, disaster_type, severity_level, description, measures, sensor_data, image_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (ts, location, disaster_type, severity, description, measures, sensor_json, image_path))
        self.conn.commit()
        print(f"[DB] 已记录灾害: {disaster_type} @ {ts}")

    def query(self, disaster_type=None, start_time=None, end_time=None, limit=50):
        sql = "SELECT * FROM disasters WHERE 1=1"
        params = []

        if disaster_type:
            sql += " AND disaster_type = ?"
            params.append(disaster_type)
        if start_time:
            sql += " AND timestamp >= ?"
            params.append(start_time)
        if end_time:
            sql += " AND timestamp <= ?"
            params.append(end_time)

        sql += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)

        cursor = self.conn.execute(sql, params)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in rows]

    def query_by_type(self, disaster_type):
        return self.query(disaster_type=disaster_type)

    def close(self):
        self.conn.close()
