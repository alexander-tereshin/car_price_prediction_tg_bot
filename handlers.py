import pathlib
import aiosqlite
import time

import pandas as pd

from datetime import datetime
from typing import Optional
from pydantic import BaseModel

from aiogram import Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.filters.callback_data import CallbackData
from aiogram.enums import ParseMode
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (Message, ReplyKeyboardMarkup,KeyboardButton, ReplyKeyboardRemove,
                           InlineKeyboardMarkup, CallbackQuery, BufferedInputFile)

from preprocessing import CarPricePredictorPreprocessor

models_folder = pathlib.Path('.').resolve() / 'models'
preprocessor = CarPricePredictorPreprocessor(models_folder)



class Item(BaseModel):
    name: str
    year: int
    km_driven: int
    fuel: str
    seller_type: str
    transmission: str
    owner: str
    mileage: str
    engine: str
    max_power: str
    torque: Optional[str] = None
    seats: float

class EntryCar(StatesGroup):
    name = State()
    year = State()
    km_driven = State()
    fuel = State()
    seller_type = State()
    transmission = State()
    owner = State()
    mileage = State()
    engine = State()
    max_power = State()
    torque = State()
    seats = State()
    batch = State()

def predict_price(item: Item) -> float:
    """
    Predict the price for a single item.

    Args:
        item (Item): The input item.

    Returns:
        float: The predicted price.
    """
    processed_df = preprocessor.preprocess_data(pd.DataFrame([item.dict()]))
    return preprocessor.ridge_regressor.predict(processed_df)[0]


def make_row_keyboard(items: list[str]) -> ReplyKeyboardMarkup:
    """
    Создаёт реплай-клавиатуру с кнопками в один ряд
    :param items: список текстов для кнопок
    :return: объект реплай-клавиатуры
    """
    row = [KeyboardButton(text=item) for item in items]
    return ReplyKeyboardMarkup(keyboard=[row], resize_keyboard=True)


router = Router()


available_brands = list(sorted(['Maruti', 'Skoda', 'Hyundai', 'Toyota', 'Ford', 'Renault',
                                'Mahindra', 'Honda', 'Chevrolet', 'Fiat', 'Datsun', 'Tata', 'Jeep',
                                'Mercedes-Benz', 'Mitsubishi', 'Audi', 'Volkswagen', 'BMW',
                                'Nissan', 'Lexus', 'Jaguar', 'Land', 'MG', 'Volvo', 'Daewoo',
                                'Kia', 'Force', 'Ambassador', 'Isuzu', 'Peugeot']))

available_fuels = ['Diesel', 'Petrol', 'LPG', 'CNG']

available_seller_type = ['Individual', 'Dealer', 'Trustmark Dealer']

available_transmission = ['Manual', 'Automatic']

available_owner = ['First Owner', 'Second Owner', 'Third Owner', 'Fourth & Above Owner', 'Test Drive Car']


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.set_data({})
    await state.clear()

    builder = ReplyKeyboardBuilder()
    builder.row(KeyboardButton(text="Single item prediction 🚗"), KeyboardButton(text="Batch prediction 🛻🚚"))
    builder.row(KeyboardButton(text="Rating 📊")),
    builder.row(KeyboardButton(text="Help 🆘"), KeyboardButton(text="Info ℹ️"))

    await message.answer("Welcome to Car Price Prediction Bot!\n\n"
                         "You can control me simply using keys below:",
                         reply_markup=builder.as_markup(resize_keyboard=True))


@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer("🤖 **Car Price Prediction Bot Help**\n\n"
                         "This bot is designed to predict car prices based on various parameters. "
                         "Here are some commands you can use:\n\n"
                         "/start - show welcome message and menu and restart bot\n"
                         "/help - show help message and list of commands\n\n"
                         "You can control me simply using keys below:\n\n"
                         "Single item prediction - Initiate the car price prediction process.\n"
                         "Batch prediction - Initiate the car prices prediction process for batch of objects.\n"
                         "Rating - View statistics including the average rating and usage statistics.\n"
                         "Info - Get information about the bot.\n"
                         "Help - Display this help message.\n\n"
                         "If you have any "
                         "questions or feedback, feel free to contact the developer @tealandr",
                         parse_mode=ParseMode.MARKDOWN)


