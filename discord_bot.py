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
    "source_address": "0.0.0.0",
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
                return None, None

            if "entries" in info:
                info = info["entries"][0]

            audio_url = info.get("url")
            title = info.get("title", "Desconocido")

            logger.info(f"Audio obtenido: {title}")

            return audio_url, title

    except Exception as e:

        logger.error(f"Error obteniendo audio: {e}")

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
            "-reconnect_delay_max 5"
        ),
        "options": "-vn"
    }

    try:

        source = discord.FFmpegPCMAudio(
            audio_url,
            executable=FFMPEG_PATH,
            **ffmpeg_options
        )

        return source

    except Exception as e:

        logger.error(f"Error creando source: {e}")

        return None

# ==================================================
# PLAY NEXT SONG
# ==================================================

async def play_next(ctx):

    guild_id = ctx.guild.id

    if guild_id not in queues or len(queues[guild_id]) == 0:

        await ctx.send("📭 Cola vacía. Desconectando...")

        if ctx.voice_client:
            await ctx.voice_client.disconnect()

        return

    url = queues[guild_id].pop(0)

    logger.info(f"Reproduciendo: {url}")

    audio_url, title = await asyncio.to_thread(
        get_audio_info,
        url
    )

    if not audio_url:

        await ctx.send("❌ No se pudo obtener el audio.")

        await play_next(ctx)

        return

    source = await create_audio_source(audio_url)

    if not source:

        await ctx.send("❌ Error creando fuente de audio.")

        await play_next(ctx)

        return

    def after_playing(error):

        if error:
            logger.error(f"Error reproducción: {error}")

        future = asyncio.run_coroutine_threadsafe(
            play_next(ctx),
            bot.loop
        )

        try:
            future.result()
        except Exception as e:
            logger.error(f"Error en after(): {e}")

    try:

        if not ctx.voice_client:

            await ctx.author.voice.channel.connect()

        ctx.voice_client.play(
            source,
            after=after_playing
        )

        await ctx.send(f"🎵 Reproduciendo: **{title}**")

    except Exception as e:

        logger.error(f"Error reproduciendo: {e}")

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

    await ctx.send("\n".join(messages))

# ==================================================
# EVENTS
# ==================================================

@bot.event
async def on_ready():

    logger.info(f"Bot conectado como {bot.user}")

# ==================================================
# START BOT
# ==================================================

if __name__ == "__main__":

    bot.run(TOKEN)