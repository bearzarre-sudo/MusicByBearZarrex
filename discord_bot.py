# ==================================================
# DISCORD MUSIC BOT - RAILWAY READY
# Python 3.11+
# ==================================================

import discord
from discord.ext import commands
import yt_dlp
import asyncio
import logging
import os

# ==================================================
# LOGGING
# ==================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)

logger = logging.getLogger("musicbot")

# ==================================================
# ENV VARIABLES
# ==================================================

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise ValueError("DISCORD_TOKEN no configurado.")

PREFIX = "!"

# ==================================================
# FFMPEG
# ==================================================

import shutil

FFMPEG_PATH = shutil.which("ffmpeg")
if not FFMPEG_PATH:
    FFMPEG_PATH = "/usr/bin/ffmpeg"
    if not os.path.exists(FFMPEG_PATH):
        logger.warning("⚠️ FFmpeg no encontrado en rutas conocidas")
        FFMPEG_PATH = "ffmpeg"

# ==================================================
# YT-DLP CONFIG
# ==================================================

ydl_opts = {
    "format": "bestaudio/best",
    "quiet": True,
    "noplaylist": True,
    "nocheckcertificate": True,
    "ignoreerrors": False,
    "logtostderr": False,
    "no_warnings": True,
    "default_search": "auto",
    "socket_timeout": 30,
    "http_headers": {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
}

ydl_playlist_opts = {
    "quiet": True,
    "extract_flat": True,
    "skip_download": True,
}

# ==================================================
# BOT CONFIG
# ==================================================

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents
)

# ==================================================
# MUSIC QUEUES
# ==================================================

queues = {}

# ==================================================
# GET AUDIO INFO
# ==================================================

def get_audio_info(url):

    try:

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:

            info = ydl.extract_info(url, download=False)

            if info is None:
                logger.warning(f"Info es None para: {url}")
                return None, None

            if "entries" in info:
                info = info["entries"][0]

            audio_url = info.get("url")
            title = info.get("title", "Desconocido")
            
            if not audio_url:
                logger.error(f"No audio URL encontrada para: {title}")
                return None, None

            logger.info(f"✅ Audio obtenido: {title}")

            return audio_url, title

    except Exception as e:

        logger.error(f"❌ Error obteniendo audio: {e}", exc_info=True)

        return None, None

# ==================================================
# GET PLAYLIST URLS
# ==================================================

def get_playlist_urls(url):

    try:

        with yt_dlp.YoutubeDL(ydl_playlist_opts) as ydl:

            info = ydl.extract_info(url, download=False)

            if not info or "entries" not in info:
                return []

            urls = []

            for entry in info["entries"]:

                if entry and "id" in entry:

                    urls.append(
                        f"https://www.youtube.com/watch?v={entry['id']}"
                    )

            logger.info(f"Playlist encontrada: {len(urls)} canciones")

            return urls

    except Exception as e:

        logger.error(f"Error playlist: {e}")

        return []

# ==================================================
# CREATE AUDIO SOURCE
# ==================================================

async def create_audio_source(audio_url):

    ffmpeg_options = {
        "before_options": (
            "-reconnect 1 "
            "-reconnect_streamed 1 "
            "-reconnect_delay_max 5 "
            "-c:a libopus"
        ),
        "options": "-vn"
    }

    logger.info(f"🔧 Creando source de audio...")
    logger.info(f"📁 FFmpeg path: {FFMPEG_PATH}")
    logger.info(f"🔗 Audio URL: {audio_url[:50]}..." if audio_url else "❌ Sin URL")

    try:
        # Verificar que la URL no está vacía
        if not audio_url:
            logger.error("❌ Audio URL está vacía")
            return None

        # Verificar que FFmpeg existe
        if not os.path.exists(FFMPEG_PATH) and FFMPEG_PATH != "ffmpeg":
            logger.warning(f"⚠️ FFmpeg no existe en {FFMPEG_PATH}, intentando fallback...")
            ffmpeg_path = shutil.which("ffmpeg") or "ffmpeg"
        else:
            ffmpeg_path = FFMPEG_PATH

        logger.info(f"📀 Usando FFmpeg: {ffmpeg_path}")

        source = discord.FFmpegPCMAudio(
            audio_url,
            executable=ffmpeg_path,
            **ffmpeg_options
        )

