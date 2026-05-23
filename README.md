# Discord Music Bot — Railway Ready

## Overview

This project is a Discord Music Bot built with:

- Python 3.11+
- discord.py
- yt-dlp
- FFmpeg
- PyNaCl

The bot is optimized for deployment on Railway and supports:

- YouTube audio streaming
- Music queues
- Playlist loading
- Voice channel auto join
- Skip songs
- Queue management
- Stable FFmpeg reconnect handling

The architecture was simplified for cloud deployment stability.

---

# Current Stack

## Backend

- Python 3.11
- discord.py[voice]
- yt-dlp
- FFmpeg
- PyNaCl

## Hosting

- Railway

## Deployment

- Nixpacks
- Procfile worker deployment

---

# Important Notes

## The bot DOES NOT download files

The bot streams audio directly from YouTube using yt-dlp and FFmpeg.

This is important for Railway compatibility.

---

# Current Architecture

## Main file

```bash
discord_bot.py
