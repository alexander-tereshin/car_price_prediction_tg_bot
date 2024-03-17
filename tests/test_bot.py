import pytest
import logging
from handlers import cmd_start, EntryCar

from aiogram_tests.handler import MessageHandler
from aiogram_tests import MockedBot

from aiogram_tests.types.dataset import MESSAGE
from aiogram.filters import Command


logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler())


@pytest.mark.asyncio
async def test_cmd_start():
    requester = MockedBot(request_handler=MessageHandler(cmd_start))
    calls = await requester.query(MESSAGE.as_object(text="/start"))
    answer_message = calls.send_message.fetchone().text
    assert answer_message.split('\n')[0] == 'Welcome to Car Price Prediction Bot!'


@pytest.mark.asyncio
async def test_command_handler():
    requester = MockedBot(MessageHandler(cmd_start, Command(commands=["start"])))
    calls = await requester.query(MESSAGE.as_object(text="/start"))
    answer_message = calls.send_message.fetchone().text
    assert answer_message.split('\n')[0] == 'Welcome to Car Price Prediction Bot!'