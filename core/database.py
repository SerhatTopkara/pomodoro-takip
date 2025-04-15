import sqlite3
import os
from datetime import datetime

class DatabaseManager:
    def __init__(self, db_path="data/pomodoro.db"):
        
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.db_path = db_path
        self.conn = None
    
    def get_connection(self):
        if self.conn is None:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def setup_database(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Çalışma seansları tablosu.
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS work_sessions (
            id INTEGER PRIMARY KEY,
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            duration INTEGER,
            is_completed BOOLEAN DEFAULT 0,
            session_type TEXT DEFAULT 'work'
        )
        ''')
        
        # Ayarlar tablosu.
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            id INTEGER PRIMARY KEY,
            work_duration INTEGER DEFAULT 25,
            short_break_duration INTEGER DEFAULT 5,
            long_break_duration INTEGER DEFAULT 15,
            sessions_before_long_break INTEGER DEFAULT 4,
            sound_enabled BOOLEAN DEFAULT 1
        )
        ''')
        
        # Varsayılan ayarları ekle.
        cursor.execute('INSERT OR IGNORE INTO settings (id) VALUES (1)')
        
        conn.commit()
    
    def save_session(self, start_time, end_time, duration, is_completed=True, session_type="work"):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO work_sessions (start_time, end_time, duration, is_completed, session_type) VALUES (?, ?, ?, ?, ?)',
            (start_time, end_time, duration, is_completed, session_type)
        )
        conn.commit()
    
    def get_sessions_by_date(self, date):
        conn = self.get_connection()
        cursor = conn.cursor()
        date_str = date.strftime("%Y-%m-%d")
        cursor.execute(
            'SELECT * FROM work_sessions WHERE date(start_time) = ? ORDER BY start_time',
            (date_str,)
        )
        return cursor.fetchall()
    
    def get_statistics(self, start_date, end_date):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            '''
            SELECT date(start_time) as work_date, 
                   SUM(duration) as total_duration,
                   COUNT(*) as session_count
            FROM work_sessions 
            WHERE date(start_time) BETWEEN ? AND ?
              AND session_type = 'work'
              AND is_completed = 1
            GROUP BY date(start_time)
            ORDER BY work_date
            ''',
            (start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
        )
        return cursor.fetchall()
    
    def get_settings(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM settings WHERE id = 1')
        return dict(cursor.fetchone())
    
    def update_settings(self, settings_dict):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        
        query = 'UPDATE settings SET '
        updates = []
        values = []
        
        for key, value in settings_dict.items():
            if key != 'id':
                updates.append(f"{key} = ?")
                values.append(value)
        
        query += ", ".join(updates) + " WHERE id = 1"
        
        cursor.execute(query, values)
        conn.commit()
        
    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None 