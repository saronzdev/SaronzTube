"""
Ejemplos de cómo usar menús inline con botones en Aiogram 3.x
y cómo manejar la selección para descargar formatos específicos con yt-dlp
"""

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
import yt_dlp

# ============================================================================
# PARTE 1: CREAR MENÚ INLINE CON BOTONES
# ============================================================================

async def show_format_menu(message: Message):
  """
  Muestra un menú con botones inline para seleccionar formato.
  
  Los botones inline son botones que aparecen DENTRO del mensaje
  y cuando el usuario presiona uno, envían un "callback" al bot
  sin escribir nada en el chat.
  """
  
  # Crear el teclado inline
  # InlineKeyboardMarkup es el contenedor
  # InlineKeyboardButton es cada botón individual
  keyboard = InlineKeyboardMarkup(inline_keyboard=[
    # Cada lista es una fila de botones
    [
      # text: lo que ve el usuario
      # callback_data: dato que se envía cuando presionan el botón
      InlineKeyboardButton(text="🎵 Audio 128k", callback_data="format:audio_128k"),
      InlineKeyboardButton(text="🎵 Audio 320k", callback_data="format:audio_320k")
    ],
    [
      InlineKeyboardButton(text="📹 360p", callback_data="format:video_360p"),
      InlineKeyboardButton(text="📹 720p", callback_data="format:video_720p")
    ],
    [
      InlineKeyboardButton(text="📹 1080p", callback_data="format:video_1080p")
    ],
    [
      InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel")
    ]
  ])
  
  # Enviar mensaje con el teclado
  await message.answer(
    "Selecciona el formato que deseas descargar:",
    reply_markup=keyboard  # ← Aquí va el teclado inline
  )


# ============================================================================
# PARTE 2: GENERAR BOTONES DINÁMICAMENTE DESDE FORMATOS DE YT-DLP
# ============================================================================

def generate_format_keyboard(formats: list) -> InlineKeyboardMarkup:
  """
  Genera un teclado inline dinámicamente desde una lista de formatos.
  
  Args:
    formats: Lista de diccionarios con info de formatos de yt-dlp
    
  Returns:
    InlineKeyboardMarkup con botones para cada formato
  """
  buttons = []
  
  # Crear botones a partir de los formatos
  for f in formats[:10]:  # Limitar a 10 formatos para no saturar
    format_id = f.get('format_id')  # ← IMPORTANTE: Este es el ID que usa yt-dlp
    height = f.get('height')
    ext = f.get('ext')
    is_audio = f.get('vcodec') == 'none'
    
    # Crear el texto del botón
    if is_audio:
      abr = f.get('abr', 0)
      text = f"🎵 Audio {int(abr)}k ({ext})"
    else:
      text = f"📹 {height}p ({ext})"
    
    # Crear el botón con el format_id en callback_data
    # Usamos formato "fmt:ID" para poder extraerlo después
    button = InlineKeyboardButton(
      text=text,
      callback_data=f"fmt:{format_id}"  # ← Guardamos el format_id aquí
    )
    
    # Agregar botón en su propia fila
    buttons.append([button])
  
  # Agregar botón de cancelar al final
  buttons.append([
    InlineKeyboardButton(text="❌ Cancelar", callback_data="cancel")
  ])
  
  return InlineKeyboardMarkup(inline_keyboard=buttons)


# Ejemplo de uso:
async def handle_url_with_menu(message: Message):
  """Cuando el usuario envía una URL, mostrar menú de formatos"""
  url = message.text
  
  # Obtener formatos con yt-dlp
  with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
    info = ydl.extract_info(url, download=False)
    formats = info.get('formats', [])
  
  # Generar teclado con los formatos
  keyboard = generate_format_keyboard(formats)
  
  # Mostrar menú
  await message.answer(
    "📋 Selecciona el formato que deseas descargar:",
    reply_markup=keyboard
  )


# ============================================================================
# PARTE 3: MANEJAR LA SELECCIÓN DEL USUARIO (CALLBACK HANDLER)
# ============================================================================

# Registrar el handler para callbacks que empiecen con "fmt:"
# @dp.callback_query(F.data.startswith("fmt:"))
async def handle_format_selection(callback: CallbackQuery):
  """
  Se ejecuta cuando el usuario presiona un botón del menú inline.
  
  callback.data contiene el string que pusimos en callback_data
  callback.message es el mensaje donde están los botones
  """
  
  # Extraer el format_id del callback_data
  # Si callback_data = "fmt:137", entonces format_id = "137"
  format_id = callback.data.split(":")[1]
  
  # Responder al callback (hace que el botón deje de mostrar "cargando...")
  await callback.answer(f"Descargando formato {format_id}...")
  
  # Editar el mensaje original para mostrar que está descargando
  await callback.message.edit_text(
    f"⏳ Descargando formato {format_id}...",
    reply_markup=None  # ← Elimina los botones
  )
  
  # Aquí viene la descarga...
  # (ver PARTE 4)


