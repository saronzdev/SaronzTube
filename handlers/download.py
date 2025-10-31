import yt_dlp, os
from config import YT_DLP_OPTIONS
from aiogram.types import InlineKeyboardButton
from utils import filter_useful_formats, remove_duplicate_formats, format_to_text

def get_formats_buttons(url: str) -> str:
  """Obtiene lista simple de formatos disponibles"""
  with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
    info = ydl.extract_info(url, download=False)
    formats = info.get('formats', [])
    
    # Limpiar y filtrar formatos
    useful = filter_useful_formats(formats)
    unique = remove_duplicate_formats(useful)
    
    # Generar texto
    # text = f"📋 Formatos únicos: {len(unique)}\n\n"
    # text += '\n'.join(format_to_text(f) for f in unique)

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

def download_video(url: str) -> str:
  """Descarga un video con el formato por defecto"""
  with yt_dlp.YoutubeDL(YT_DLP_OPTIONS) as ydl:
    info = ydl.extract_info(url, download=True)
    return ydl.prepare_filename(info)
