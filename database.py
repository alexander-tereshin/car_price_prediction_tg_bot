import pathlib
import sqlite3
from typing import Tuple, Any, Optional

import aiosqlite

db_path = pathlib.Path(".").resolve() / "rating.db"


class Database:
    def __init__(self):
        self.conn: Optional[aiosqlite.Connection] = None

    async def connect(self):
        try:
            self.conn = await aiosqlite.connect(db_path)
        except aiosqlite.Error:
            pass

    @property
    def is_connected(self) -> bool:
        return self.conn is not None

    @staticmethod
    async def _fetch(cursor, mode) -> Optional[Any]:
        if mode == "one":
            return await cursor.fetchone()
        if mode == "many":
            return await cursor.fetchmany()
        if mode == "all":
            return await cursor.fetchall()

        return None

    async def execute(
        self, query: str, values: Tuple = (), *, fetch: str = None
    ) -> Optional[Any]:
        cursor = await self.conn.cursor()

        await cursor.execute(query, values)
        data = await self._fetch(cursor, fetch)
        await self.conn.commit()

        await cursor.close()
        return data


DB = Database()


async def init_db():
    await DB.connect()
    if db_path.exists():
        return
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute(
        "CREATE TABLE rating(client_id INTEGER primary key unique , rating INTEGER, ts DATETIME)"
    )
    connection.commit()
    cursor.close()
    connection.close()