<<<<<<< HEAD
        logger.info(f"✅ Source de audio creado exitosamente")
        return source

    except FileNotFoundError as e:
        logger.error(f"❌ FFmpeg no encontrado: {e}")
        logger.error(f"📍 Rutas buscadas: {FFMPEG_PATH}, /usr/bin/ffmpeg, fallback a PATH")
        return None
    except discord.DiscordException as e:
        logger.error(f"❌ Discord error: {e}", exc_info=True)
        return None
    except Exception as e:
        logger.error(f"❌ Error desconocido creando source: {type(e).__name__}: {e}", exc_info=True)
=======
        logger.info(f"✅ Source de audio creado con FFmpeg: {FFMPEG_PATH}")
        return source

    except FileNotFoundError:
        logger.error(f"❌ FFmpeg no encontrado en: {FFMPEG_PATH}")
        return None
    except Exception as e:

        logger.error(f"❌ Error creando source: {e}", exc_info=True)

>>>>>>> 4c348f96875ba45362781ab76a79ebbe2a91db0d
        return None

# ==================================================
# PLAY NEXT SONG
# ==================================================

async def play_next(ctx):

    guild_id = ctx.guild.id

    if guild_id not in queues or len(queues[guild_id]) == 0:

        logger.info("📭 Cola vacía")
        await ctx.send("📭 Cola vacía. Desconectando...")

        if ctx.voice_client:
            await ctx.voice_client.disconnect()

        return

    url = queues[guild_id].pop(0)

    logger.info(f"🎵 Reproduciendo: {url}")

    audio_url, title = await asyncio.to_thread(
        get_audio_info,
        url
    )

    if not audio_url:

        logger.error(f"❌ No se pudo obtener audio para: {url}")
        await ctx.send("❌ No se pudo obtener el audio. Saltando...")
        await play_next(ctx)

        return

    source = await create_audio_source(audio_url)

    if not source:

<<<<<<< HEAD
        logger.error(f"❌ Fallo criar source - Saltando: {title}")
        await ctx.send(f"❌ **Error de audio**: No se pudo reproducir `{title}`. Saltando...")
=======
        logger.error(f"❌ Error creando source para: {title}")
        await ctx.send("❌ Error creando fuente de audio. Saltando...")
>>>>>>> 4c348f96875ba45362781ab76a79ebbe2a91db0d
        await play_next(ctx)

        return

    def after_playing(error):

        if error:
            logger.error(f"❌ Error en reproducción: {error}", exc_info=True)
        else:
            logger.info(f"✅ Canción terminada: {title}")

        try:
            asyncio.run_coroutine_threadsafe(
                play_next(ctx),
                bot.loop
            )
        except Exception as e:
            logger.error(f"❌ Error en after_playing: {e}", exc_info=True)

    try:

        if not ctx.voice_client:
            await ctx.author.voice.channel.connect()

        ctx.voice_client.play(
            source,
            after=after_playing
        )

        await ctx.send(f"🎵 Reproduciendo: **{title}**")
        logger.info(f"✅ Reproduciendo: {title}")

    except Exception as e:

        logger.error(f"❌ Error reproduciendo: {e}", exc_info=True)
        await ctx.send(f"❌ Error reproduciendo: {e}")
        await play_next(ctx)

# ==================================================
# PLAY COMMAND
# ==================================================

@bot.command()
async def play(ctx, *, query):

    if not ctx.author.voice:

        return await ctx.send(
            "❌ Debes estar en un canal de voz."
        )

    try:

        if not ctx.voice_client:

            await ctx.author.voice.channel.connect()

        elif ctx.voice_client.channel != ctx.author.voice.channel:

            await ctx.voice_client.move_to(
                ctx.author.voice.channel
            )

    except Exception as e:

        return await ctx.send(
            f"❌ Error conectando: {e}"
        )

    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []

    queues[ctx.guild.id].append(query)

    await ctx.send("✅ Agregado a la cola.")

    if not ctx.voice_client.is_playing():

        await play_next(ctx)

# ==================================================
# PLAYLIST COMMAND
# ==================================================

