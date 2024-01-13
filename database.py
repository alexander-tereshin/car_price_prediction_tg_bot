import pathlib
import sqlite3


def init_db():
    db_path = pathlib.Path('.').resolve() / 'rating.db'
    if db_path.exists():
        return
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    cursor.execute("CREATE TABLE rating(client_id INTEGER primary key unique , rating INTEGER, ts DATETIME)")
    connection.commit()
    cursor.close()
    connection.close()

