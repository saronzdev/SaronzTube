"""Utilidades para procesar y limpiar formatos de video"""

def filter_useful_formats(formats: list) -> list:
  """Filtra formatos útiles (excluye miniaturas y formatos raros)"""
  useful = []
  for f in formats:
    ext = f.get('ext', '')
    height = f.get('height') or 0
    is_audio = f.get('vcodec') == 'none'
    
    # Excluir miniaturas y formatos raros
    if ext in ['mhtml', 'webp', 'jpg']:
      continue
    
    # Para audios, solo permitir mp3, m4a, mp4
    if is_audio and ext not in ['mp3', 'm4a', 'mp4']:
      continue
    
    # Solo videos con altura > 100 o audios permitidos
    if height > 100 or is_audio:
      useful.append(f)
  
  return useful

def remove_duplicate_formats(formats: list) -> list:
  """Elimina formatos duplicados basándose en resolución y extensión"""
  seen = set()
  unique_formats = []
  
  for f in formats:
    height = f.get('height')
    ext = f.get('ext', 'N/A')
    is_audio = f.get('vcodec') == 'none'
    abr = f.get('abr') or 0  # Audio bitrate
    
    if is_audio:
      # Agrupar audios por rangos de calidad (solo uno por rango)
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

def format_to_text(format_info: dict) -> str:
  """Convierte info de formato a texto legible"""
  height = format_info.get('height')
  ext = format_info.get('ext', 'N/A')
  is_audio = format_info.get('vcodec') == 'none'
  abr = format_info.get('abr')  # Audio bitrate en kbps
  fps = format_info.get('fps')
  filesize = format_info.get('filesize') or format_info.get('filesize_approx', 0)
  
  # Convertir tamaño a MB
  size_mb = f"{filesize / (1024 * 1024):.1f}MB" if filesize else "?"
  
  if is_audio:
    quality = f"{int(abr)}k" if abr else "?"
    label = f"🎵 Audio {quality}"
  else:
    label = f"📹 {height}p" if height else "📹 Video"
    if fps:
      label += f"@{int(fps)}fps"
  
  return f"• {label} ({ext}) - {size_mb}"

def format_to_button_label(format_info: dict) -> str:
  """Convierte info de formato a label de botón (más corto)"""
  height = format_info.get('height')
  ext = format_info.get('ext', 'N/A')
  is_audio = format_info.get('vcodec') == 'none'
  abr = format_info.get('abr')
  
  if is_audio:
    quality = f"{int(abr)}k" if abr else "?"
    return f"🎵 {quality} ({ext})"
  else:
    return f"📹 {height}p ({ext})"
