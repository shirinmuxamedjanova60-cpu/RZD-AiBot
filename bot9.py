import asyncio
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import LabeledPrice, PreCheckoutQuery, InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = "7592755189:AAG3PHzCSW4iun-_AzynrQFtVuZWS8acZOQ"
ADMIN_ID = 6444684762
ADMIN_USER = "@Ezzzzzoochka"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class Order(StatesGroup):
    waiting_for_target = State()

def main_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💀 [ DOX / OSINT ]", callback_data="dox")],
        [InlineKeyboardButton(text="☣️ [ DOX+ / FULL ]", callback_data="dox_plus")],
        [InlineKeyboardButton(text="🛡️ [ DEF-GUARD / 10 ДНЕЙ ]", callback_data="def")],
        [InlineKeyboardButton(text="👨‍💻 АДМИН", url=f"https://t.me/{ADMIN_USER[1:]}")]
    ])

@dp.message(Command("start"))
async def start(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("СИСТЕМА ЗАПУЩЕНА.\n————————————————\nВыбирай вектор атаки или защиты:", reply_markup=main_kb(), parse_mode="Markdown")

@dp.callback_query(F.data.in_(["dox", "dox_plus"]))
async def dox_init(call: types.CallbackQuery, state: FSMContext):
    mode = "FULL" if call.data == "dox_plus" else "BASE"
    await state.update_data(mode=call.data)
    await call.message.edit_text(f"РЕЖИМ: {mode}\nВведи данные цели (юзер/номер/ссылка):")
    await state.set_state(Order.waiting_for_target)

@dp.message(Order.waiting_for_target)
async def get_target(message: types.Message, state: FSMContext):
    user_data = await state.get_data()
    mode = user_data.get("mode")
    await state.update_data(target=message.text)
    
    if mode == "dox_plus":
        info_text = (
            f"🎯 ЦЕЛЬ ПРИНЯТА (DOX+): {message.text}\n\n"
            "ЧТО ВХОДИТ В FULL ПАКЕТ:\n"
            "• История сообщений в открытых чатах\n"
            "• Список групп и каналов цели\n"
            "• Круг общения: выявление близких контактов\n"
            "• Анализ речи: частота слов и триггеры\n"
            "• Местоположение / Адрес (если есть в базах)\n"
            "• Данные матери / Родственников (при наличии)\n"
            "• Паспортные данные (если имеются)\n\n"
            "ЦЕНА: 50 STARS ⭐️"
        )
        price, callback_pay = 50, "pay_dox_plus"
    else:
        info_text = (
            f"🎯 ЦЕЛЬ ПРИНЯТА (BASE): {message.text}\n\n"
            "ЧТО ВХОДИТ В ПАКЕТ:\n"
            "• Адрес проживания (при наличии в базах)\n"
            "• Данные матери (если будут найдены)\n"
            "• Паспортные данные (если есть в реестрах)\n"
            "• Номера телефонов, почты, соцсети\n"
            "• Слив информации в профильные чаты\n\n"
            "ЦЕНА: 15 STARS ⭐️"
        )
        price, callback_pay = 15, "pay_dox"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f"💳 ОПЛАТИТЬ {price} ⭐️", callback_data=callback_pay)],
        [InlineKeyboardButton(text="🔙 ОТМЕНА", callback_data="back")]
    ])
    await message.answer(info_text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data == "def")
async def def_info(call: types.CallbackQuery):
    info_text = (
        "🛡️ ОПЕРАЦИЯ: DEF-GUARD\n"
        "СРОК ДЕЙСТВИЯ: 10 ДНЕЙ\n\n"
        "ЧТО ВХОДИТ В ЗАЩИТУ:\n"
        "• Круглосуточный мониторинг угроз\n"
        "• Блокировка попыток сваттинга и докса\n"
        "• Зачистка данных из публичных баз\n"
        "• Иммунитет к сносу аккаунта\n\n"
        "ЦЕНА: 15 STARS ⭐️"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 КУПИТЬ НА 10 ДНЕЙ - 15 ⭐️", callback_data="pay_def")],
        [InlineKeyboardButton(text="🔙 НАЗАД", callback_data="back")]
    ])
    await call.message.edit_text(info_text, reply_markup=kb, parse_mode="Markdown")

@dp.callback_query(F.data.startswith("pay_"))
async def send_invoice(call: types.CallbackQuery):
    if "dox_plus" in call.data:
        label, amount = "DOX+ FULL", 50
    elif "dox" in call.data:
        label, amount = "DOX BASE", 15
    else:
        label, amount = "DEF GUARD (10 ДНЕЙ)", 15

    await bot.send_invoice(
        chat_id=call.from_user.id,
        title=label,
        description=f"Активация модуля {label}",
        payload=call.data,
        currency="XTR",
        prices=[LabeledPrice(label=label, amount=amount)],
        provider_token=""
    )
    await call.answer()

@dp.callback_query(F.data == "back")
async def back(call: types.CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.edit_text("СИСТЕМА ЗАПУЩЕНА.\n————————————————\nВыбирай вектор атаки или защиты:", reply_markup=main_kb(), parse_mode="Markdown")
    await call.answer()

@dp.pre_checkout_query()
async def pre_checkout(query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(query.id, ok=True)

@dp.message(F.successful_payment)
async def success(message: types.Message, state: FSMContext):
    data = await state.get_data()
    target = data.get("target", "Защита (10 дней)")
    payload = message.successful_payment.invoice_payload
    
    await message.answer(f"✅ ОПЛАЧЕНО.\n\nВ работе. Срочно отпиши админу: {ADMIN_USER}", parse_mode="Markdown")
    
    user = message.from_user
    service = "☣️ DOX+" if "plus" in payload else ("📂 ДОКС" if "dox" in payload else "🛡️ ЗАЩИТА (10 ДНЕЙ)")
    
    report = (
        "💰 ФИКСИРУЮ ПРИБЫЛЬ!\n"
        "————————————————\n"
        f"👤 КЛИЕНТ: @{user.username if user.username else 'NoUser'}\n"
        f"🎯 ЦЕЛЬ: {target}\n"
        f"📦 УСЛУГА: {service}\n"
        "————————————————"
    )
    await bot.send_message(ADMIN_ID, report, parse_mode="Markdown")
    await state.clear()

async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
