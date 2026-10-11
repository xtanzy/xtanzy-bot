import os
import json
import logging
import asyncio
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Загружаем токен из .env
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# Загружаем базу треков
with open("music.json", "r", encoding="utf-8") as f:
    MUSIC = json.load(f)

bot = Bot(token=TOKEN)
dp = Dispatcher()


def main_menu():
    kb = [
        [InlineKeyboardButton(text="🔍 Поиск по названию", callback_data="search")],
        [InlineKeyboardButton(text="📀 Вся дискография", callback_data="discography")],
        [InlineKeyboardButton(text="📅 По годам", callback_data="years")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=kb)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "Привет! Я бот-каталог моей музыки 🎵\n\nЧто будем искать?",
        reply_markup=main_menu()
    )


@dp.callback_query(F.data == "discography")
async def show_all(callback: types.CallbackQuery):
    if not MUSIC:
        await callback.message.answer("Пока треков нет 🎧")
    else:
        text = "📀 <b>Вся дискография:</b>\n\n"
        for song in MUSIC:
            text += f"• {song['title']} ({song['year']})\n"
        await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data == "years")
async def show_years(callback: types.CallbackQuery):
    if not MUSIC:
        await callback.message.answer("Пока треков нет 🎧")
    else:
        years = sorted({song["year"] for song in MUSIC}, reverse=True)
        text = "📅 <b>Треки по годам:</b>\n\n"
        for year in years:
            count = sum(1 for s in MUSIC if s["year"] == year)
            text += f"• {year} — {count} треков\n"
        await callback.message.answer(text, parse_mode="HTML")
    await callback.answer()


@dp.callback_query(F.data == "search")
async def ask_search(callback: types.CallbackQuery):
    await callback.message.answer("Напиши название трека 👇")
    await callback.answer()


@dp.message(F.text)
async def search_song(message: types.Message):
    query = message.text.lower()
    results = [s for s in MUSIC if query in s["title"].lower()]
    if not results:
        await message.answer("Ничего не нашёл 🤷‍♂️ Попробуй другое название.")
        return
    for song in results[:5]:
        await message.answer(f"🎵 {song['title']} ({song['year']})")


async def main():
    logging.basicConfig(level=logging.INFO)
    print("Бот запущен ✅")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
