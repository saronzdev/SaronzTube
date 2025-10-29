import yt_dlp, os
from config import YT_DLP_OPTIONS
from utils import filter_useful_formats, remove_duplicate_formats, format_to_button_label
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_formats_with_keyboard(url: str) -> tuple[str, InlineKeyboardMarkup, list]:
  """Obtiene formatos y genera teclado inline"""
  with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
    info = ydl.extract_info(url, download=False)
    formats = info.get('formats', [])
    
    # Limpiar y filtrar formatos
    useful = filter_useful_formats(formats)
    unique = remove_duplicate_formats(useful)
    
    # Crear botones inline
    buttons = []
    for f in unique:
      format_id = f.get('format_id')
      label = format_to_button_label(f)
      
      # Crear botón con callback_data = format_id
      buttons.append([InlineKeyboardButton(text=label, callback_data=f"fmt_{format_id}")])
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    text = f"📋 Selecciona el formato que deseas descargar:"
    
    return text, keyboard, unique

def download_video(url: str, format_id: str = None) -> str:
  """Descarga un video con el formato especificado"""
  options = YT_DLP_OPTIONS.copy()
  if format_id:
    options['format'] = format_id
  
  with yt_dlp.YoutubeDL(options) as ydl:
    info = ydl.extract_info(url, download=True)
    return ydl.prepare_filename(info)
