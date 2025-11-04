import yt_dlp, os
from config import YT_DLP_OPTIONS
from aiogram.types import InlineKeyboardButton
from utils import filter_useful_formats, remove_duplicate_formats, format_to_text

def get_formats_buttons(url: str):
  """Obtiene botones de formatos con reintentos y opciones de fallback.
  Evita que un error de formato impida listar los disponibles.
  """
  base = YT_DLP_OPTIONS.copy()
  base['quiet'] = True
  # Remover 'format' para obtener TODOS los formatos disponibles
  base.pop('format', None)

  def _extract(options):
    with yt_dlp.YoutubeDL(options) as ydl:
      return ydl.extract_info(url, download=False)

  info = None
  try:
    info = _extract(base)
  except yt_dlp.utils.DownloadError:
    # Fallback 1: quitar extractor_args especiales de YouTube
    fallback1 = base.copy()
    fallback1.pop('extractor_args', None)
    try:
      info = _extract(fallback1)
    except yt_dlp.utils.DownloadError:
      # Fallback 2: usar opciones mínimas
      minimal = {
        'quiet': True,
        'noprogress': True,
        'nocheckcertificate': True,
        'geo_bypass': True,
        'force_ipv4': base.get('force_ipv4', True),
        'http_headers': base.get('http_headers', {}),
        'user_agent': base.get('user_agent'),
      }
      info = _extract(minimal)

  formats = info.get('formats', []) if info else []
  useful = filter_useful_formats(formats)
  unique = remove_duplicate_formats(useful)

  buttons = []
  for f in unique:
    buttons.append(InlineKeyboardButton(
      text=format_to_text(f),
      callback_data=f"fmt:{f.get('format_id')}"
    ))
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

  def _build_format_string(fmt_obj):
    """Construye una cadena de formato robusta basada en el formato elegido.
    - Si es video-only: combina con bestaudio.
    - Si es audio-only: usa ese audio, con fallback a bestaudio.
    - Si tiene audio+video: selecciona por id.
    Añade fallback general a QUALITY más tarde.
    """
    if not fmt_obj:
      return None
    vcodec = (fmt_obj.get('vcodec') or '').lower()
    acodec = (fmt_obj.get('acodec') or '').lower()
    fid = fmt_obj.get('format_id')
    is_video_only = vcodec != 'none' and acodec == 'none'
    is_audio_only = vcodec == 'none' and acodec != 'none'
    has_both = vcodec != 'none' and acodec != 'none'
    if has_both:
      return f"id={fid}"
    if is_video_only:
      return f"bestvideo[id={fid}]+bestaudio"
    if is_audio_only:
      return f"bestaudio[id={fid}]/bestaudio"
    # fallback genérico por id
    return f"id={fid}"

  # Si se especifica un formato, validarlo contra la lista actual de formatos
  if format_id:
    probe_opts = options.copy()
    probe_opts['quiet'] = True
    with yt_dlp.YoutubeDL(probe_opts) as ydl:
      info = ydl.extract_info(url, download=False)
      formats = info.get('formats', [])
      selected = next((f for f in formats if str(f.get('format_id')) == str(format_id)), None)
    fmt_str = _build_format_string(selected)
    if fmt_str:
      # Añadir fallback general a la cadena definida en config (QUALITY dentro de options['format'])
      # QUALITY viene embebido en options['format'] por defecto; aquí lo reforzamos añadiendo '/best' si no se define
      options['format'] = f"{fmt_str}/best"
    else:
      # Si no encontramos el formato, usa la calidad por defecto del proyecto
      options.pop('format', None)

  # Intentar descargar; si falla por formato, reintentar con mejor disponible
  try:
    with yt_dlp.YoutubeDL(options) as ydl:
      info = ydl.extract_info(url, download=True)
      return ydl.prepare_filename(info)
  except yt_dlp.utils.DownloadError as e:
    # Reintento con fallback fuerte
    fallback_opts = YT_DLP_OPTIONS.copy()
    fallback_opts['quiet'] = options.get('quiet', True)
    with yt_dlp.YoutubeDL(fallback_opts) as ydl:
      info = ydl.extract_info(url, download=True)
      return ydl.prepare_filename(info)