@router.message(F.text.lower().split()[0] == "info")
async def info(message: Message, started_at: str):
    await message.answer("🤖 **Car Price prediction Bot**\n\n"
                         "This bot designed for ML model inference as part of the Homework Project "
                         "for the Applied Python course in Higher School of Economics\n\n"
                         f"🚀 **Bot started at:** {started_at}\n\n"
                         "For detailed instructions and to access the source code, check the [GitHub repository]"
                         "(https://github.com/alexander-tereshin).\n\n"
                         "If you have any questions or feedback, feel free to contact the developer @tealandr",
                         parse_mode=ParseMode.MARKDOWN)


@router.message(F.text.lower().split()[0] == "help")
async def help(message: Message):
    await message.answer("🤖 **Car Price Prediction Bot Help**\n\n"
                         "This bot is designed to predict car prices based on various parameters. "
                         "Here are some commands you can use:\n\n"
                         "/start - show welcome message and menu and restart bot\n"
                         "/help - show help message and list of commands\n\n"
                         "You can control me simply using keys below:\n\n"
                         "Single item prediction - Initiate the car price prediction process. "
                         "After price prediction, you will be prompted to leave a review\n"
                         "Batch prediction - Initiate the car prices prediction process for batch of objects.\n"
                         "Rating - View statistics including the average rating and usage statistics.\n"
                         "Info - Get information about the bot.\n"
                         "Help - Display this help message.\n\n"
                         "After price prediction, you will be prompted to leave a review\n"
                         "If you have any "
                         "questions or feedback, feel free to contact the developer @tealandr",
                         parse_mode=ParseMode.MARKDOWN)


@router.message(F.text.lower().split()[0] == "rating")
async def rating(message: Message):
    """
    Display statistics including average rating and usage statistics.
    """
    db_path = pathlib.Path('.').resolve() / 'rating.db'
    db = await aiosqlite.connect(db_path)
    cursor = await db.execute(f"SELECT avg(rating) FROM rating")
    average_rating = (await cursor.fetchone())[0]

    cursor = await db.execute(f"SELECT count (distinct ts ) FROM rating")
    number_reviews = (await cursor.fetchone())[0]

    cursor = await db.execute(f"SELECT max(ts) FROM rating")
    max_ts = (await cursor.fetchone())[0]

    await cursor.close()
    await db.close()

    stats_message = (
        f"📊 <b>Statistics</b>\n\n"
        f"⭐ <b>Average Rating:</b> {average_rating} \n"
        f"📈 <b>Number of Reviews:</b> {number_reviews} \n"
        f"⏰ <b>Last Review:</b> {max_ts} \n"
    )
    await message.answer(stats_message, parse_mode=ParseMode.HTML)



