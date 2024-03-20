import pytest
import sys
import os

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from database import DB, init_db


@pytest.fixture
async def db():
    await init_db()
    yield DB
    if DB.is_connected:
        await DB.conn.close()


@pytest.mark.asyncio
async def test_db_connect():
    await DB.connect()
    assert DB.is_connected


@pytest.mark.asyncio
async def test_execute_without_fetch(db):
    query = "INSERT INTO rating VALUES (?, ?, ?)"
    values = (123, 5, "2024-03-20 10:00:00")

    cursor = AsyncMock()
    cursor.execute.return_value.__aenter__.return_value = None

    DB.conn = AsyncMock()
    DB.conn.cursor.return_value = cursor

    data = await DB.execute(query, values)

    cursor.execute.assert_called_once_with(query, values)
    DB.conn.commit.assert_called_once()

    assert data is None


@pytest.mark.asyncio
async def test_init_db():
    connection_mock = MagicMock()
    cursor_mock = MagicMock()
    cursor_mock.fetchone.return_value = None

    with patch("database.sqlite3.connect", return_value=connection_mock):
        with patch.object(connection_mock, "cursor", return_value=cursor_mock):
            await init_db()

            cursor_mock.execute.assert_any_call(
                "select name from sqlite_schema where type='table' and name='rating'"
            )
            cursor_mock.execute.assert_any_call(
                "CREATE TABLE rating(client_id INTEGER primary key unique , rating INTEGER, ts DATETIME)"
            )
            connection_mock.commit.assert_called_once()


@pytest.mark.asyncio
async def test_fetch_all():
    query = "SELECT * FROM rating"
    result = [(1, 5, "2024-03-20 10:00:00")]

    cursor_mock = AsyncMock()
    cursor_mock.fetchall.side_effect = lambda: result

    DB.conn = AsyncMock()
    DB.conn.cursor.return_value = cursor_mock

    data = await DB.execute(query, fetch="all")

    cursor_mock.execute.assert_called_once_with(query, ())
    cursor_mock.fetchall.assert_called_once()
    assert data == result


if __name__ == "__main__":
    pytest.main()
