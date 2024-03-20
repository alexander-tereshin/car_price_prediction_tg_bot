import pytest
import sys
import os

from unittest import TestCase
from unittest.mock import AsyncMock, MagicMock, patch
from aiogram_tests import MockedBot
from aiogram_tests.handler import MessageHandler
from aiogram_tests.types.dataset import MESSAGE
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from io import BytesIO

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import handlers


class TestMakeRowKeyboard(TestCase):
    def test_make_row_keyboard(self):
        items = ["Button 1", "Button 2", "Button 3"]
        expected_keyboard = ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text=item) for item in items]],
            resize_keyboard=True,
        )
        actual_keyboard = handlers.make_row_keyboard(items)
        self.assertEqual(actual_keyboard.keyboard, expected_keyboard.keyboard)
        self.assertEqual(
            actual_keyboard.resize_keyboard, expected_keyboard.resize_keyboard
        )


@pytest.mark.asyncio
async def test_cmd_start():
    requester = MockedBot(
        MessageHandler(handlers.cmd_start, Command(commands=["start"]))
    )
    calls = await requester.query(MESSAGE.as_object(text="/start"))
    answer_message = calls.send_message.fetchone().text
    assert answer_message.startswith("Welcome to Car Price Prediction Bot!")


@pytest.mark.asyncio
async def test_cmd_help():
    requester = MockedBot(MessageHandler(handlers.cmd_help, Command(commands=["help"])))
    calls = await requester.query(MESSAGE.as_object(text="/help"))
    answer_message = calls.send_message.fetchone().text
    assert answer_message.startswith("🤖 **Car Price Prediction Bot Help**")


@pytest.mark.asyncio
async def test_info():
    started_at = "2022-03-19 12:00:00"

    message_mock = AsyncMock()
    message_mock.text = "info"

    await handlers.info(message=message_mock, started_at=started_at)

    expected_answer_text = (
        "🤖 **Car Price prediction Bot**\n\n"
        "This bot designed for ML model inference as part of the Homework Project "
        "for the Applied Python course in Higher School of Economics\n\n"
        f"🚀 **Bot started at:** {started_at}\n\n"
        "For detailed instructions and to access the source code, check the [GitHub repository]"
        "(https://github.com/alexander-tereshin/car_price_prediction_tg_bot).\n\n"
        "If you have any questions or feedback, feel free to contact the developer @tealandr"
    )

    message_mock.answer.assert_called_with(
        expected_answer_text, parse_mode=ParseMode.MARKDOWN
    )


@pytest.mark.asyncio
async def test_rating():
    async def mock_db_execute(query, fetch):
        if query.startswith("SELECT avg(rating)"):
            return (4.5,)
        elif query.startswith("SELECT count (distinct ts )"):
            return (100,)
        elif query.startswith("SELECT max(ts)"):
            return ("2022-03-19 12:00:00",)

    with patch("handlers.DB.execute", new=mock_db_execute):
        message_mock = AsyncMock()
        await handlers.rating(message=message_mock)
        expected_stats_message = (
            "📊 <b>Statistics</b>\n\n"
            "⭐ <b>Average Rating:</b> 4.5 \n"
            "📈 <b>Number of Reviews:</b> 100 \n"
            "⏰ <b>Last Review:</b> 2022-03-19 12:00:00 \n"
        )
        message_mock.answer.assert_called_once_with(
            expected_stats_message, parse_mode=ParseMode.HTML
        )


@pytest.mark.asyncio
async def test_single_item_prediction():
    requester = MockedBot(MessageHandler(handlers.single_item_prediction))
    calls = await requester.query(MESSAGE.as_object(text="single item prediction"))
    answer_message = calls.send_message.fetchone().text
    assert answer_message.startswith("Choose Brand:\n\n1. Ambassador\n2. Audi\n3. BMW")


@pytest.mark.asyncio
async def test_single_item_prediction_1_incorrect():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_1_incorrect, state=handlers.EntryCar.name
        )
    )
    calls = await requester.query(MESSAGE.as_object())
    answer_message = calls.send_message.fetchone()
    assert answer_message.text.startswith("You have entered incorrect brand number.")


@pytest.mark.asyncio
async def test_single_item_prediction_1_correct():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_1_correct, state=handlers.EntryCar.name
        )
    )
    calls = await requester.query(MESSAGE.as_object(text="1"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text == ("Enter car production year, for example: 2019")


@pytest.mark.asyncio
async def test_single_item_prediction_2_incorrect():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_2_incorrect, state=handlers.EntryCar.year
        )
    )
    calls = await requester.query(MESSAGE.as_object())
    answer_message = calls.send_message.fetchone()
    assert answer_message.text.startswith("Entered year is incorrect.")