#entry point for single item prediction
@router.message(F.text.lower()[:-2] == "single item prediction")
async def single_item_prediction(message: Message, state: FSMContext):
    await message.answer(text="Choose Brand:\n\n" + "\n".join([f"{i + 1}. {j}" for i, j in enumerate(available_brands)]),
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(EntryCar.name)

#handle correct brand
@router.message(EntryCar.name, F.text.in_([str(i+1) for i in range(len(available_brands))]))
async def single_item_prediction_1(message: Message, state: FSMContext):
    index = int(message.text)
    await state.update_data(name=available_brands[index-1])
    await message.answer(text="Enter car production year in format %Y,\n"
                              "e.g. 2019")
    await state.set_state(EntryCar.year)

#handle incorrect brand
@router.message(EntryCar.name)
async def single_item_prediction_1(message: Message, state: FSMContext):
    index = int(message.text)
    await message.answer(text="You have entered incorrect brand number. Please try again.\n\n"
                              "Choose Brand:\n\n" + "\n".join([f"{i + 1}. {j}" for i, j in enumerate(available_brands)]))

#handle correct year
@router.message(EntryCar.year, F.text.regexp(r'^(19|20)\d{2}$'))
async def single_item_prediction_2(message: Message, state: FSMContext):
    await state.update_data(year=message.text)
    await message.answer(text="Type total number of integer kilometres the car travelled in its life,\n"
                              "eg. 10000")
    await state.set_state(EntryCar.km_driven)

#handle incorrect year
@router.message(EntryCar.year)
async def single_item_prediction_2(message: Message, state: FSMContext):
    await state.update_data(year=message.text)
    await message.answer(text="Entered year is incorrect. Please try again and enter year in format %Y\n"
                              "eg. 2019")

#handle correct km driven
@router.message(EntryCar.km_driven, F.text.regexp(r'^\d{1,6}$'))
async def single_item_prediction_3(message: Message, state: FSMContext):
    await state.update_data(km_driven=message.text)
    await message.answer(text="Choose fuel type from options below:",
                         reply_markup=make_row_keyboard(available_fuels))
    await state.set_state(EntryCar.fuel)


#handle incorrect km driven
@router.message(EntryCar.km_driven)
async def single_item_prediction_3(message: Message, state: FSMContext):
    await state.update_data(km_driven=message.text)
    await message.answer(text="Entered km driven is incorrect\n"
                              "Please try again and enter km driven in range from 0 to 999999:")

#handle correct available_fuels
@router.message(EntryCar.fuel, F.text.in_(available_fuels))
async def single_item_prediction_4(message: Message, state: FSMContext):
    await state.update_data(fuel=message.text)
    await message.answer(text="Choose seller type from the options below:",
                         reply_markup=make_row_keyboard(available_seller_type))
    await state.set_state(EntryCar.seller_type)

#handle correct available_seller_type
@router.message(EntryCar.seller_type, F.text.in_(available_seller_type))
async def single_item_prediction_5(message: Message, state: FSMContext):
    await state.update_data(seller_type=message.text)
    await message.answer(text="Choose transmission type from the options below:",
                         reply_markup=make_row_keyboard(available_transmission))
    await state.set_state(EntryCar.transmission)

#handle correct available_transmission
@router.message(EntryCar.transmission, F.text.in_(available_transmission))
async def single_item_prediction_6(message: Message, state: FSMContext):
    await state.update_data(transmission=message.text)
    await message.answer(text="Choose what ownership counts from the options below:",
                         reply_markup=make_row_keyboard(available_owner))
    await state.set_state(EntryCar.owner)

#handle correct available_owner
@router.message(EntryCar.owner, F.text.in_(available_owner))
async def single_item_prediction_8(message: Message, state: FSMContext):
    await state.update_data(owner=message.text)
    await message.answer(text="Enter mileage (kilometers covered by car in 1 litre of fuel,\n"
                              "e.g. 7.9)",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(EntryCar.mileage)


#handle correct mileage
@router.message(EntryCar.mileage, F.text.regexp('^\d{1,2}([,\.]\d{1,5})?$'))
async def single_item_prediction_9(message: Message, state: FSMContext):
    await state.update_data(mileage=message.text)
    await message.answer(text="Enter engine CC as integer")
    await state.set_state(EntryCar.engine)

#handle incorrect mileage
@router.message(EntryCar.mileage)
async def single_item_prediction_9(message: Message, state: FSMContext):
    await state.update_data(mileage=message.text)
    await message.answer(text="Entered mileage is incorrect.\n"
                              "Try again (enter kilometers covered by Car in 1 litre of fuel,\n"
                              "e.g. 7.9)")

#handle correct engine CC
@router.message(EntryCar.engine, F.text.regexp(r'^\d{1,6}$'))
async def single_item_prediction_10(message: Message, state: FSMContext):
    await state.update_data(engine=message.text)
    await message.answer(text="Enter horsepower of an engine,\ne.g. 132.2")
    await state.set_state(EntryCar.max_power)

#handle incorrect engine CC
@router.message(EntryCar.engine)
async def single_item_prediction_10(message: Message, state: FSMContext):
    await state.update_data(engine=message.text)
    await message.answer(text="Entered engine CC is incorrect.\n"
                              "Retype engine CC")

#handle correct engine max_power
@router.message(EntryCar.max_power, F.text.regexp('^\d{1,3}([,\.]\d{1,5})?$'))
async def single_item_prediction_11(message: Message, state: FSMContext):
    await state.update_data(max_power=message.text)
    await message.answer(text="Enter seats number, e.g. 5")
    await state.set_state(EntryCar.seats)

#handle incorrect engine max_power
@router.message(EntryCar.max_power)
async def single_item_prediction_11(message: Message, state: FSMContext):
    await state.update_data(max_power=message.text)
    await message.answer(text="Entered engine max power is incorrect.\n"
                              "Retype engine max power, e.g. 132.2")


#handle correct seats number
@router.message(EntryCar.seats, F.text.in_([str(i) for i in range (1,21)]))
async def final(message: Message, state: FSMContext):
    await state.update_data(seats=message.text)
    await message.answer(text="All data gathered. Please wait for the prediction... ⏳")

    time.sleep(1.5)

    data = await state.get_data()

    await state.set_data({})
    await state.clear()

    try:
        price = round(predict_price(Item(**data)), 2)

        if price < 50000:
            price = 50000

        price_formatted = '{:,}'.format(price).replace(',', ' ')
        await message.answer(text=f"Predicted price is <b>{price_formatted}</b> RUB",
                             parse_mode=ParseMode.HTML)

        builder = InlineKeyboardBuilder()

        for i in range(1,6):
            builder.add(InlineKeyboardButton(text=i * '⭐️',
                                             callback_data=str(i)))
        builder.adjust(3)
        await message.answer("Please, rate this Bot 🌝", reply_markup=builder.as_markup())

    except Exception as e:
        await message.answer(str(e))
        await message.answer('Consider restart bot using /start command')


@router.callback_query(F.data.in_([str(i) for i in range(1,6)]))
async def send_thanks(callback: CallbackQuery):
    try:
        user_id = int(callback.from_user.id)
        rating = int(callback.data)
        time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        db_path = pathlib.Path('.').resolve() / 'rating.db'
        db = await aiosqlite.connect(db_path)

        cursor = await db.execute(f"INSERT INTO rating VALUES ({user_id}, {rating}, '{time}')")

        await db.commit()
        await cursor.close()
        await db.close()

        await callback.answer(
            text="Your review is registered ✨\n"
                 "Thanks for using this Bot!",
            show_alert=True)

    except aiosqlite.Error as e:
        print(e)
        db_path = pathlib.Path('.').resolve() / 'rating.db'
        db = await aiosqlite.connect(db_path)

        cursor = await db.execute(f"SELECT rating FROM rating where client_id = {user_id}")
        last_rating = '⭐️' * int((await cursor.fetchone())[0])

        cursor = await db.execute(f"SELECT ts FROM rating where client_id = {user_id}")
        review_ts = (await cursor.fetchone())[0]

        await cursor.close()
        await db.close()
        await callback.answer(f"You have already rated this Bot at {review_ts}\n\n"
                              f"Your last review was {last_rating}",
                              show_alert=True)

#handle incorrect seats number
@router.message(EntryCar.seats)
async def final(message: Message, state: FSMContext):
    await state.update_data(seats=message.text)
    await message.answer(text="Entered seats number incorrect."
                              "Retype seats number in range from 1 to 20")



#entry point for batch
@router.message(F.text.lower()[:-3] == "batch prediction")
async def batch_prediction(message: Message, state: FSMContext):
    await message.answer(text="Please attach .csv file with car entities",
                         reply_markup=ReplyKeyboardRemove())
    await state.set_state(EntryCar.batch)


@router.message(EntryCar.batch, F.content_type == 'document')
async def batch_prediction_1(message: Message, state: FSMContext, bot: Bot):
    buffer = await bot.download(message.document)
    df = pd.read_csv(buffer)

    processed_df = preprocessor.preprocess_data(df)
    predictions = preprocessor.ridge_regressor.predict(processed_df).tolist()

    result = []
    for _, row in df.iterrows():
        result.append({"input_data": row.to_dict(), "predicted_price": predictions.pop(0)})

    result_df = pd.DataFrame(result)
    result_bytes = bytes(result_df.to_csv(lineterminator='\r\n', index=False), encoding='utf-8')

    await message.reply_document(BufferedInputFile(result_bytes, filename='result.csv'))
    await state.clear()


@router.message(F.text)
async def my_text_handler(message: Message):
    await message.answer("Unkown command or message\n"
                         "Available commands:\n"
                         "/start - show welcome message and menu and restart bot\n"
                         "/help - show help message and list of commands\n\n"
                         "You can control me simply using keys below"
                         )






