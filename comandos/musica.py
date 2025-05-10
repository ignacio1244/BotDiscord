import asyncio
import discord

import yt_dlp as youtube_dl
import os
from discord.ext import commands

# Opciones para youtube_dl
ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

ffmpeg_options = {
    'options': '-vn'
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        try:
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

            if 'entries' in data:
                # Tomar el primer elemento de una playlist
                data = data['entries'][0]

            filename = data['url'] if stream else ytdl.prepare_filename(data)
            try:
                # Intenta encontrar FFmpeg automáticamente
                return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)
            except Exception as e:
                print(f"Error al crear FFmpegPCMAudio: {e}")
                # Intenta con una ruta explícita a FFmpeg
                ffmpeg_path = "C:/ffmpeg/bin/ffmpeg.exe"  # Ajusta esta ruta
                return cls(discord.FFmpegPCMAudio(filename, executable=ffmpeg_path, **ffmpeg_options), data=data)
        except Exception as e:
            print(f"Error en from_url: {e}")
            raise e

class Musica(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.queue = {}
        self.now_playing = {}

    @commands.command(name="unirse", aliases=["join"])
    async def unirse(self, ctx):
        """Hace que el bot se una al canal de voz"""
        if ctx.author.voice is None:
            await ctx.send("❌ Debes estar en un canal de voz para usar este comando.")
            return

        channel = ctx.author.voice.channel
        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()
        
        await ctx.send(f"✅ Me he unido a {channel.name}")

    @commands.command(name="salir", aliases=["leave", "disconnect"])
    async def salir(self, ctx):
        """Hace que el bot salga del canal de voz"""
        if ctx.voice_client is None:
            await ctx.send("❌ No estoy conectado a ningún canal de voz.")
            return
        
        await ctx.voice_client.disconnect()
        await ctx.send("👋 He salido del canal de voz")
        
        # Limpiar la cola de reproducción
        guild_id = str(ctx.guild.id)
        if guild_id in self.queue:
            self.queue[guild_id] = []
        if guild_id in self.now_playing:
            self.now_playing[guild_id] = None

    @commands.command(name="reproducir", aliases=["play", "p"])
    async def reproducir(self, ctx, *, url):
        """Reproduce una canción desde YouTube"""
        if ctx.author.voice is None:
            await ctx.send("❌ Debes estar en un canal de voz para usar este comando.")
            return
            
        # Unirse al canal si no está ya
        if ctx.voice_client is None:
            channel = ctx.author.voice.channel
            await channel.connect()
            
        guild_id = str(ctx.guild.id)
        
        # Inicializar la cola si no existe
        if guild_id not in self.queue:
            self.queue[guild_id] = []
            
        # Mensaje de carga
        mensaje = await ctx.send(f"🔍 Buscando `{url}`...")
            
        try:
            # Extraer información sin descargar
            loop = asyncio.get_event_loop()
            data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=False))
            
            if 'entries' in data:
                # Es una playlist
                if len(data['entries']) > 1:
                    await mensaje.edit(content=f"⚠️ Las playlists no están soportadas. Reproduciendo solo el primer video.")
                data = data['entries'][0]
                
            # Añadir a la cola
            self.queue[guild_id].append({
                'url': url,
                'title': data['title'],
                'requester': ctx.author.display_name
            })
            
            await mensaje.edit(content=f"✅ Añadido a la cola: **{data['title']}**")
            
            # Si no está reproduciendo nada, iniciar reproducción
            if not ctx.voice_client.is_playing() and len(self.queue[guild_id]) == 1:
                await self.play_next(ctx)
                
        except Exception as e:
            await mensaje.edit(content=f"❌ Error: {str(e)}")

    @commands.command(name="pausa", aliases=["stop", "s"])
    async def pausa(self, ctx):
        """Pausa la reproducción actual"""
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send("❌ No hay nada reproduciéndose actualmente.")
            return
            
        ctx.voice_client.pause()
        await ctx.send("⏸️ Reproducción pausada")

    @commands.command(name="continuar", aliases=["resume"])
    async def continuar(self, ctx):
        """Continúa la reproducción pausada"""
        if ctx.voice_client is None:
            await ctx.send("❌ No estoy conectado a ningún canal de voz.")
            return
            
        if not ctx.voice_client.is_paused():
            await ctx.send("❌ La reproducción no está pausada.")
            return
            
        ctx.voice_client.resume()
        await ctx.send("▶️ Reproducción continuada")

    @commands.command(name="saltar", aliases=["skip"])
    async def saltar(self, ctx):
        """Salta a la siguiente canción en la cola"""
        if ctx.voice_client is None or not ctx.voice_client.is_playing():
            await ctx.send("❌ No hay nada reproduciéndose actualmente.")
            return
            
        ctx.voice_client.stop()
        await ctx.send("⏭️ Saltando a la siguiente canción...")

    @commands.command(name="cola", aliases=["queue", "q"])
    async def cola(self, ctx):
        """Muestra la cola de reproducción actual"""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.queue or not self.queue[guild_id]:
            await ctx.send("📭 La cola de reproducción está vacía.")
            return
            
        embed = discord.Embed(
            title="🎵 Cola de reproducción",
            description="Lista de canciones en cola:",
            color=discord.Color.blue()
        )
        
        # Añadir canción actual
        if guild_id in self.now_playing and self.now_playing[guild_id]:
            embed.add_field(
                name="🎧 Reproduciendo ahora:",
                value=f"**{self.now_playing[guild_id]['title']}**\nSolicitada por: {self.now_playing[guild_id]['requester']}",
                inline=False
            )
        
        # Añadir canciones en cola
        for i, song in enumerate(self.queue[guild_id], 1):
            embed.add_field(
                name=f"{i}. {song['title']}",
                value=f"Solicitada por: {song['requester']}",
                inline=False
            )
            
            # Limitar a 10 canciones para no sobrecargar el embed
            if i >= 10:
                remaining = len(self.queue[guild_id]) - 10
                if remaining > 0:
                    embed.set_footer(text=f"Y {remaining} canciones más...")
                break
                
        await ctx.send(embed=embed)

    @commands.command(name="limpiar", aliases=["clear"])
    async def limpiar(self, ctx):
        """Limpia la cola de reproducción"""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.queue or not self.queue[guild_id]:
            await ctx.send("📭 La cola ya está vacía.")
            return
            
        self.queue[guild_id] = []
        await ctx.send("🧹 Cola de reproducción limpiada.")

    async def play_next(self, ctx):
        """Reproduce la siguiente canción en la cola"""
        guild_id = str(ctx.guild.id)
        
        if guild_id not in self.queue or not self.queue[guild_id]:
            if guild_id in self.now_playing:
                self.now_playing[guild_id] = None
            return
            
        # Obtener la siguiente canción
        next_song = self.queue[guild_id].pop(0)
        self.now_playing[guild_id] = next_song
        
        try:
            # Reproducir la canción
            player = await YTDLSource.from_url(next_song['url'], loop=self.bot.loop, stream=True)
            
            # Verificar que el bot sigue conectado
            if not ctx.voice_client or not ctx.voice_client.is_connected():
                await ctx.send("❌ El bot se desconectó del canal de voz.")
                return
                
            ctx.voice_client.play(
                player, 
                after=lambda e: asyncio.run_coroutine_threadsafe(
                    self.song_finished(ctx, e), self.bot.loop
                )
            )
            
            # Enviar mensaje
            embed = discord.Embed(
                title="🎵 Reproduciendo ahora",
                description=f"**{player.title}**",
                color=discord.Color.green()
            )
            embed.add_field(name="Solicitada por", value=next_song['requester'], inline=True)
            
            await ctx.send(embed=embed)
            
        except Exception as e:
            error_msg = f"❌ Error al reproducir: {str(e)}"
            print(error_msg)
            await ctx.send(error_msg)
            # Intentar con la siguiente canción
            await self.play_next(ctx)

    async def song_finished(self, ctx, error):
        """Callback cuando termina una canción"""
        if error:
            print(f"Error en la reproducción: {error}")
            
        # Reproducir la siguiente canción
        await self.play_next(ctx)

async def setup(bot):
    await bot.add_cog(Musica(bot))
    # Al inicio del archivo