@pytest.mark.asyncio
async def test_single_item_prediction_2_correct():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_2_correct, state=handlers.EntryCar.year
        )
    )
    calls = await requester.query(MESSAGE.as_object(text="1950"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text == (
        "Type total number of integer kilometres the car travelled in its life, "
        "for example: 10000"
    )


@pytest.mark.asyncio
async def test_single_item_prediction_3_incorrect():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_3_incorrect,
            state=handlers.EntryCar.km_driven,
        )
    )
    calls = await requester.query(MESSAGE.as_object(text="-1"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text.startswith("Entered km driven is incorrect.")


@pytest.mark.asyncio
async def test_single_item_prediction_3_correct():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_3_correct, state=handlers.EntryCar.km_driven
        )
    )
    calls = await requester.query(MESSAGE.as_object(text="1900"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text == "Choose fuel type from options below:"


@pytest.mark.asyncio
async def test_single_item_prediction_4_correct():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_4_correct, state=handlers.EntryCar.fuel
        )
    )
    calls = await requester.query(MESSAGE.as_object(text="Diesel"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text == "Choose seller type from the options below:"


@pytest.mark.asyncio
async def test_single_item_prediction_5_correct():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_5_correct,
            state=handlers.EntryCar.seller_type,
        )
    )
    calls = await requester.query(MESSAGE.as_object(text="Individual"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text == "Choose transmission type from the options below:"


@pytest.mark.asyncio
async def test_single_item_prediction_6_correct():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_6_correct,
            state=handlers.EntryCar.transmission,
        )
    )
    calls = await requester.query(MESSAGE.as_object(text="Manual"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text == "Choose what ownership counts from the options below:"


@pytest.mark.asyncio
async def test_single_item_prediction_8_correct():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_8_correct, state=handlers.EntryCar.owner
        )
    )
    calls = await requester.query(MESSAGE.as_object(text="First Owner"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text == (
        "Enter mileage (kilometers covered by car in 1 litre of fuel), "
        "for example: 7.9"
    )


@pytest.mark.asyncio
async def test_single_item_prediction_9_correct():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_9_correct, state=handlers.EntryCar.mileage
        )
    )
    calls = await requester.query(MESSAGE.as_object(text="12.1"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text.startswith("Enter engine CC as integer ")


@pytest.mark.asyncio
async def test_single_item_prediction_9_incorrect():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_9_incorrect, state=handlers.EntryCar.mileage
        )
    )
    calls = await requester.query(MESSAGE.as_object(text="121212"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text.startswith("Entered mileage is incorrect.")


@pytest.mark.asyncio
async def test_single_item_prediction_10_correct():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_10_correct, state=handlers.EntryCar.engine
        )
    )
    calls = await requester.query(MESSAGE.as_object(text="1000"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text == "Enter horsepower of an engine, for example: 132.2"


@pytest.mark.asyncio
async def test_single_item_prediction_10_incorrect():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_10_incorrect, state=handlers.EntryCar.engine
        )
    )
    calls = await requester.query(MESSAGE.as_object(text="-1000"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text.startswith("Entered engine CC is incorrect")


@pytest.mark.asyncio
async def test_single_item_prediction_11_correct():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_11_correct,
            state=handlers.EntryCar.max_power,
        )
    )
    calls = await requester.query(MESSAGE.as_object(text="121.1"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text == "Enter seats number, for example: 5"


@pytest.mark.asyncio
async def test_single_item_prediction_11_incorrect():
    requester = MockedBot(
        MessageHandler(
            handlers.single_item_prediction_11_incorrect,
            state=handlers.EntryCar.max_power,
        )
    )
    calls = await requester.query(MESSAGE.as_object(text="-1000"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text.startswith("Entered engine max power is incorrect.")


@pytest.mark.asyncio
async def test_final_correct():
    requester = MockedBot(
        MessageHandler(handlers.final_correct, state=handlers.EntryCar.seats)
    )
    calls = await requester.query(MESSAGE.as_object(text="7"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text.startswith("Consider restart bot using /start command")


@pytest.mark.asyncio
async def test_final_incorrect():
    requester = MockedBot(
        MessageHandler(handlers.final_incorrect, state=handlers.EntryCar.seats)
    )
    calls = await requester.query(MESSAGE.as_object(text="-1000"))
    answer_message = calls.send_message.fetchone()
    assert answer_message.text.startswith("Entered seats number incorrect.")


@pytest.mark.asyncio
async def test_batch_prediction():
    requester = MockedBot(MessageHandler(handlers.batch_prediction))
    calls = await requester.query(MESSAGE.as_object(text="batch prediction"))
    answer_message = calls.send_message.fetchone().text
    assert answer_message.startswith("Please attach .csv file with car entities")


@pytest.mark.asyncio
async def test_my_text_handler():
    requester = MockedBot(MessageHandler(handlers.my_text_handler))
    calls = await requester.query(MESSAGE.as_object(text="awdqwdqwd"))
    answer_message = calls.send_message.fetchone().text
    assert answer_message.startswith("Unknown command or message")


@pytest.mark.asyncio
async def test_help_meassage():
    requester = MockedBot(MessageHandler(handlers.help_message))
    calls = await requester.query(MESSAGE.as_object(text="help"))
    answer_message = calls.send_message.fetchone().text
    assert "Help" in answer_message


class MockPreprocessor:
    @staticmethod
    def preprocess_data(df):
        return df

    @staticmethod
    def ridge_regressor_predict(df):
        return [1, 2, 3]


@pytest.mark.asyncio
async def test_batch_prediction_1():
    bot = AsyncMock()
    message = AsyncMock()
    state = AsyncMock()

    buffer = (
        b"name,year,km_driven,fuel,seller_type,transmission,owner,mileage,engine,max_power,torque,seats\n"
        b"Maruti Swift Dzire VDI,2014,145500,Diesel,Individual,Manual,First Owner,23.4 kmpl,1248 CC,74 bhp,190Nm@ 2000rpm,5.0\n"
        b"Skoda Rapid 1.5 TDI Ambition,2014,120000,Diesel,Individual,Manual,Second Owner,21.14 kmpl,1498 CC,103.52 bhp,250Nm@ 1500-2500rpm,5.0\n"
        b"Hyundai i20 Sportz Diesel,2010,127000,Diesel,Individual,Manual,First Owner,23.0 kmpl,1396 CC,90 bhp,22.4 kgm at 1750-2750rpm,5.0\n"
        b'Maruti Swift VXI BSIII,2007,120000,Petrol,Individual,Manual,First Owner,16.1 kmpl,1298 CC,88.2 bhp,"11.5@ 4,500(kgm@ rpm)",5.0\n'
    )

    bot.download.return_value = BytesIO(buffer)
    mock_preprocessor = MagicMock()
    mock_preprocessor.preprocess_data.return_value = "mock_df"
    mock_preprocessor.ridge_regressor.predict.return_value = [1]

    with patch(
        "preprocessing.CarPricePredictorPreprocessor", return_value=mock_preprocessor
    ):
        await handlers.batch_prediction_1(message, state, bot)

    bot.download.assert_called_once_with(message.document)

    call_args = message.reply_document.call_args
    input_file_object = call_args[0][0]

    assert input_file_object.filename == "result.csv"


class TestBotRating(TestCase):
    def setUp(self):
        self.callback_query = MagicMock()

    @patch("database.DB")
    async def test_send_thanks(self, mock_db):
        self.callback_query.from_user.id = 123
        self.callback_query.data = "5"

        mock_db.execute.side_effect = [
            MagicMock(return_value=None),
            MagicMock(return_value=(("5",),)),
            MagicMock(return_value=("2024-02-20 10:00:00",)),
        ]

        await handlers.send_thanks(self.callback_query)

        mock_db.execute.assert_called_with(
            "INSERT INTO rating VALUES (123, 5, ?)",
            mock_db.execute(),
        )
        self.callback_query.answer.assert_called_with(
            text="Your review is registered ✨\nThanks for using this Bot!",
            show_alert=True,
        )

    @patch("database.DB")
    async def test_send_thanks_already_rated(self, mock_db):
        self.callback_query.from_user.id = 123
        self.callback_query.data = "5"

        mock_db.execute.side_effect = [
            MagicMock(return_value=None),
            MagicMock(return_value=(("5",),)),
            MagicMock(return_value=("2024-02-20 10:00:00",)),
        ]

        await handlers.send_thanks(self.callback_query)

        self.callback_query.answer.assert_called_with(
            text="You have already rated this Bot at 2024-02-20 10:00:00\n\nYour last review was ⭐️⭐️⭐️⭐️⭐️",
            show_alert=True,
        )


if __name__ == "__main__":
    pytest.main()
