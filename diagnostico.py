#!/usr/bin/env python3
"""
Script de diagnóstico completo para la VM de Azure
"""
import os
import sys
import yt_dlp
from config import YT_DLP_OPTIONS, COOKIES_FILE

print("=" * 60)
print("🔍 DIAGNÓSTICO DE SARONZTUBE")
print("=" * 60)

# 1. Verificar versión de yt-dlp
print("\n1️⃣ Versión de yt-dlp:")
import yt_dlp.version
print(f"   yt-dlp: {yt_dlp.version.__version__}")

# 2. Verificar cookies
print("\n2️⃣ Archivo de cookies:")
print(f"   Ruta: {COOKIES_FILE}")
print(f"   Existe: {'✅ Sí' if os.path.exists(COOKIES_FILE) else '❌ No'}")
if os.path.exists(COOKIES_FILE):
    size = os.path.getsize(COOKIES_FILE)
    print(f"   Tamaño: {size} bytes")
    if size == 0:
        print("   ⚠️  Archivo vacío!")

# 3. Verificar configuración
print("\n3️⃣ Configuración de YT_DLP_OPTIONS:")
print(f"   cookiefile: {YT_DLP_OPTIONS.get('cookiefile')}")
print(f"   player_client: {YT_DLP_OPTIONS.get('extractor_args', {}).get('youtube', {}).get('player_client')}")

# 4. Probar extracción de información
print("\n4️⃣ Prueba de extracción (sin descargar):")
TEST_URL = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
print(f"   URL: {TEST_URL}")

try:
    print("   ⏳ Extrayendo información...")
    with yt_dlp.YoutubeDL(YT_DLP_OPTIONS) as ydl:
        info = ydl.extract_info(TEST_URL, download=False)
        print(f"   ✅ Éxito!")
        print(f"   - Título: {info.get('title', 'N/A')[:50]}...")
        print(f"   - Formatos: {len(info.get('formats', []))}")
        
except Exception as e:
    print(f"   ❌ Error: {str(e)[:100]}")
    print("\n💡 Posibles causas:")
    print("   - Cookies expiradas o mal formateadas")
    print("   - IP de Azure bloqueada por YouTube")
    print("   - yt-dlp desactualizado")
    print("   - Problema de red/firewall")
    sys.exit(1)

# 5. Verificar conectividad
print("\n5️⃣ Conectividad:")
import socket
try:
    socket.create_connection(("www.youtube.com", 443), timeout=5)
    print("   ✅ Conexión a YouTube OK")
except:
    print("   ❌ No se puede conectar a YouTube")

print("\n" + "=" * 60)
print("✅ DIAGNÓSTICO COMPLETO")
print("=" * 60)
