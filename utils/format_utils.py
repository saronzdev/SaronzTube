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

def format_to_text(format_info: dict) -> str:
  height = format_info.get('height')
  ext = format_info.get('ext', 'N/A')
  is_audio = format_info.get('vcodec') == 'none'
  abr = format_info.get('abr')
  fps = format_info.get('fps')
  filesize = format_info.get('filesize') or format_info.get('filesize_approx', 0)
  
  size_mb = f"{filesize / (1024 * 1024):.1f}MB" if filesize else " "
  
  if is_audio:
    quality = f"{int(abr)}k" if abr else " "
    label = f"🎵 Audio {quality}"
  else:
    label = f"📹 {height}p" if height else "📹 Video"
    if fps:
      label += f"{int(fps)}"
  
  return f"{label} {ext} {size_mb}"
