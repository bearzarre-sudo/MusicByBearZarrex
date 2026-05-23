#!/usr/bin/env python3
"""
PRE-FLIGHT CHECK para Railway
Se ejecuta antes de discord_bot.py
"""

import os
import sys
import logging
import subprocess
import shutil

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("preflight")

def main():
    logger.info("=" * 70)
    logger.info("🚀 PRE-FLIGHT CHECK - DISCORD MUSIC BOT")
    logger.info("=" * 70)
    
    errors = []
    
    # 1. Verificar DISCORD_TOKEN
    logger.info("\n1️⃣ Verificando DISCORD_TOKEN...")
    token = os.getenv("DISCORD_TOKEN")
    if token:
        logger.info(f"✅ DISCORD_TOKEN encontrado ({len(token)} caracteres)")
    else:
        logger.error("❌ DISCORD_TOKEN no definido")
        errors.append("DISCORD_TOKEN no configurado")
    
    # 2. Verificar FFmpeg
    logger.info("\n2️⃣ Verificando FFmpeg...")
    ffmpeg = shutil.which("ffmpeg")
    if ffmpeg:
        logger.info(f"✅ FFmpeg encontrado: {ffmpeg}")
        try:
            result = subprocess.run(
                [ffmpeg, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.split('\n')[0]
                logger.info(f"✅ {version}")
            else:
                logger.error("❌ FFmpeg no funciona correctamente")
                errors.append("FFmpeg malconfigured")
        except Exception as e:
            logger.error(f"❌ Error probando FFmpeg: {e}")
            errors.append(f"FFmpeg error: {e}")
    else:
        logger.error("❌ FFmpeg NO encontrado en PATH")
        logger.error("   En Railway, asegúrate de que nixpacks.toml incluye: \"ffmpeg\"")
        errors.append("FFmpeg not found")
    
    # 3. Verificar Python version
    logger.info("\n3️⃣ Verificando Python...")
    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    if sys.version_info >= (3, 11):
        logger.info(f"✅ Python {py_version}")
    else:
        logger.error(f"❌ Python {py_version} (requerido >= 3.11)")
        errors.append(f"Python {py_version} not supported")
    
    # 4. Verificar dependencias Python
    logger.info("\n4️⃣ Verificando dependencias Python...")
    deps = {
        "discord": "discord.py",
        "yt_dlp": "yt-dlp",
        "aiohttp": "aiohttp",
    }
    
    for module, name in deps.items():
        try:
            __import__(module)
            logger.info(f"✅ {name}")
        except ImportError:
            logger.error(f"❌ {name}")
            errors.append(f"{name} not installed")
    
    # 5. Verificar PyNaCl
    logger.info("\n5️⃣ Verificando PyNaCl (para voice)...")
    try:
        import nacl
        logger.info("✅ PyNaCl instalado")
    except ImportError:
        logger.warning("⚠️ PyNaCl no instalado - Algunos features pueden fallar")
        logger.warning("   Instala con: pip install PyNaCl")
    
    # 6. Verificar discord.FFmpegPCMAudio
    logger.info("\n6️⃣ Verificando discord.FFmpegPCMAudio...")
    try:
        from discord import FFmpegPCMAudio
        logger.info("✅ FFmpegPCMAudio disponible")
    except ImportError as e:
        logger.error(f"❌ FFmpegPCMAudio no disponible: {e}")
        errors.append("FFmpegPCMAudio import failed")
    
    # Resumen
    logger.info("\n" + "=" * 70)
    if errors:
        logger.error("❌ ERRORES ENCONTRADOS:")
        for error in errors:
            logger.error(f"   - {error}")
        logger.error("\n🔧 SOLUCIONES:")
        logger.error("1. Si FFmpeg no se encuentra:")
        logger.error("   - Verificar nixpacks.toml: nixPkgs = [...\"ffmpeg\"...]")
        logger.error("   - Hacer rebuild en Railway (git push)")
        logger.error("\n2. Si falta DISCORD_TOKEN:")
        logger.error("   - Ir a Railway Dashboard → Variables")
        logger.error("   - Agregar: DISCORD_TOKEN = <tu_token>")
        logger.error("\n3. Si faltan dependencias Python:")
        logger.error("   - requirements.txt debería tener todas")
        logger.error("   - Hacer rebuild en Railway")
        logger.info("\n⏸️ No iniciando el bot debido a errores críticos")
        return 1
    else:
        logger.info("✅ TODOS LOS CHECKS PASARON")
        logger.info("✅ El bot está listo para iniciarse")
        logger.info("\n🚀 Iniciando Discord Music Bot...")
        return 0

if __name__ == "__main__":
    sys.exit(main())
