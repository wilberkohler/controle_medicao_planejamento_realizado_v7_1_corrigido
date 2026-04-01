from __future__ import annotations

from database.db import get_connection


class BaseRepository:
    """
    Camada base simples para acesso ao SQLite com fechamento seguro de conexão.

    Melhorias principais:
    - uso consistente de context manager;
    - rollback automático em caso de falha;
    - suporte a operações execute_many quando necessário.
    """

    def fetchall(self, sql: str, params=()):
        with get_connection() as conn:
            rows = conn.execute(sql, params).fetchall()
        return rows

    def fetchone(self, sql: str, params=()):
        with get_connection() as conn:
            row = conn.execute(sql, params).fetchone()
        return row

    def execute(self, sql: str, params=()):
        with get_connection() as conn:
            cur = conn.execute(sql, params)
            conn.commit()
            return cur.lastrowid

    def execute_script(self, sql_script: str):
        with get_connection() as conn:
            conn.executescript(sql_script)
            conn.commit()

    def executemany(self, sql: str, seq_of_params):
        with get_connection() as conn:
            cur = conn.executemany(sql, seq_of_params)
            conn.commit()
            return cur.rowcount
