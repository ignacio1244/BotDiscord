import discord
import random
import json
import os
import asyncio
import aiohttp
from discord.ext import commands
from datetime import datetime, timedelta

class Wordle(commands.Cog):
    """Cog para el juego de Wordle"""
    
    def __init__(self, bot):
        self.bot = bot
        self.canal_wordle = os.getenv("CANAL_WORDLE_ID", None)
        if self.canal_wordle:
            try:
                self.canal_wordle = int(self.canal_wordle)
            except ValueError:
                self.canal_wordle = None
                
        self.juegos_activos = {}
        self.cooldowns = {}
        self.palabras = self._cargar_palabras_base()
        self.teclado = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Ñ"],
            ["Z", "X", "C", "V", "B", "N", "M"]
        ]
    
    def _cargar_palabras_base(self):
        """Carga la lista de palabras base para el juego"""
        ruta_json = os.path.join("utils", "palabras_wordle.json")
        
        try:
            # Intentar cargar palabras desde el archivo JSON
            with open(ruta_json, 'r', encoding='utf-8') as archivo:
                palabras_json = json.load(archivo)
                palabras_base = palabras_json.get("palabras", [])
                
            if not palabras_base:
                raise FileNotFoundError("El archivo JSON existe pero no contiene palabras")
                
        except (FileNotFoundError, json.JSONDecodeError):
            # Si el archivo no existe o está mal formateado, usar la lista predeterminada
            # y crear el archivo JSON para uso futuro
            palabras_base = [
                    "GATOS",
                    "PERRO",

        ]

        return [palabra for palabra in palabras_base if len(palabra) == 5]
    
       
    @commands.command(name="palabras_total")
    async def palabras_total(self, ctx):
        """Muestra el total de palabras disponibles para el juego"""
        await ctx.send(f"📊 Actualmente hay **{len(self.palabras)}** palabras disponibles para el juego Wordle.")
        
    @commands.command(name="wordle", aliases=["palabra"])
    async def wordle(self, ctx):
        """
        Inicia un juego de Wordle
        
        Adivina la palabra de 5 letras en 6 intentos.
        🟩 = Letra correcta en posición correcta
        🟨 = Letra correcta en posición incorrecta
        ⬛ = Letra incorrecta
        """
        
        if self.canal_wordle and ctx.channel.id != self.canal_wordle:
            return await ctx.send(f"⚠️ Este comando solo se puede usar en el canal <#{self.canal_wordle}>")
            
        usuario_id = str(ctx.author.id)
        if usuario_id in self.cooldowns:
            tiempo_restante = self.cooldowns[usuario_id] - datetime.now()
            if tiempo_restante.total_seconds() > 0:
                minutos = int(tiempo_restante.total_seconds() // 60)
                segundos = int(tiempo_restante.total_seconds() % 60)
                return await ctx.send(f"⏳ Debes esperar {minutos}m {segundos}s para jugar de nuevo.")
        
        if usuario_id in self.juegos_activos:
            return await ctx.send("⚠️ Ya tienes un juego de Wordle activo. Termínalo antes de iniciar uno nuevo.")
            
        palabra = random.choice(self.palabras).upper()
        
        self.juegos_activos[usuario_id] = {
            "palabra": palabra,
            "intentos": 0,
            "max_intentos": 6,
            "adivinado": False,
            "mensaje": None,
            "canal": ctx.channel.id
        }
        
        embed = discord.Embed(
            title="🎮 Wordle",
            description=f"¡Hola {ctx.author.mention}! He pensado una palabra de 5 letras.\n"
                       f"Tienes 6 intentos para adivinarla.\n\n"
                       f"Escribe tu intento en este canal.\n"
                       f"🟩 = Letra correcta en posición correcta\n"
                       f"🟨 = Letra correcta en posición incorrecta\n"
                       f"⬛ = Letra incorrecta\n\n"
                       f"Para rendirte, escribe `!rendirse`",
            color=discord.Color.blue()
        )
        embed.set_footer(text="Tienes 2 minutos para cada intento")
        
        mensaje = await ctx.send(embed=embed)
        self.juegos_activos[usuario_id]["mensaje"] = mensaje.id
        
        await self._jugar_wordle(ctx, usuario_id)
        
    @commands.command(name="rendirse", aliases=["surrender", "abandonar"])
    async def rendirse(self, ctx):
        """Abandona el juego de Wordle actual"""
        usuario_id = str(ctx.author.id)
        
        if usuario_id not in self.juegos_activos:
            return await ctx.send("⚠️ No tienes ningún juego de Wordle activo.")
            
        palabra = self.juegos_activos[usuario_id]["palabra"]
        await ctx.send(f"😔 Te has rendido. La palabra era: **{palabra}**")
        
        del self.juegos_activos[usuario_id]
        
    async def _jugar_wordle(self, ctx, usuario_id):
        """Maneja la lógica del juego de Wordle"""
        juego = self.juegos_activos[usuario_id]
        
        juego["letras_usadas"] = set()
        juego["estado_letras"] = {} 
        
        while juego["intentos"] < juego["max_intentos"] and not juego["adivinado"]:
            try:
                def check(m):
                    return m.author.id == ctx.author.id and m.channel.id == ctx.channel.id
                        
                mensaje = await self.bot.wait_for("message", check=check, timeout=120)
                
                if mensaje.content.lower() in ["!rendirse", "!surrender", "!abandonar"]:
                    await ctx.send(f"😔 Te has rendido. La palabra era: **{juego['palabra']}**")
                    del self.juegos_activos[usuario_id]
                    return
                
                intento = mensaje.content.upper()
                if len(intento) != 5:
                    respuesta = await ctx.send("⚠️ La palabra debe tener exactamente 5 letras.", delete_after=5)
                    continue
                        
                if not intento.isalpha():
                    respuesta = await ctx.send("⚠️ La palabra solo debe contener letras.", delete_after=5)
                    continue
                
                juego["intentos"] += 1
                resultado = self._evaluar_intento(intento, juego["palabra"])
        
                for i, letra in enumerate(intento):
                    juego["letras_usadas"].add(letra)
                    
                    estado_actual = juego["estado_letras"].get(letra, "⬛")
                    if resultado[i] == "🟩" or estado_actual == "🟩":
                        juego["estado_letras"][letra] = "🟩"
                    elif resultado[i] == "🟨" and estado_actual != "🟩":
                        juego["estado_letras"][letra] = "🟨"
                    elif estado_actual not in ["🟩", "🟨"]:
                        juego["estado_letras"][letra] = "⬛"
                                 
                embed = discord.Embed(
                    title=f"🎮 Wordle - Intento {juego['intentos']}/{juego['max_intentos']}",
                    description=self._generar_historial(juego, intento, resultado),
                    color=discord.Color.blue()
                )
                
                embed.add_field(
                    name="⌨️ Teclado",
                    value=self._generar_teclado(juego["estado_letras"]),
                    inline=False
                )
                
                letras_ordenadas = sorted(list(juego["letras_usadas"]))
                embed.add_field(
                    name="🔤 Letras usadas",
                    value=" ".join(letras_ordenadas),
                    inline=False
                )
                
                if intento == juego["palabra"] or juego["intentos"] >= juego["max_intentos"]:
                    if intento == juego["palabra"]:
                        juego["adivinado"] = True
                        
                        resultado_visual = ""
                        for r in resultado:
                            resultado_visual += r
                        
                        embed_final = discord.Embed(
                            title="🎮 Wordle - ¡Juego Terminado!",
                            description=f"🎉 ¡Felicidades {ctx.author.mention}! Has adivinado la palabra.\n\n"
                                       f"**{juego['palabra']}**\n\n"
                                       f"{resultado_visual}\n\n"
                                       f"Lo lograste en {juego['intentos']} intentos.",
                            color=discord.Color.green()
                        )
                        
                        self.cooldowns[usuario_id] = datetime.now() + timedelta(hours=1)
                    else:
                        embed_final = discord.Embed(
                            title="🎮 Wordle - ¡Juego Terminado!",
                            description=f"😔 Has agotado tus intentos.\n\n"
                                       f"La palabra era: **{juego['palabra']}**",
                            color=discord.Color.red()
                        )
                        
                        self.cooldowns[usuario_id] = datetime.now() + timedelta(minutes=30)
                    
                    await ctx.send(embed=embed_final)
                    
                    del self.juegos_activos[usuario_id]
                    return
                
                mensaje_progreso = await ctx.send(embed=embed)
                        
            except asyncio.TimeoutError:
                await ctx.send(f"⏱️ Se agotó el tiempo. El juego ha terminado. La palabra era **{juego['palabra']}**.")
                del self.juegos_activos[usuario_id]
                return

    def _evaluar_intento(self, intento, palabra):
        """Evalúa el intento del usuario y devuelve el resultado"""
        resultado = ["⬛"] * 5  
        letras_restantes = {}
        
        for letra in palabra:
            if letra in letras_restantes:
                letras_restantes[letra] += 1
            else:
                letras_restantes[letra] = 1
        
        for i in range(5):
            if intento[i] == palabra[i]:
                resultado[i] = "🟩"
                letras_restantes[intento[i]] -= 1
        
        for i in range(5):
            if resultado[i] == "⬛" and intento[i] in letras_restantes and letras_restantes[intento[i]] > 0:
                resultado[i] = "🟨"
                letras_restantes[intento[i]] -= 1
                
        return resultado
    
    def _generar_teclado(self, estado_letras):
        """Genera una representación visual del teclado con el estado de las letras"""
        teclado = [
            ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
            ["A", "S", "D", "F", "G", "H", "J", "K", "L", "Ñ"],
            ["Z", "X", "C", "V", "B", "N", "M"]
        ]
        
        teclado_visual = ""
        
        for fila in teclado:
            for letra in fila:
                estado = estado_letras.get(letra, "⬜")
                teclado_visual += f"{letra}:{estado} "
            teclado_visual += "\n"
            
        return teclado_visual
    
    def _generar_historial(self, juego, intento_actual, resultado_actual):
        """Genera el historial de intentos para mostrar en el embed"""
        historial = ""
        
        historial += f"Intento {juego['intentos']}: {intento_actual}\n"
        historial += "".join(resultado_actual) + "\n\n"
        
        return historial

async def setup(bot):
    await bot.add_cog(Wordle(bot))