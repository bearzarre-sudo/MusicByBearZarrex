#!/usr/bin/env python3
"""
DIAGNOSTIC TOOL - Discord Bot Music Issue
Diagnostica problemas de reproducción de música
"""

import os
import sys
import subprocess
import asyncio
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)
logger = logging.getLogger("diagnostic")

def check_ffmpeg():
    """Verifica FFmpeg en varias locaciones"""
    logger.info("=" * 60)
    logger.info("🔍 FFMPEG CHECK")
    logger.info("=" * 60)
    
    paths_to_check = [
        "ffmpeg",
        "/usr/bin/ffmpeg",
        "/usr/local/bin/ffmpeg",
        "C:\\Program Files\\ffmpeg\\bin\\ffmpeg.exe",
        "C:\\ffmpeg\\bin\\ffmpeg.exe",
    ]
    
    import shutil
    ffmpeg_in_path = shutil.which("ffmpeg")
    
    if ffmpeg_in_path:
        logger.info(f"✅ FFmpeg encontrado en PATH: {ffmpeg_in_path}")
        
        try:
            result = subprocess.run(
                [ffmpeg_in_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                logger.info(f"✅ FFmpeg versión: {version_line}")
            else:
                logger.error(f"❌ FFmpeg retorna error: {result.stderr[:200]}")
        except Exception as e:
            logger.error(f"❌ No se pudo ejecutar FFmpeg: {e}")
    else:
        logger.error("❌ FFmpeg NO encontrado en PATH")
    
    logger.info("\n📍 Buscando en locaciones conocidas...")
    for path in paths_to_check:
        if os.path.exists(path):
            logger.info(f"  ✅ Encontrado: {path}")
        else:
            logger.info(f"  ❌ No existe: {path}")

def check_discord_py():
    """Verifica discord.py[voice]"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 DISCORD.PY[VOICE] CHECK")
    logger.info("=" * 60)
    
    try:
        import discord
        logger.info(f"✅ discord.py versión: {discord.__version__}")
        
        # Verificar que voice está disponible
        from discord.ext import voice_client
        logger.info("✅ discord.ext.voice_client disponible")
        
        # Verificar FFmpegPCMAudio
        from discord import FFmpegPCMAudio
        logger.info("✅ discord.FFmpegPCMAudio disponible")
    except ImportError as e:
        logger.error(f"❌ Error importando discord: {e}")

def check_yt_dlp():
    """Verifica yt-dlp"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 YT-DLP CHECK")
    logger.info("=" * 60)
    
    try:
        import yt_dlp
        logger.info(f"✅ yt-dlp versión: {yt_dlp.__version__}")
        
        # Intentar extraer info de un video de prueba
        logger.info("\n📽️ Probando extracción de info...")
        with yt_dlp.YoutubeDL({"quiet": True}) as ydl:
            info = ydl.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=False)
            if info and info.get("url"):
                logger.info(f"✅ URL de audio obtenida: {info.get('url')[:50]}...")
                logger.info(f"✅ Título: {info.get('title')}")
            else:
                logger.error("❌ No se pudo obtener URL de audio")
    except ImportError:
        logger.error("❌ yt-dlp no instalado")
    except Exception as e:
        logger.error(f"❌ Error con yt-dlp: {e}")

