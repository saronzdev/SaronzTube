import asyncio, logging, os
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from dotenv import load_dotenv
from config import URL_PATTERN
from handlers import download_video, get_formats_buttons
from middlewares import check_authorization

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(
  level=logging.INFO,
  format='%(asctime)s | %(levelname)-8s | %(message)s',
  datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Silenciar warnings de yt-dlp
logging.getLogger('yt_dlp').setLevel(logging.ERROR)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Diccionario para guardar URLs temporalmente {chat_id: url}
user_urls = {}

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

    await callback.message.edit_text("✅ Seleccionado", reply_markup=None)

@dp.message(F.text)
async def handle_url(message: Message):
  url = message.text
  if not URL_PATTERN.search(url):
    return
  
  try:
    # Guardar URL para este usuario
    user_urls[message.chat.id] = url
    
    buttons = get_formats_buttons(url)
    rows = []
    cancel_btn = buttons[-1] 
    format_btns = buttons[:-1]
    
    for i in range(0, len(format_btns), 2):
      rows.append(format_btns[i:i+2])
    
    rows.append([cancel_btn])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=rows)
    await message.answer("📋 Selecciona el formato:", reply_markup=keyboard)
    
  except Exception as e:
    logger.error(f"Error: {e}")
    await message.answer(f"❌ Error: {str(e)}")

@dp.callback_query(F.data.startswith("fmt:"))
async def handle_format_selection(callback: CallbackQuery):
  
  format_id = callback.data.split(":")[1]

  if format_id == "cancel":
    await callback.message.edit_text("❌ Descarga cancelada.", reply_markup=None)
    user_urls.pop(callback.message.chat.id, None)
    return

  url = user_urls.get(callback.message.chat.id)
  if not url:
    await callback.message.edit_text("❌ Error: URL no encontrada. Envía el link nuevamente.", reply_markup=None)
    return

  await callback.message.edit_text(f"⏳ Descargando...", reply_markup=None)
  
  try:
    file = download_video(url)
    video = FSInputFile(file)
    await callback.message.answer_video(video)
    os.remove(file)
    await callback.message.edit_text("✅ Descarga completada.", reply_markup=None)
    user_urls.pop(callback.message.chat.id, None)
    
  except Exception as e:
    logger.error(f"Error descargando: {e}")
    await callback.message.answer(f"❌ Error: {str(e)}")

async def main():
  logger.info("Bot iniciado correctamente")
  try:
    await dp.start_polling(bot)
  except Exception as e:
    logger.error(f"Error en polling: {e}")
    raise

if __name__ == "__main__":
  try:
    asyncio.run(main())
  except KeyboardInterrupt:
    logger.info("Bot detenido")
