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
        self.ruta_estadisticas = os.path.join("utils", "estadisticas.json")
    
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
    
    def _cargar_estadisticas(self):
        """Carga las estadísticas de los usuarios desde el archivo JSON"""
        try:
            with open(self.ruta_estadisticas, 'r', encoding='utf-8') as archivo:
                return json.load(archivo)
        except (FileNotFoundError, json.JSONDecodeError):
            return {}
            
    def _guardar_estadisticas(self, estadisticas):
        """Guarda las estadísticas de los usuarios en el archivo JSON"""
        with open(self.ruta_estadisticas, 'w', encoding='utf-8') as archivo:
            json.dump(estadisticas, archivo, indent=4, ensure_ascii=False)
            
    def _actualizar_estadisticas(self, usuario_id, ganado, intentos):
        """Actualiza las estadísticas del usuario"""
        estadisticas = self._cargar_estadisticas()
        
        # Convertir ID a string para usarlo como clave en el JSON
        usuario_id = str(usuario_id)
        
        # Inicializar estadísticas del usuario si no existen
        if usuario_id not in estadisticas:
            estadisticas[usuario_id] = {}
            
        # Inicializar estadísticas de wordle si no existen
        if "wordle" not in estadisticas[usuario_id]:
            estadisticas[usuario_id]["wordle"] = {
                "partidas_jugadas": 0,
                "partidas_ganadas": 0,
                "partidas_perdidas": 0,
                "intentos_totales": 0,
                "historial_intentos": []
            }
            
        # Actualizar estadísticas
        estadisticas[usuario_id]["wordle"]["partidas_jugadas"] += 1
        
        if ganado:
            estadisticas[usuario_id]["wordle"]["partidas_ganadas"] += 1
            estadisticas[usuario_id]["wordle"]["intentos_totales"] += intentos
            estadisticas[usuario_id]["wordle"]["historial_intentos"].append(intentos)
        else:
            estadisticas[usuario_id]["wordle"]["partidas_perdidas"] += 1
            
        # Guardar estadísticas actualizadas
        self._guardar_estadisticas(estadisticas)
        
        return estadisticas[usuario_id]["wordle"]
       
    @commands.command(name="palabras_total")
    async def palabras_total(self, ctx):
        """Muestra el total de palabras disponibles para el juego"""
        await ctx.send(f"📊 Actualmente hay **{len(self.palabras)}** palabras disponibles para el juego Wordle.")
        
    @commands.command(name="wordle_stats", aliases=["wstats"])
    async def wordle_stats(self, ctx, usuario: discord.Member = None):
        """Muestra las estadísticas de Wordle de un usuario"""
        if usuario is None:
            usuario = ctx.author
            
        estadisticas = self._cargar_estadisticas()
        usuario_id = str(usuario.id)
        
        if usuario_id not in estadisticas or "wordle" not in estadisticas[usuario_id]:
            return await ctx.send(f"⚠️ {usuario.display_name} aún no tiene estadísticas de Wordle.")
            
        stats = estadisticas[usuario_id]["wordle"]
        partidas_jugadas = stats["partidas_jugadas"]
        partidas_ganadas = stats["partidas_ganadas"]
        partidas_perdidas = stats["partidas_perdidas"]
        
        # Calcular porcentaje de victorias
        porcentaje_victorias = (partidas_ganadas / partidas_jugadas * 100) if partidas_jugadas > 0 else 0
        
        # Calcular promedio de intentos
        promedio_intentos = (stats["intentos_totales"] / partidas_ganadas) if partidas_ganadas > 0 else 0
        
        # Crear embed con estadísticas
        embed = discord.Embed(
            title=f"📊 Estadísticas de Wordle de {usuario.display_name}",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="🎮 Partidas jugadas", value=str(partidas_jugadas), inline=True)
        embed.add_field(name="🏆 Victorias", value=str(partidas_ganadas), inline=True)
        embed.add_field(name="❌ Derrotas", value=str(partidas_perdidas), inline=True)
        embed.add_field(name="📈 % de victorias", value=f"{porcentaje_victorias:.1f}%", inline=True)
        embed.add_field(name="🔢 Promedio de intentos", value=f"{promedio_intentos:.1f}", inline=True)
        
        # Mostrar distribución de intentos si hay victorias
        if partidas_ganadas > 0 and "historial_intentos" in stats:
            distribucion = {}
            for intento in stats["historial_intentos"]:
                distribucion[intento] = distribucion.get(intento, 0) + 1
                
            distribucion_texto = ""
            for i in range(1, 7):
                cantidad = distribucion.get(i, 0)
                barras = "█" * min(cantidad, 15)
                distribucion_texto += f"{i}: {barras} {cantidad}\n"
                
            embed.add_field(name="📊 Distribución de intentos", value=distribucion_texto, inline=False)
        
        await ctx.send(embed=embed)
        
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
        
        # Actualizar estadísticas (partida perdida)
        self._actualizar_estadisticas(ctx.author.id, False, 0)
        
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
                    # Actualizar estadísticas (partida perdida)
                    self._actualizar_estadisticas(ctx.author.id, False, 0)
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
                        
                        # Actualizar estadísticas (partida ganada)
                        stats = self._actualizar_estadisticas(ctx.author.id, True, juego["intentos"])
                        
                        embed_final = discord.Embed(
                            title="🎮 Wordle - ¡Juego Terminado!",
                            description=f"🎉 ¡Felicidades {ctx.author.mention}! Has adivinado la palabra.\n\n"
                                       f"**{juego['palabra']}**\n\n"
                                       f"{resultado_visual}\n\n"
                                       f"Lo lograste en {juego['intentos']} intentos.",
                            color=discord.Color.green()
                        )
                        
                        # Añadir estadísticas al embed
                        embed_final.add_field(
                            name="📊 Tus estadísticas",
                            value=f"🎮 Partidas: {stats['partidas_jugadas']}\n"
                                 f"🏆 Victorias: {stats['partidas_ganadas']}\n"
                                 f"📈 Promedio: {stats['intentos_totales']/stats['partidas_ganadas']:.1f} intentos",
                            inline=False
                        )
                        
                        self.cooldowns[usuario_id] = datetime.now() + timedelta(hours=1)
                    else:
                        # Actualizar estadísticas (partida perdida)
                        stats = self._actualizar_estadisticas(ctx.author.id, False, 0)
                        
                        embed_final = discord.Embed(
                            title="🎮 Wordle - ¡Juego Terminado!",
                            description=f"😔 Has agotado tus intentos.\n\n"
                                       f"La palabra era: **{juego['palabra']}**",
                            color=discord.Color.red()
                        )
                        
                        # Añadir estadísticas al embed
                        embed_final.add_field(
                            name="📊 Tus estadísticas",
                            value=f"🎮 Partidas: {stats['partidas_jugadas']}\n"
                                 f"❌ Derrotas: {stats['partidas_perdidas']}\n"
                                 f"🏆 Victorias: {stats['partidas_ganadas']}",
                            inline=False
                        )
                        
                        self.cooldowns[usuario_id] = datetime.now() + timedelta(minutes=30)
                    
                    await ctx.send(embed=embed_final)
                    
                    del self.juegos_activos[usuario_id]
                    return
                
                mensaje_progreso = await ctx.send(embed=embed)
                        
            except asyncio.TimeoutError:
                await ctx.send(f"⏱️ Se agotó el tiempo. El juego ha terminado. La palabra era **{juego['palabra']}**.")
                # Actualizar estadísticas (partida perdida)
                self._actualizar_estadisticas(ctx.author.id, False, 0)
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