def check_pynacl():
    """Verifica PyNaCl para voice"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 PYNACL CHECK")
    logger.info("=" * 60)
    
    try:
        import nacl
        logger.info(f"✅ PyNaCl instalado (versión: {nacl.__version__ if hasattr(nacl, '__version__') else 'desconocida'})")
    except ImportError:
        logger.error("❌ PyNaCl NO instalado - Necesario para voice")
        logger.error("   Instala con: pip install PyNaCl")

def check_audio_url():
    """Verifica si se puede acceder a una URL de audio"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 AUDIO URL CONNECTIVITY CHECK")
    logger.info("=" * 60)
    
    try:
        import yt_dlp
        logger.info("Obteniendo URL de audio...")
        
        with yt_dlp.YoutubeDL({
            "quiet": True,
            "format": "bestaudio/best"
        }) as ydl:
            info = ydl.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=False)
            audio_url = info.get("url")
            
            if audio_url:
                logger.info(f"✅ URL obtenida: {audio_url[:50]}...")
                
                # Verificar que la URL es accesible
                import urllib.request
                logger.info("Verificando acceso a URL...")
                req = urllib.request.Request(audio_url, headers={'User-Agent': 'Mozilla/5.0'})
                try:
                    response = urllib.request.urlopen(req, timeout=5)
                    logger.info(f"✅ URL es accesible (HTTP {response.status})")
                except Exception as e:
                    logger.warning(f"⚠️ Problema accediendo URL: {e}")
            else:
                logger.error("❌ No se pudo obtener URL de audio")
    except Exception as e:
        logger.error(f"❌ Error en audio URL check: {e}")

def check_ffmpeg_with_audio():
    """Intenta crear un source de audio con FFmpeg"""
    logger.info("\n" + "=" * 60)
    logger.info("🔍 FFMPEG AUDIO SOURCE CHECK")
    logger.info("=" * 60)
    
    try:
        import discord
        import yt_dlp
        import shutil
        
        ffmpeg_path = shutil.which("ffmpeg") or "ffmpeg"
        logger.info(f"FFmpeg path: {ffmpeg_path}")
        
        # Obtener URL de audio
        logger.info("Obteniendo URL de audio...")
        with yt_dlp.YoutubeDL({"quiet": True, "format": "bestaudio/best"}) as ydl:
            info = ydl.extract_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ", download=False)
            audio_url = info.get("url")
        
        if not audio_url:
            logger.error("❌ No se pudo obtener URL de audio")
            return
        
        logger.info("Creando FFmpegPCMAudio...")
        ffmpeg_options = {
            "before_options": (
                "-reconnect 1 "
                "-reconnect_streamed 1 "
                "-reconnect_delay_max 5"
            ),
            "options": "-vn"
        }
        
        try:
            source = discord.FFmpegPCMAudio(
                audio_url,
                executable=ffmpeg_path,
                **ffmpeg_options
            )
            logger.info("✅ FFmpegPCMAudio creado exitosamente")
            source.cleanup()  # Limpiar
        except FileNotFoundError:
            logger.error(f"❌ FFmpeg no encontrado: {ffmpeg_path}")
        except Exception as e:
            logger.error(f"❌ Error creando source: {type(e).__name__}: {e}")
            
    except Exception as e:
        logger.error(f"❌ Error general: {e}")

def main():
    logger.info("\n")
    logger.info("╔" + "=" * 58 + "╗")
    logger.info("║" + " " * 58 + "║")
    logger.info("║" + "  🎵 DISCORD MUSIC BOT - DIAGNOSTIC TOOL  ".center(58) + "║")
    logger.info("║" + " " * 58 + "║")
    logger.info("╚" + "=" * 58 + "╝")
    
    check_ffmpeg()
    check_pynacl()
    check_discord_py()
    check_yt_dlp()
    check_audio_url()
    check_ffmpeg_with_audio()
    
    logger.info("\n" + "=" * 60)
    logger.info("✅ DIAGNOSTIC COMPLETO")
    logger.info("=" * 60)
    logger.info("\n📝 Interpretación de resultados:")
    logger.info("  ✅ = Todo OK")
    logger.info("  ⚠️ = Advertencia, pero puede funcionar")
    logger.info("  ❌ = Error crítico que previene reproducción")
    logger.info("\n💡 Si hay ❌ en FFmpeg CHECK: Railway no tiene ffmpeg instalado")
    logger.info("   Solución: Verificar nixpacks.toml contiene: nixPkgs = [...\"ffmpeg\"...]")

if __name__ == "__main__":
    main()
