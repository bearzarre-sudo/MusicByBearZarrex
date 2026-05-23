# Discord Music Bot — Railway Ready

## ✨ Features

- 🎵 YouTube audio streaming
- 📝 Music queues with skip functionality
- 📂 Playlist loading
- 🔊 Voice channel auto-join
- ⏸️ Queue management
- 🔌 Stable FFmpeg reconnection

---

## 📋 Requirements

- Python 3.11+
- discord.py[voice] >= 2.3.2
- yt-dlp >= 2024.1.1
- FFmpeg (instalado automáticamente en Railway)
- PyNaCl >= 1.5.0

---

## 🚀 Deployment on Railway

### Environment Variables

Set in Railway dashboard:

```
DISCORD_TOKEN=tu_token_aqui
```

### Configuration

El bot usa `nixpacks.toml` para instalación automática:

```toml
[phases.setup]
nixPkgs = ["python311", "ffmpeg", "libopus"]
```

FFmpeg se instala **automáticamente** en Railway.

---

## 🔧 Commands

| Command | Usage | Description |
|---------|-------|-------------|
| `!play` | `!play <song_name_or_url>` | Reproduce una canción |
| `!playlist` | `!playlist <youtube_playlist_url>` | Carga una playlist |
| `!queue` | `!queue` | Muestra las 10 primeras canciones |
| `!skip` | `!skip` | Salta a la siguiente canción |
| `!join` | `!join` | Conecta al canal de voz del usuario |
| `!leave` | `!leave` | Desconecta del canal de voz |
| `!test` | `!test` | Verifica el estado del bot |

---

## 📊 Troubleshooting

### ❌ "Bot no reproduce música en Railway"

**Causas posibles:**

1. **FFmpeg no está disponible**
   - ✅ SOLUCIONADO: Se instala automáticamente vía nixpacks.toml
   - Verificar logs en Railway: debe mostrar "✅ FFmpeg está disponible"

2. **DISCORD_TOKEN no configurado**
   - Ve a Railway → Variables → Asegúrate de que DISCORD_TOKEN está presente

3. **Problemas de conexión con YouTube**
   - yt-dlp necesita acceso a internet
   - Railway permite conexiones salientes por defecto

4. **Errores de audio en el canal de voz**
   - Asegúrate de que PyNaCl está instalado (se incluye en requirements.txt)

### 🔍 Debug: Comandos útiles

```
!test          # Verifica que todos los componentes están listos
!join          # Conecta manualmente al canal de voz
!play <URL>    # Prueba con una URL de YouTube directa
```

---

## 🔄 Actualización en Railway

1. Haz push a tu rama (el webhook de GitHub triggea auto-deploy)
2. Railway detectará cambios en:
   - `discord_bot.py`
   - `requirements.txt`
   - `nixpacks.toml`
3. Reinstalará dependencias automáticamente

---

## 📝 Local Development

### Setup

```bash
python -m venv venv
source venv/Scripts/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Run

```bash
export DISCORD_TOKEN="your_token"  # Linux/Mac
set DISCORD_TOKEN=your_token       # Windows CMD
python discord_bot.py
```

---

## 🐛 Known Issues & Solutions

### ❌ "The authenticity of host 'github.com' can't be established"
- Normal en primera conexión SSH, railway lo resuelve automáticamente

### ❌ "FFmpeg: command not found"
- Verificar que `nixpacks.toml` tiene `"ffmpeg"` en nixPkgs
- Esperar a que Railway termine de buildear (puede tomar 2-3 minutos)

### ❌ "No audio after !play command"
- Ejecutar `!test` para verificar estado
- Revisar logs en Railway para mensajes de error
- Asegúrate de estar en un canal de voz primero

---

## 🤝 Contributing

Para reportar bugs, crea un issue con logs de Railway.

---

## 📄 License

MIT

---

The bot streams audio directly from YouTube using yt-dlp and FFmpeg.

This is important for Railway compatibility.

---

# Current Architecture

## Main file

```bash
discord_bot.py
