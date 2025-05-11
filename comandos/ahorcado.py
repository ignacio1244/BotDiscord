import discord
import random
import asyncio
import json
import os
import time
from discord.ext import commands
from comandos.estadisticas import Estadisticas  # Añadir esta importación
from comandos.casino import casino_manager  # Importar el casino_manager

class Ahorcado(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {}
        self.ultimo_juego = {}
        self.tiempo_espera = 60  # Tiempo de espera en segundos entre partidas
        self.stats_manager = Estadisticas(bot)  # Inicializar el gestor de estadísticas
        
        # Cargar palabras desde el archivo JSON
        self.palabras = self.cargar_palabras()
        
        # Configuración de dificultades
        self.dificultades = {
            'facil': {
                'intentos': 8,
                'multiplicador': 1.2,
                'emoji': '🟢',
                'color': discord.Color.green()
            },
            'normal': {
                'intentos': 6,
                'multiplicador': 2.0,
                'emoji': '🟡',
                'color': discord.Color.gold()
            },
            'dificil': {
                'intentos': 4,
                'multiplicador': 3.0,
                'emoji': '🔴',
                'color': discord.Color.red()
            }
        }
        
        # Imágenes del ahorcado (ASCII art)
        self.estados_ahorcado = [
            '''```
  +---+
  |   |
      |
      |
      |
      |
=========```''',
            '''```
  +---+
  |   |
  O   |
      |
      |
      |
=========```''',
            '''```
  +---+
  |   |
  O   |
  |   |
      |
      |
=========```''',
            '''```
  +---+
  |   |
  O   |
 /|   |
      |
      |
=========```''',
            '''```
  +---+
  |   |
  O   |
 /|\\  |
      |
      |
=========```''',
            '''```
  +---+
  |   |
  O   |
 /|\\  |
 /    |
      |
=========```''',
            '''```
  +---+
  |   |
  O   |
 /|\\  |
 / \\  |
      |
=========```'''
        ]

    def cargar_palabras(self):
        """Carga las palabras desde el archivo JSON"""
        # Ruta correcta al archivo JSON en la carpeta utils
        ruta_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils', 'palabras_ahorcado.json')
        
        # Si el archivo no existe, crear uno con palabras predeterminadas
        if not os.path.exists(ruta_json):
            # Asegurarse de que la carpeta utils existe
            os.makedirs(os.path.dirname(ruta_json), exist_ok=True)
            
            palabras_default = {
                'facil': [
                    'sol', 'mar', 'pan', 'luz', 'paz', 
                    'flor', 'casa', 'mesa', 'gato', 'perro',
                    'amor', 'vida', 'azul', 'rojo', 'nube'
                ],
                'normal': [
                    'samuel', 'activity', 'banana', 'school', 'python', 
                    'discord', 'teclado', 'monitor', 'raton', 'internet',
                    'variable', 'funcion', 'clase', 'objeto', 'programa'
                ],
                'dificil': [
                    'programacion', 'videojuego', 'computadora', 'algoritmo',
                    'inteligencia', 'desarrollo', 'aplicacion', 'tecnologia',
                    'experiencia', 'comunicacion', 'informacion', 'matematicas',
                    'universidad', 'conocimiento', 'aprendizaje'
                ]
            }
            
            # Guardar el diccionario predeterminado en un archivo JSON
            with open(ruta_json, 'w', encoding='utf-8') as f:
                json.dump(palabras_default, f, ensure_ascii=False, indent=2)
            
            return palabras_default
        
        # Si el archivo existe, cargar las palabras desde él
        try:
            with open(ruta_json, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error al cargar palabras: {e}")
            # En caso de error, devolver un diccionario vacío con las categorías
            return {'facil': [], 'normal': [], 'dificil': []}

    @commands.command(name="agregar_palabra", aliases=["add_word"])
    @commands.has_permissions(administrator=True)
    async def agregar_palabra(self, ctx, palabra: str, dificultad: str = "normal"):
        """Agrega una nueva palabra al juego del ahorcado (solo administradores)
        
        Parámetros:
        - palabra: La palabra a agregar
        - dificultad: "facil", "normal" o "dificil" (opcional, por defecto "normal")
        """
        # Verificar si la dificultad es válida
        dificultad = dificultad.lower()
        if dificultad not in self.dificultades:
            await ctx.send(f"❌ Dificultad no válida. Las opciones son: `facil`, `normal` o `dificil`.")
            return
        
        # Verificar si la palabra ya existe en esa dificultad
        if palabra.lower() in [p.lower() for p in self.palabras[dificultad]]:
            await ctx.send(f"❌ La palabra '{palabra}' ya existe en la dificultad {dificultad}.")
            return
        
        # Agregar la palabra
        self.palabras[dificultad].append(palabra.lower())
        
        # Guardar las palabras actualizadas en el archivo JSON (ruta correcta)
        ruta_json = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'utils', 'palabras_ahorcado.json')
        with open(ruta_json, 'w', encoding='utf-8') as f:
            json.dump(self.palabras, f, ensure_ascii=False, indent=2)
        
        await ctx.send(f"✅ Palabra '{palabra}' agregada correctamente a la dificultad {dificultad}.")

    @commands.command(name="ahorcado", aliases=["hangman"])
    async def ahorcado(self, ctx, apuesta: int = None, dificultad: str = "normal"):
        """Inicia un juego del ahorcado con apuesta y dificultad opcional
        
        Parámetros:
        - apuesta: Cantidad de monedas a apostar
        - dificultad: "facil", "normal" o "dificil" (opcional, por defecto "normal")
        """
        # Verificar si ya hay un juego en este canal
        if ctx.channel.id in self.games:
            await ctx.send("❌ Ya hay un juego de ahorcado activo en este canal.")
            return
        
        # Verificar el tiempo de espera entre partidas
        usuario_id = str(ctx.author.id)
        tiempo_actual = time.time()
        
        if usuario_id in self.ultimo_juego:
            tiempo_transcurrido = tiempo_actual - self.ultimo_juego[usuario_id]
            if tiempo_transcurrido < self.tiempo_espera:
                tiempo_restante = int(self.tiempo_espera - tiempo_transcurrido)
                minutos = tiempo_restante // 60
                segundos = tiempo_restante % 60
                await ctx.send(f"⏳ Debes esperar {minutos} minutos y {segundos} segundos antes de iniciar otra partida.")
                return
            
        # Verificar si se proporcionó una apuesta
        if apuesta is None:
            await ctx.send("❌ Debes especificar una cantidad para apostar. Ejemplo: `!ahorcado 100 facil`")
            return
            
        # Verificar si la apuesta es válida
        if apuesta <= 0:
            await ctx.send("❌ La apuesta debe ser mayor que 0.")
            return
            
        # Verificar si la dificultad es válida
        dificultad = dificultad.lower()
        if dificultad not in self.dificultades:
            await ctx.send(f"❌ Dificultad no válida. Las opciones son: `facil`, `normal` o `dificil`.")
            return
            
        # Verificar si el usuario tiene suficiente saldo
        usuario_id = str(ctx.author.id)
        saldo_actual = casino_manager.obtener_saldo(usuario_id)
        
        if saldo_actual < apuesta:
            await ctx.send(f"❌ No tienes suficiente saldo. Tu saldo actual es: {saldo_actual}")
            return
            
        # Descontar la apuesta
        nuevo_saldo = saldo_actual - apuesta
        casino_manager.actualizar_saldo(usuario_id, nuevo_saldo)
        
        # Obtener configuración de dificultad
        config_dificultad = self.dificultades[dificultad]
        max_intentos = config_dificultad['intentos']
        multiplicador = config_dificultad['multiplicador']
        
        # Iniciar el juego
        palabra = random.choice(self.palabras[dificultad]).upper()
        letras_adivinadas = []
        intentos_fallidos = 0
        
        # Guardar el estado del juego
        self.games[ctx.channel.id] = {
            'palabra': palabra,
            'letras_adivinadas': letras_adivinadas,
            'intentos_fallidos': intentos_fallidos,
            'max_intentos': max_intentos,
            'apuesta': apuesta,
            'jugador': ctx.author.id,
            'dificultad': dificultad,
            'multiplicador': multiplicador
        }
        
        # Registrar el tiempo de inicio de la partida
        self.ultimo_juego[usuario_id] = tiempo_actual
        
        # Mostrar el estado inicial
        await self.mostrar_estado(ctx)
        
        # Mensaje de inicio
        emoji_dificultad = config_dificultad['emoji']
        await ctx.send(f"🎮 **{ctx.author.display_name}** ha iniciado un juego de ahorcado {emoji_dificultad} **{dificultad.upper()}** apostando **{apuesta}** monedas.\n"
                      f"Tienes {max_intentos} intentos para adivinar la palabra. ¡Buena suerte!\n"
                      f"**Simplemente escribe una letra en el chat para adivinar.**")

    async def mostrar_estado(self, ctx):
        """Muestra el estado actual del juego"""
        # Obtener el ID del canal correctamente
        canal_id = ctx.id if hasattr(ctx, 'id') else ctx.channel.id
        
        game = self.games[canal_id]
        palabra = game['palabra']
        letras_adivinadas = game['letras_adivinadas']
        intentos_fallidos = game['intentos_fallidos']
        dificultad = game['dificultad']
        multiplicador = game['multiplicador']
        
        # Crear la representación de la palabra
        palabra_mostrada = ""
        for letra in palabra:
            if letra in letras_adivinadas:
                palabra_mostrada += letra + " "
            else:
                palabra_mostrada += "_ "
                
        # Obtener el color según la dificultad
        color = self.dificultades[dificultad]['color']
        emoji_dificultad = self.dificultades[dificultad]['emoji']
        
        # Crear el mensaje con el estado del juego
        embed = discord.Embed(
            title=f"🎮 Juego del Ahorcado - {emoji_dificultad} {dificultad.upper()}",
            color=color
        )
        
        # Añadir el dibujo del ahorcado PRIMERO
        embed.description = self.estados_ahorcado[intentos_fallidos]
        
        # Luego añadir los demás campos
        embed.add_field(name="Palabra", value=f"```{palabra_mostrada}```", inline=False)
        embed.add_field(name="Letras usadas", value=f"```{', '.join(sorted(letras_adivinadas)) if letras_adivinadas else 'Ninguna'}```", inline=False)
        embed.add_field(name="Intentos restantes", value=f"```{game['max_intentos'] - intentos_fallidos}```", inline=False)
        embed.add_field(name="Apuesta", value=f"```{game['apuesta']} monedas```", inline=False)
        embed.add_field(name="Multiplicador", value=f"```x{multiplicador}```", inline=False)
        
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        """Procesa los mensajes para el juego del ahorcado"""
        # Ignorar mensajes del bot
        if message.author.bot:
            return
            
        # Verificar si hay un juego activo en este canal
        if message.channel.id not in self.games:
            return
            
        # Verificar que el mensaje sea del jugador correcto
        if message.author.id != self.games[message.channel.id]['jugador']:
            return
            
        # Obtener el contenido del mensaje
        contenido = message.content.strip().upper()
        
        # Verificar que sea una sola letra
        if len(contenido) != 1 or not contenido.isalpha():
            return
            
        # Procesar la letra
        await self.procesar_letra(message.channel, contenido)

    async def procesar_letra(self, canal, letra):
        """Procesa una letra adivinada"""
        game = self.games[canal.id]
        palabra = game['palabra']
        
        # Verificar si la letra ya fue adivinada
        if letra in game['letras_adivinadas']:
            await canal.send(f"⚠️ Ya adivinaste la letra '{letra}'. Intenta con otra.")
            return
            
        # Agregar la letra a las letras adivinadas
        game['letras_adivinadas'].append(letra)
        
        # Verificar si la letra está en la palabra
        if letra in palabra:
            # Verificar si se completó la palabra
            palabra_completa = True
            for l in palabra:
                if l not in game['letras_adivinadas']:
                    palabra_completa = False
                    break
                    
            if palabra_completa:
                # El jugador ganó
                await self.finalizar_juego(canal, True)
            else:
                # Mostrar el estado actualizado
                await self.mostrar_estado(canal)
        else:
            # La letra no está en la palabra
            game['intentos_fallidos'] += 1
            
            # Verificar si se agotaron los intentos
            if game['intentos_fallidos'] >= game['max_intentos']:
                # El jugador perdió
                await self.finalizar_juego(canal, False)
            else:
                # Mostrar el estado actualizado
                await self.mostrar_estado(canal)

    async def finalizar_juego(self, canal, ganado):
        """Finaliza el juego actual"""
        game = self.games[canal.id]
        palabra = game['palabra']
        jugador_id = game['jugador']
        apuesta = game['apuesta']
        dificultad = game['dificultad']
        multiplicador = game['multiplicador']
        
        # Obtener el usuario
        jugador = self.bot.get_user(jugador_id)
        
        if ganado:
            # Calcular la ganancia
            ganancia = int(apuesta * multiplicador)
            
            # Actualizar el saldo
            saldo_actual = casino_manager.obtener_saldo(str(jugador_id))
            nuevo_saldo = saldo_actual + ganancia
            casino_manager.actualizar_saldo(str(jugador_id), nuevo_saldo)
            
            # Actualizar estadísticas - ganancia neta (ganancia - apuesta)
            ganancia_neta = ganancia - apuesta
            # Comentamos o eliminamos la línea que causa el error
            # self.stats_manager.registrar_victoria_ahorcado(jugador_id, ganancia_neta)
            
            # Crear el mensaje de victoria
            embed = discord.Embed(
                title="🎮 ¡Juego del Ahorcado - Victoria!",
                description=f"¡Felicidades {jugador.mention}! Has adivinado la palabra **{palabra}**.",
                color=self.dificultades[dificultad]['color']
            )
            
            embed.add_field(name="💰 Ganancia", value=f"{ganancia} monedas", inline=True)
            embed.add_field(name="💵 Nuevo saldo", value=f"{nuevo_saldo} monedas", inline=True)
            
        else:
            # Actualizar estadísticas
            # Comentamos o eliminamos la línea que causa el error
            # self.stats_manager.registrar_derrota_ahorcado(jugador_id, apuesta)
            
            # Crear el mensaje de derrota
            embed = discord.Embed(
                title="🎮 Juego del Ahorcado - Derrota",
                description=f"Lo siento {jugador.mention}, has perdido. La palabra era **{palabra}**.",
                color=discord.Color.red()
            )
            
            embed.add_field(name="💸 Pérdida", value=f"{apuesta} monedas", inline=True)
            
        # Eliminar el juego
        del self.games[canal.id]
        
        # Enviar el mensaje
        await canal.send(embed=embed)

    @commands.command(name="rendirse_ahorcado", aliases=["surrender_hangman"])
    async def rendirse(self, ctx):
        """Abandona el juego de ahorcado actual"""
        # Verificar si hay un juego activo en este canal
        if ctx.channel.id not in self.games:
            await ctx.send("❌ No hay ningún juego de ahorcado activo en este canal.")
            return
            
        game = self.games[ctx.channel.id]
        
        # Verificar si es el jugador quien se rinde
        if ctx.author.id != game['jugador']:
            await ctx.send("❌ Solo el jugador que inició el juego puede rendirse.")
            return
            
        # Mostrar la palabra
        dificultad = game['dificultad']
        emoji_dificultad = self.dificultades[dificultad]['emoji']
        
        await ctx.send(f"😔 Te has rendido en el juego {emoji_dificultad} **{dificultad.upper()}**. La palabra era: **{game['palabra']}**\n"
                      f"Has perdido tu apuesta de **{game['apuesta']}** monedas.")
        
        # Eliminar el juego
        del self.games[ctx.channel.id]
        
    @commands.command(name="tiempo_espera_ahorcado", aliases=["hangman_cooldown"])
    async def tiempo_espera(self, ctx):
        """Muestra el tiempo restante para poder jugar otra partida"""
        usuario_id = str(ctx.author.id)
        
        if usuario_id not in self.ultimo_juego:
            await ctx.send("✅ Puedes iniciar una partida de ahorcado ahora mismo.")
            return
            
        tiempo_actual = time.time()
        tiempo_transcurrido = tiempo_actual - self.ultimo_juego[usuario_id]
        
        if tiempo_transcurrido >= self.tiempo_espera:
            await ctx.send("✅ Puedes iniciar una partida de ahorcado ahora mismo.")
        else:
            tiempo_restante = int(self.tiempo_espera - tiempo_transcurrido)
            minutos = tiempo_restante // 60
            segundos = tiempo_restante % 60
            await ctx.send(f"⏳ Debes esperar {minutos} minutos y {segundos} segundos antes de iniciar otra partida.")
        
    @commands.command(name="dificultades_ahorcado", aliases=["hangman_difficulties"])
    async def dificultades(self, ctx):
        """Muestra información sobre las dificultades del ahorcado"""
        embed = discord.Embed(
            title="🎮 Dificultades del Ahorcado",
            description="Elige tu nivel de dificultad al iniciar un juego: `!ahorcado [apuesta] [dificultad]`",
            color=discord.Color.blue()
        )
        
        # Añadir información de cada dificultad
        for dificultad, config in self.dificultades.items():
            emoji = config['emoji']
            intentos = config['intentos']
            multiplicador = config['multiplicador']
            
            # Determinar el rango de letras
            if dificultad == 'facil':
                rango = "3-5 letras"
            elif dificultad == 'normal':
                rango = "6-8 letras"
            else:
                rango = "9+ letras"
                
            embed.add_field(
                name=f"{emoji} {dificultad.upper()}",
                value=f"• Palabras: {rango}\n• Intentos: {intentos}\n• Multiplicador: x{multiplicador}",
                inline=True
            )
            
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ahorcado(bot))