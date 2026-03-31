from database.db import get_connection

class BaseRepository:
    def fetchall(self, sql, params=()):
        conn = get_connection()
        rows = conn.execute(sql, params).fetchall()
        conn.close()
        return rows

    def fetchone(self, sql, params=()):
        conn = get_connection()
        row = conn.execute(sql, params).fetchone()
        conn.close()
        return row

    def execute(self, sql, params=()):
        conn = get_connection()
        cur = conn.execute(sql, params)
        conn.commit()
        lastrowid = cur.lastrowid
        conn.close()
        return lastrowid
