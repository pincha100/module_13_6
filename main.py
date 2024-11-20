from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils import executor
from aiogram.dispatcher.filters import Text


API_TOKEN = ''
bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)


# Определяем группу состояний для цепочки "Calories"
class UserState(StatesGroup):
    age = State()
    growth = State()
    weight = State()


# Обычная клавиатура
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
button_calculate = KeyboardButton("Рассчитать")
button_info = KeyboardButton("Информация")
keyboard.add(button_calculate, button_info)

# Inline-клавиатура
inline_keyboard = InlineKeyboardMarkup()
button_calories = InlineKeyboardButton("Рассчитать норму калорий", callback_data="calories")
button_formulas = InlineKeyboardButton("Формулы расчёта", callback_data="formulas")
inline_keyboard.add(button_calories, button_formulas)


# Обработчик команды /start
@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Привет! Я бот, помогающий рассчитывать норму калорий. Выберите действие:",
                         reply_markup=keyboard)


# Обработчик кнопки "Рассчитать" для вызова Inline-клавиатуры
@dp.message_handler(Text(equals="Рассчитать", ignore_case=True))
async def main_menu(message: types.Message):
    await message.answer("Выберите опцию:", reply_markup=inline_keyboard)


# Обработчик кнопки "Формулы расчёта"
@dp.callback_query_handler(lambda call: call.data == "formulas")
async def get_formulas(call: types.CallbackQuery):
    formula = (
        "Формула Миффлина-Сан Жеора:\n"
        "Для мужчин: 10 × вес (кг) + 6.25 × рост (см) - 5 × возраст (лет) + 5\n"
        "Для женщин: 10 × вес (кг) + 6.25 × рост (см) - 5 × возраст (лет) - 161"
    )
    await call.message.answer(formula)


# Обработчик кнопки "Рассчитать норму калорий"
@dp.callback_query_handler(lambda call: call.data == "calories")
async def set_age(call: types.CallbackQuery):
    await call.message.answer("Введите свой возраст:")
    await UserState.age.set()


# Обработка возраста и переход к росту
@dp.message_handler(state=UserState.age)
async def set_growth(message: types.Message, state: FSMContext):
    await state.update_data(age=int(message.text))  # Сохраняем возраст
    await message.answer("Введите свой рост (в сантиметрах):")
    await UserState.growth.set()


# Обработка роста и переход к весу
@dp.message_handler(state=UserState.growth)
async def set_weight(message: types.Message, state: FSMContext):
    await state.update_data(growth=int(message.text))  # Сохраняем рост
    await message.answer("Введите свой вес (в килограммах):")
    await UserState.weight.set()


# Обработка веса и подсчёт нормы калорий
@dp.message_handler(state=UserState.weight)
async def send_calories(message: types.Message, state: FSMContext):
    await state.update_data(weight=int(message.text))  # Сохраняем вес

    # Получаем все данные пользователя
    data = await state.get_data()
    age = data["age"]
    growth = data["growth"]
    weight = data["weight"]

    # Формула Миффлина-Сан Жеора для мужчин:
    calories = 10 * weight + 6.25 * growth - 5 * age + 5

    # Для женщин можно использовать: calories = 10 * weight + 6.25 * growth - 5 * age - 161

    # Отправляем результат пользователю
    await message.answer(f"Ваша норма калорий: {calories:.2f} ккал в день.")

    # Завершаем машину состояний
    await state.finish()


# Обработчик кнопки "Информация"
@dp.message_handler(Text(equals="Информация", ignore_case=True))
async def send_info(message: types.Message):
    await message.answer("Я бот для расчёта нормы калорий. Нажмите 'Рассчитать', чтобы начать!")


# Обработчик всех прочих сообщений
@dp.message_handler()
async def all_messages(message: types.Message):
    await message.answer("Введите команду /start, чтобы начать общение.")


# Запуск бота
if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
