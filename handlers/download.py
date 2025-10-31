import yt_dlp, os
from config import YT_DLP_OPTIONS
from aiogram.types import InlineKeyboardButton
from utils import filter_useful_formats, remove_duplicate_formats, format_to_text

def get_formats_buttons(url: str) -> str:
  options = YT_DLP_OPTIONS.copy()
  options['quiet'] = True
  
  with yt_dlp.YoutubeDL(options) as ydl:
    info = ydl.extract_info(url, download=False)
    formats = info.get('formats', [])
    
    useful = filter_useful_formats(formats)
    unique = remove_duplicate_formats(useful)

    buttons = []
    
    for f in unique:
      buttons.append(InlineKeyboardButton(
        text=format_to_text(f),
        callback_data=f"fmt:{f.get('format_id')}"
      )
    )
      
    buttons.append(
      InlineKeyboardButton(
        text="❌ Cancelar",
        callback_data="fmt:cancel"
      )
    )
    
    return buttons

def download_video(url: str, format_id: str = None) -> str:
  """Descarga un video con el formato especificado o el por defecto"""
  options = YT_DLP_OPTIONS.copy()
  
  # Si se especifica un formato, usarlo; sino usar el por defecto
  if format_id:
    options['format'] = format_id
  
  with yt_dlp.YoutubeDL(options) as ydl:
    info = ydl.extract_info(url, download=True)
    return ydl.prepare_filename(info)
