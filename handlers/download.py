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
  # Usar extractor por defecto de escritorio (evitar clientes móviles que limitan a 360p)
  base.pop('extractor_args', None)

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
  # Para descargas de alta calidad, permitir que yt-dlp use el extractor web completo
  options.pop('extractor_args', None)

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
    height = fmt_obj.get('height') or 0
    is_video_only = vcodec != 'none' and acodec == 'none'
    is_audio_only = vcodec == 'none' and acodec != 'none'
    has_both = vcodec != 'none' and acodec != 'none'
    # Limitar audio según resolución para evitar tamaños desproporcionados
    def _audio_cap(h):
      if h <= 144:
        return 64
      if h <= 360:
        return 96
      if h <= 480:
        return 128
      return 160

    abr_cap = _audio_cap(height)

    if has_both:
      # Seleccionar exactamente ese id; fallback limitado por altura
      return f"id={fid}/best[height<={height}]"
    if is_video_only:
      # Combinar con bestaudio limitado por abr; fallback restringido por altura
      return (
        f"bestvideo[id={fid}]+bestaudio[abr<={abr_cap}]"
        f"/bestvideo[height<={height}]+bestaudio[abr<={abr_cap}]"
        f"/best[height<={height}]"
      )
    if is_audio_only:
      # Mantener audio solamente; fallback a bestaudio con límite
      return f"bestaudio[id={fid}]/bestaudio[abr<={abr_cap}]/bestaudio"
    # fallback genérico por id con límite de altura si existe
    return f"id={fid}/best[height<={height}]"

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
      # Usar la cadena robusta que ya incluye fallbacks limitados por altura
      options['format'] = fmt_str
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
