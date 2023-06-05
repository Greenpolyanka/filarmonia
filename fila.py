import logging
import asyncpg
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import psycopg2
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from psycopg2 import extensions

host = '10.40.240.85'
port = '5432'
user = 'student'
password = 'student-rtf-123'
database = 'fila'

TOKEN = '6055998098:AAEIhwECL5vI_PZBLvszTJh6tSMEUX2O3bA'
bot = Bot(token=TOKEN)

logging.basicConfig(level=logging.INFO)

dp = Dispatcher(bot, storage=MemoryStorage())

role_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
role_keyboard.add(KeyboardButton('Расписание мероприятий'))
role_keyboard.add(KeyboardButton('Внести себя в списки артистов'))
role_keyboard.add(KeyboardButton('Информация о призерах конкурсов'))
role_keyboard.add(KeyboardButton('Узнать информацию о залах'))
role_keyboard.add(KeyboardButton('Узнать свой id'))
role_keyboard.add(KeyboardButton('Деятельность артистов'))

######запуск бота######

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply('Привет, я бот филармонии. Что бы вы хотели сделать:', reply_markup=role_keyboard)


#########мероприятия###########


async def send_message_with_limit(chat_id, message_text):
    if len(message_text) <= 4096:
        await bot.send_message(chat_id, message_text)
    else:
        parts = [message_text[i:i + 4096] for i in range(0, len(message_text), 4096)]
        for part in parts:
            await bot.send_message(chat_id, part)


@dp.message_handler(lambda message: message.text == 'Расписание мероприятий')
async def handler_chose_mero(message: types.Message, state: FSMContext):
    await message.reply("Для начала список:", reply_markup=role_keyboard)
    conn = psycopg2.connect(database='fila', user='student', password='student-rtf-123',
                            host='10.40.240.85', port='5432')
    cursor = conn.cursor()
    try:
        cursor.execute('select * from fila.mero_view')
        rows = cursor.fetchall()

        response = 'Мероприятия и их расписание:\n\n'
        for row in rows:
            mero_str = f"Название: {row[0]}\nДата: {row[1]}\nТип: {row[2]}\nЗал: {row[3]}\n\n"
            response += mero_str

        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о мероприятиях.")

    cursor.close()
    conn.close()


####информация о призерах####


async def send_message_with_limit(chat_id, message_text):
    if len(message_text) <= 4096:
        await bot.send_message(chat_id, message_text)
    else:
        parts = [message_text[i:i + 4096] for i in range(0, len(message_text), 4096)]
        for part in parts:
            await bot.send_message(chat_id, part)


@dp.message_handler(lambda message: message.text == 'Информация о призерах конкурсов')
async def handler_chose_mero(message: types.Message, state: FSMContext):
    conn = psycopg2.connect(database='fila', user='student', password='student-rtf-123',
                            host='10.40.240.85', port='5432')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM fila.призеры_конкурсов')
        rows = cursor.fetchall()

        response = 'Конкурсы и их призеры:\n\n'
        for row in rows:
            priz_str = f"Конкурс: {row[1]}\nДата: {row[2]}\nАртист: {row[0]}\nМесто: {row[3]}\n\n"
            response += priz_str

        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о мероприятиях.")

    cursor.close()
    conn.close()


###########залы############


async def send_message_with_limit(chat_id, message_text):
    if len(message_text) <= 4096:
        await bot.send_message(chat_id, message_text)
    else:
        parts = [message_text[i:i + 4096] for i in range(0, len(message_text), 4096)]
        for part in parts:
            await bot.send_message(chat_id, part)


@dp.message_handler(lambda message: message.text == 'Узнать информацию о залах')
async def handler_chose_zal(message: types.Message, state: FSMContext):
    conn = psycopg2.connect(database='fila', user='student', password='student-rtf-123',
                            host='10.40.240.85', port='5432')
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT * FROM fila.залы')
        rows = cursor.fetchall()

        response = 'Дополнительная информация о залах:\n\n'
        for row in rows:
            zal_str = f"Название зала: {row[1]}\nВместимость: {row[2]}\nХарактеристики: {row[3]}\n\n"
            response += zal_str

        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о мероприятиях.")

    cursor.close()
    conn.close()


##добавление артиста##


async def send_message_with_limit(chat_id, message_text):
    if len(message_text) <= 4096:
        await bot.send_message(chat_id, message_text)
    else:
        parts = [message_text[i:i+4096] for i in range(0, len(message_text), 4096)]
        for part in parts:
            await bot.send_message(chat_id, part)

