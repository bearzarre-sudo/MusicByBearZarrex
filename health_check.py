#!/usr/bin/env python3
# ==================================================
# DISCORD BOT - HEALTH CHECK
# Verifica que todas las dependencias estén OK
# ==================================================

import sys
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

def check_python():
    version = sys.version_info
    if version.major == 3 and version.minor >= 11:
        logging.info(f"✅ Python {version.major}.{version.minor} OK")
        return True
    logging.error(f"❌ Python {version.major}.{version.minor} (requerido: 3.11+)")
    return False

def check_module(name):
    try:
        __import__(name)
        logging.info(f"✅ {name} instalado")
        return True
    except ImportError:
        logging.error(f"❌ {name} NO instalado")
        return False

def check_ffmpeg():
    try:
        result = subprocess.run(
            ["ffmpeg", "-version"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            logging.info("✅ FFmpeg disponible")
            return True
    except Exception as e:
        logging.error(f"❌ FFmpeg no disponible: {e}")
        return False

def main():
    logging.info("🔍 Verificando dependencies...\n")
    
    checks = [
        ("Python 3.11+", check_python),
        ("discord", lambda: check_module("discord")),
        ("yt_dlp", lambda: check_module("yt_dlp")),
        ("aiohttp", lambda: check_module("aiohttp")),
        ("nacl", lambda: check_module("nacl")),
        ("FFmpeg", check_ffmpeg),
    ]
    
    results = []
    for name, check_fn in checks:
        try:
            results.append(check_fn())
        except Exception as e:
            logging.error(f"❌ Error en {name}: {e}")
            results.append(False)
    
    logging.info(f"\n{'='*50}")
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        logging.info(f"✅ TODAS LAS VERIFICACIONES PASARON ({passed}/{total})")
        logging.info("🚀 El bot está listo para usar")
        return 0
    else:
        logging.error(f"❌ {total - passed}/{total} VERIFICACIONES FALLARON")
        logging.error("Instala las dependencias faltantes:")
        logging.error("  pip install -r requirements.txt")
        return 1

if __name__ == "__main__":
    sys.exit(main())
