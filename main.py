import asyncio, logging, os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv
from config import URL_PATTERN
from handlers import download_video, get_formats_with_keyboard
from middlewares import check_authorization

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s | %(levelname)-8s | %(message)s',
  datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.message.middleware(check_authorization)

@dp.message(Command("start"))
async def cmd_start(message: Message):
  await message.answer(
    "🎬 Bienvenido a SaronzTube\n"
    "Envíame una URL de video para descargar."
  )

@dp.message(Command("help"))
async def cmd_help(message: Message):
  await message.answer(
    "📖 Ayuda\n\n"
    "/start - Iniciar el bot\n"
    "/help - Mostrar ayuda\n\n"
    "Envía una URL de video para descargarlo."
  )

@dp.message(Command("test"))
async def cmd_test(message: Message):
    btn_1 = InlineKeyboardButton(text="Saludar", callback_data="saludar")
    btn_2 = InlineKeyboardButton(text="Despedirse", callback_data="despedirse")
    btns = [[btn_1, btn_2]]
    markup = InlineKeyboardMarkup(inline_keyboard=btns)
    await message.answer("Elige uno", reply_markup=markup)

@dp.callback_query(F.data.in_(["saludar", "despedirse"]))
async def handler_callback(callback: CallbackQuery):
    await callback.answer()
    
    if callback.data == "saludar":
        await callback.message.answer("¡Hola!")
    elif callback.data == "despedirse":
        await callback.message.answer("¡Adiós!")
    
    # Opción 1: Eliminar el mensaje completamente
    # await callback.message.delete()
    
    # Opción 2: Editar el mensaje y quitar botones (comenta la línea de arriba)
    await callback.message.edit_text("✅ Seleccionado", reply_markup=None)

@dp.message(F.text)
async def handle_url(message: Message):
  url = message.text
  if not URL_PATTERN.search(url):
    return
  
  try:
    # Mostrar formatos con botones
    keyboard = get_formats_with_keyboard(url)
    await message.answer("📋 Selecciona el formato:", reply_markup=keyboard)
    
    # # Descargar
    # await message.answer("⏳ Descargando...")
    # file = download_video(url)
    
    # # Enviar video
    # video = FSInputFile(file)
    # await message.answer_video(video)
    # os.remove(file)
    
  except Exception as e:
    logger.error(f"Error: {e}")
    await message.answer(f"❌ Error: {str(e)}")

async def main():
  logger.info("Bot iniciado")
  await dp.start_polling(bot)

if __name__ == "__main__":
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    logger.info("Bot detenido")
