import aiosqlite
import pathlib

db_path = pathlib.Path('.').resolve() / 'rating.db'


async def get_connection():
    connection = await aiosqlite.connect(db_path)
    yield connection
    await connection.close()


