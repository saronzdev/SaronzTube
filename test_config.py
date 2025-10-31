#!/usr/bin/env python3
"""Test para verificar que config.py encuentra cookies.txt"""
import os
from config import YT_DLP_OPTIONS, COOKIES_FILE

print("🔍 Verificando configuración...")
print(f"Directorio actual: {os.getcwd()}")
print(f"Ruta de cookies: {COOKIES_FILE}")
print(f"Archivo existe: {'✅ Sí' if os.path.exists(COOKIES_FILE) else '❌ No'}")
print(f"cookiefile en YT_DLP_OPTIONS: {YT_DLP_OPTIONS.get('cookiefile')}")

if YT_DLP_OPTIONS.get('cookiefile'):
    print("\n✅ El bot usará cookies")
else:
    print("\n⚠️ El bot NO usará cookies (solo clientes móviles)")