@dp.message_handler(lambda message: message.text == "Внести себя в списки артистов")
async def handle_add_artist(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await add_artist(message, chat_id, state)


async def add_artist(message: types.Message, chat_id: int, state: FSMContext):
    await bot.send_message(chat_id, "Введите свой ID:")
    await AddArtistState.NUMBER.set()
    await state.update_data(chat_id=chat_id)


class AddArtistState(StatesGroup):
    NUMBER = State()
    NAME = State()
    PHAM = State()
    PHONE = State()


@dp.message_handler(state=AddArtistState.NUMBER)
async def handle_artist_number(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_номер = message.text
    await state.update_data(p_номер=p_номер)
    await bot.send_message(chat_id, "Введите своё имя:")
    await AddArtistState.NAME.set()


@dp.message_handler(state=AddArtistState.NAME)
async def handle_artist_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_имя = message.text
    await state.update_data(p_имя=p_имя)
    await bot.send_message(chat_id, "Введите свою фамилию:")
    await AddArtistState.PHAM.set()


@dp.message_handler(state=AddArtistState.PHAM)
async def handle_artist_pham(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_фамилия = message.text
    await state.update_data(p_фамилия=p_фамилия)
    await bot.send_message(chat_id, "Введите свой номер телефона (вида 8-000-000-00-00):")
    await AddArtistState.PHONE.set()


@dp.message_handler(state=AddArtistState.PHONE)
async def handle_artist_phone(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    p_телефон = message.text
    await state.update_data(p_телефон=p_телефон)

    data = await state.get_data()

    p_номер = data.get('p_номер')
    p_имя = data.get('p_имя')
    p_фамилия = data.get('p_фамилия')
    p_телефон = data.get('p_телефон')

    try:
        conn = psycopg2.connect(database='fila', user='student', password='student-rtf-123',
                                host='10.40.240.85', port='5432')

        cursor = conn.cursor()

        cursor.execute('CALL fila.bot_добавление_артиста(%s, %s, %s, %s)',
                       (p_номер, p_имя, p_фамилия, p_телефон))
        conn.commit()

        cursor.close()
        conn.close()

        await bot.send_message(chat_id, "Артист успешно добавлен")

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при регистрации, попробуйте ещё раз.")

    # Сброс состояния
    await state.finish()



###############информация об артисте###############

@dp.message_handler(lambda message: message.text == "Узнать свой id")
async def handle_get_artist_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Введите свою фамилию:")
    await GetArtistIdState.FIRST_NAME.set()
    await state.update_data(chat_id=chat_id)


class GetArtistIdState(StatesGroup):
    FIRST_NAME = State()
    LAST_NAME = State()


@dp.message_handler(state=GetArtistIdState.FIRST_NAME)
async def handle_get_artist_id_first_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    first_name = message.text
    await state.update_data(first_name=first_name)
    await bot.send_message(chat_id, "Введите имя:")
    await GetArtistIdState.LAST_NAME.set()


@dp.message_handler(state=GetArtistIdState.LAST_NAME)
async def handle_get_artist_id_last_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    last_name = message.text
    await state.update_data(last_name=last_name)

    data = await state.get_data()

    last_name = data.get('first_name')
    first_name = data.get('last_name')

    try:
        conn = psycopg2.connect(database='fila', user='student', password='student-rtf-123',
                                host='10.40.240.85', port='5432')

        cursor = conn.cursor()

        cursor.execute('SELECT id_артиста FROM fila.артисты WHERE имя_артиста = %s AND фамилия_артиста = %s',
                       (first_name, last_name))
        result = cursor.fetchone()

        if result:
            id_артиста = result[0]
            await bot.send_message(chat_id, f"Ваш ID артиста: {id_артиста}")
        else:
            await bot.send_message(chat_id, "Артист не найден.")

        cursor.close()
        conn.close()

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await bot.send_message(chat_id, "Произошла ошибка при получении ID артиста.")

    await state.finish()


###############информация о жанре артиста###############

@dp.message_handler(lambda message: message.text == "Деятельность артистов")
async def handle_do_artist_id(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    await bot.send_message(chat_id, "Введите фамилию интересующего артиста:")
    await GetArtistDoState.LAST_NAME.set()
    await state.update_data(chat_id=chat_id)


class GetArtistDoState(StatesGroup):
    LAST_NAME = State()
    FIRST_NAME = State()


@dp.message_handler(state=GetArtistDoState.LAST_NAME)
async def handle_do_artist_id_last_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    last_name = message.text
    await state.update_data(last_name=last_name)
    await bot.send_message(chat_id, "Введите его имя:")
    await GetArtistDoState.FIRST_NAME.set()


@dp.message_handler(state=GetArtistDoState.FIRST_NAME)
async def handle_do_artist_id_first_name(message: types.Message, state: FSMContext):
    chat_id = message.chat.id
    first_name = message.text
    await state.update_data(first_name=first_name)

    data = await state.get_data()

    first_name = data.get('first_name')
    last_name = data.get('last_name')

    conn = psycopg2.connect(database='fila', user='student', password='student-rtf-123',
                            host='10.40.240.85', port='5432')
    cursor = conn.cursor()

    try:

        cursor.execute('select * from fila.жанр_view where имя_артиста = %s and фамилия_артиста = %s',
                       (first_name, last_name))
        rows = cursor.fetchall()
        ##result = cursor.fetchone()

        response = 'Жанры артиста:\n\n'
        for row in rows:
            жанр_str = f"{row[0]}\n\n"
            response += жанр_str


        await send_message_with_limit(message.chat.id, response)

    except psycopg2.Error as e:
        print("Ошибка при выполнении запроса:", e)
        await message.answer("Произошла ошибка при получении информации о жанрах артиста.")

        cursor.close()
        conn.close()


    await state.finish()


if __name__ == '__main__':
    logging.info("Бот запущен!")
    executor.start_polling(dp)