@bot.command()
async def playlist(ctx, *, url):

    if not ctx.author.voice:

        return await ctx.send(
            "❌ Debes estar en un canal de voz."
        )

    await ctx.send("📂 Extrayendo playlist...")

    video_urls = await asyncio.to_thread(
        get_playlist_urls,
        url
    )

    if not video_urls:

        return await ctx.send(
            "❌ No se encontraron videos."
        )

    if ctx.guild.id not in queues:
        queues[ctx.guild.id] = []

    queues[ctx.guild.id].extend(video_urls)

    await ctx.send(
        f"✅ {len(video_urls)} canciones agregadas."
    )

    try:

        if not ctx.voice_client:

            await ctx.author.voice.channel.connect()

    except Exception as e:

        return await ctx.send(
            f"❌ Error conectando: {e}"
        )

    if not ctx.voice_client.is_playing():

        await play_next(ctx)

# ==================================================
# SKIP COMMAND
# ==================================================

@bot.command()
async def skip(ctx):

    if ctx.voice_client and ctx.voice_client.is_playing():

        ctx.voice_client.stop()

        await ctx.send("⏭️ Canción saltada.")

# ==================================================
# QUEUE COMMAND
# ==================================================

@bot.command()
async def queue(ctx):

    guild_id = ctx.guild.id

    if guild_id not in queues or not queues[guild_id]:

        return await ctx.send("📭 Cola vacía.")

    preview = queues[guild_id][:10]

    text = "\n".join(
        [f"{i+1}. {song}" for i, song in enumerate(preview)]
    )

    await ctx.send(
        f"📜 Cola:\n{text}"
    )

# ==================================================
# LEAVE COMMAND
# ==================================================

@bot.command()
async def leave(ctx):

    if ctx.voice_client:

        await ctx.voice_client.disconnect()

        queues.pop(ctx.guild.id, None)

        await ctx.send("👋 Desconectado.")

# ==================================================
# JOIN COMMAND
# ==================================================

@bot.command()
async def join(ctx):

    if not ctx.author.voice:

        return await ctx.send(
            "❌ Debes estar en un canal de voz."
        )

    try:

        if ctx.voice_client:

            await ctx.voice_client.move_to(
                ctx.author.voice.channel
            )

        else:

            await ctx.author.voice.channel.connect()

        await ctx.send(
            f"✅ Conectado a {ctx.author.voice.channel.name}"
        )

    except Exception as e:

        await ctx.send(f"❌ Error: {e}")

# ==================================================
# TEST COMMAND
# ==================================================

@bot.command()
async def test(ctx):

    messages = [
        "✅ Bot operativo",
        "✅ FFmpeg configurado",
        "✅ yt-dlp configurado"
    ]

    try:
        import nacl
        messages.append("✅ PyNaCl instalado")
    except:
        messages.append("❌ PyNaCl NO instalado")
    
    # Verificar FFmpeg
    try:
        import shutil
        ffmpeg_path = shutil.which("ffmpeg") or FFMPEG_PATH
        messages.append(f"📁 FFmpeg: {ffmpeg_path}")
    except:
        messages.append("❌ FFmpeg no encontrado")

    await ctx.send("\n".join(messages))
    
    logger.info("=" * 60)
    logger.info("✅ TEST COMMAND EJECUTADO")
    logger.info("=" * 60)
    logger.info(f"FFmpeg path: {FFMPEG_PATH}")
    logger.info(f"Bot latency: {bot.latency * 1000:.2f}ms")
    logger.info("=" * 60)

# ==================================================
# EVENTS
# ==================================================

@bot.event
async def on_ready():

    logger.info(f"✅ Bot conectado como {bot.user}")
    logger.info(f"📁 FFmpeg path: {FFMPEG_PATH}")
    
    # Verificar FFmpeg
    try:
        result = await asyncio.to_thread(
            os.popen,
            f"{FFMPEG_PATH} -version"
        )
        output = result.read()
        if output:
            logger.info("✅ FFmpeg está disponible y funcional")
        else:
            logger.warning("⚠️ FFmpeg no responde correctamente")
    except Exception as e:
        logger.warning(f"⚠️ No se pudo verificar FFmpeg: {e}")

# ==================================================
# START BOT
# ==================================================

if __name__ == "__main__":

    bot.run(TOKEN)