# ============================================================================
# PARTE 4: DESCARGAR CON YT-DLP USANDO EL FORMAT_ID
# ============================================================================

def download_with_format(url: str, format_id: str) -> str:
  """
  Descarga un video con un format_id específico.
  
  Args:
    url: URL del video
    format_id: ID del formato (ej: "137", "140", "18")
    
  Returns:
    Nombre del archivo descargado
  """
  
  # Configurar yt-dlp con el format_id específico
  ydl_opts = {
    'format': format_id,  # ← AQUÍ especificamos el formato exacto
    'outtmpl': '%(title)s.%(ext)s',
    'quiet': True
  }
  
  # Descargar
  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    info = ydl.extract_info(url, download=True)
    filename = ydl.prepare_filename(info)
    return filename


# Ejemplo completo del callback handler con descarga:
async def handle_format_selection_complete(callback: CallbackQuery):
  """Handler completo con descarga"""
  
  # 1. Extraer format_id
  format_id = callback.data.split(":")[1]
  
  # 2. Responder al callback
  await callback.answer("Descargando...")
  
  # 3. Editar mensaje
  await callback.message.edit_text(
    f"⏳ Descargando...",
    reply_markup=None
  )
  
  # 4. Obtener la URL original (necesitas guardarla antes)
  # Puedes guardarla en una variable global, base de datos, o en el callback_data
  # Por ejemplo: callback_data = "fmt:137:url_youtube.com/watch?v=..."
  url = "https://..."  # ← Aquí deberías obtener la URL guardada
  
  # 5. Descargar con el formato seleccionado
  try:
    filename = download_with_format(url, format_id)
    
    # 6. Enviar el archivo al usuario
    await callback.message.answer(f"✅ Descarga completada: {filename}")
    # Aquí enviarías el archivo...
    
  except Exception as e:
    await callback.message.answer(f"❌ Error: {str(e)}")


# ============================================================================
# PARTE 5: GUARDAR LA URL EN EL CALLBACK_DATA (AVANZADO)
# ============================================================================

def generate_format_keyboard_with_url(formats: list, url: str) -> InlineKeyboardMarkup:
  """
  Versión avanzada: guarda la URL en cada botón.
  
  PROBLEMA: callback_data tiene límite de 64 caracteres
  SOLUCIÓN: Usar un ID corto o hash en lugar de la URL completa
  """
  buttons = []
  
  for f in formats[:10]:
    format_id = f.get('format_id')
    height = f.get('height')
    is_audio = f.get('vcodec') == 'none'
    
    text = f"🎵 Audio" if is_audio else f"📹 {height}p"
    
    # OPCIÓN 1: Incluir URL directamente (si es corta)
    # callback_data = f"fmt:{format_id}:{url}"
    
    # OPCIÓN 2: Usar un hash/ID corto
    # Guardar url en una base de datos/diccionario con un ID
    # callback_data = f"fmt:{format_id}:ID123"
    
    button = InlineKeyboardButton(
      text=text,
      callback_data=f"fmt:{format_id}"  # Por simplicidad
    )
    buttons.append([button])
  
  return InlineKeyboardMarkup(inline_keyboard=buttons)


# ============================================================================
# PARTE 6: REGISTRAR LOS HANDLERS EN EL DISPATCHER
# ============================================================================

"""
En tu main.py, deberías tener algo así:

# Registrar callback handler
@dp.callback_query(F.data.startswith("fmt:"))
async def callback_handler(callback: CallbackQuery):
    format_id = callback.data.split(":")[1]
    # ... resto del código
    
# O si usas cancelar:
@dp.callback_query(F.data == "cancel")
async def cancel_handler(callback: CallbackQuery):
    await callback.answer("Cancelado")
    await callback.message.edit_text("❌ Cancelado", reply_markup=None)
"""


# ============================================================================
# RESUMEN DE CONCEPTOS CLAVE
# ============================================================================

"""
1. InlineKeyboardButton:
   - text: Lo que ve el usuario
   - callback_data: Dato que se envía al bot (máx 64 caracteres)

2. InlineKeyboardMarkup:
   - inline_keyboard: Lista de listas de botones
   - Cada lista interna = una fila de botones

3. CallbackQuery:
   - callback.data: El callback_data del botón presionado
   - callback.message: El mensaje donde están los botones
   - callback.answer(): SIEMPRE debes llamar esto
   - callback.message.edit_text(): Para editar el mensaje

4. Format ID en yt-dlp:
   - Cada formato tiene un ID único (ej: "137", "140")
   - Usa 'format': format_id en las opciones de yt-dlp
   - info.get('format_id') para obtenerlo

5. Filtro de callbacks:
   - F.data.startswith("fmt:") → Todos que empiezan con "fmt:"
   - F.data == "cancel" → Solo el que es exactamente "cancel"
   - F.data.in_(["opt1", "opt2"]) → Varios específicos
"""
