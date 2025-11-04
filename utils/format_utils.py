def filter_useful_formats(formats: list) -> list:
  useful = []
  for f in formats:
    ext = f.get('ext', '')
    height = f.get('height') or 0
    is_audio = f.get('vcodec') == 'none'
    
    if ext in ['mhtml', 'webp', 'jpg']:
      continue
    
    if is_audio and ext not in ['mp3', 'm4a', 'mp4']:
      continue
    
    if height > 100 or is_audio:
      useful.append(f)
  
  return useful

def remove_duplicate_formats(formats: list) -> list:
  seen = set()
  unique_formats = []
  
  for f in formats:
    height = f.get('height')
    ext = f.get('ext', 'N/A')
    is_audio = f.get('vcodec') == 'none'
    abr = f.get('abr') or 0
    
    if is_audio:
      if abr < 70:
        quality_range = 'low'
      elif abr < 100:
        quality_range = 'medium'
      else:
        quality_range = 'high'
      key = ('audio', quality_range)
    else:
      key = (height, ext)
    
    if key not in seen:
      seen.add(key)
      unique_formats.append(f)
  
  return unique_formats

def format_to_text(format_info: dict, duration: float | None = None) -> str:
  """Devuelve un texto amigable para el botón del formato, incluyendo tamaño.
  Si no hay tamaño real en los metadatos, intenta estimarlo con tbr/abr/vbr y duración.
  """
  height = format_info.get('height')
  ext = format_info.get('ext', 'N/A')
  vcodec = (format_info.get('vcodec') or '').lower()
  is_audio = vcodec == 'none'
  abr = format_info.get('abr')  # kbps
  vbr = format_info.get('vbr')  # kbps
  tbr = format_info.get('tbr')  # kbps (total)
  filesize = format_info.get('filesize') or format_info.get('filesize_approx')

  def _fmt_size_mb(bytes_val: float) -> str:
    return f"{bytes_val / (1024 * 1024):.1f}MB"

  size_txt = " "
  if filesize and isinstance(filesize, (int, float)) and filesize > 0:
    size_txt = _fmt_size_mb(float(filesize))
  elif duration and duration > 0:
    # Estimar tamaño
    kbps = None
    if tbr:
      kbps = tbr
    else:
      if is_audio:
        kbps = abr or tbr
      else:
        # Para video-only estimar con vbr + audio base (96 kbps)
        if vcodec != 'none' and (format_info.get('acodec') or '').lower() == 'none':
          kbps = (vbr or 0) + 96
        else:
          # Si es AV, suma vbr+abr si existen
          if vbr and abr:
            kbps = vbr + abr
          else:
            kbps = vbr or abr or tbr
    if kbps and kbps > 0:
      bytes_est = (kbps * 1000 / 8.0) * float(duration)
      size_txt = f"≈{_fmt_size_mb(bytes_est)}"

  if is_audio:
    quality = f"{int(abr)}k" if abr else ""
    label = f"🎵 Audio {quality}".strip()
  else:
    label = f"📹 {height}p" if height else "📹 Video"

  return f"{label} {ext} {size_txt}"
