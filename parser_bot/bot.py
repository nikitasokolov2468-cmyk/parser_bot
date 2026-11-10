import asyncio
import logging
import sys
from aiogram import Bot, Dispatcher, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from parser import parse_books

# Вставь сюда токен своего бота от BotFather
TOKEN = "9135444465:AAEOJTNC6LgEwr0KJFke0nEdaACuuEUJYg4"

dp = Dispatcher()


@dp.message(CommandStart())
async def command_start(message: Message) -> None:
    await message.answer(
        f"Привет, {html.bold(message.from_user.full_name)}! 🤖\n"
        "Я бот-парсер. Отправь мне команду в формате:\n"
        "<code>/parse https://example.com</code>"
    )


@dp.message(Command("parse"))
async def command_parse(message: Message) -> None:
    status_msg = await message.answer("⏳ Паршу каталог книг с Books to Scrape...")

    books = await parse_books()

    if not books:
        await status_msg.edit_text("❌ Не удалось получить список книг.")
        return

    # Берем первые 5 книг для примера
    response_lines = ["📚 <b>Вот что удалось найти на сайте:</b>\n"]
    for i, book in enumerate(books[:5], 1):
        response_lines.append(
            f"{i}. <b>{book['title']}</b>\n"
            f"💰 Цена: <code>{book['price']}</code>\n"
            f"🔗 <a href='{book['url']}'>Ссылка на книгу</a>\n"
        )

    await status_msg.edit_text("\n".join(response_lines), disable_web_page_preview=True)


@dp.message(Command("parse"))
async def command_parse(message: Message) -> None:
    # Получаем URL из сообщения (например: /parse https://somesite.com)
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer("Пожалуйста, укажи URL после команды. Пример:\n<code>/parse https://example.com</code>")
        return

    url = args[1]
    status_msg = await message.answer("⏳ Собираю данные с сайта...")

    # Запускаем асинхронный парсинг
    data = await parse_data(url)

    if not data:
        await status_msg.edit_text("❌ Не удалось получить данные по этому URL.")
        return

    response_text = (
        f"✅ <b>Результат парсинга:</b>\n\n"
        f"📌 <b>Заголовок:</b> {data['title']}\n"
        f"📊 <b>Статус:</b> {data['value']}\n"
        f"🔗 <b>Источник:</b> {data['url']}"
    )

    await status_msg.edit_text(response_text)


async def main() -> None:
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())

