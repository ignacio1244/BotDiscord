# ppyt.py
import random
import discord
from discord.ui import View, Button

# Diccionario de emojis para el juego
EMOJIS = {
    "piedra": "✊",
    "papel": "✋",
    "tijeras": "✌"
}

# Función para determinar el ganador entre el usuario y el bot
def determinar_ganador(usuario, bot):
    if usuario == bot:
        return "¡Empate! 😐"
    elif (usuario == "piedra" and bot == "tijeras") or \
         (usuario == "papel" and bot == "piedra") or \
         (usuario == "tijeras" and bot == "papel"):
        return "¡Ganaste! 🎉"
    else:
        return "¡Perdiste! 💀"

# Vista de botones para las elecciones del usuario
class EleccionView(View):
    def __init__(self, jugador):
        super().__init__(timeout=30) 
        self.jugador = jugador
        self.eleccion = None

    @discord.ui.button(label=f"{EMOJIS['piedra']} Piedra", style=discord.ButtonStyle.danger)
    async def piedra(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.eleccion = "piedra"
        self.stop()

    @discord.ui.button(label=f"{EMOJIS['papel']} Papel", style=discord.ButtonStyle.primary)
    async def papel(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.eleccion = "papel"
        self.stop()

    @discord.ui.button(label=f"{EMOJIS['tijeras']} Tijeras", style=discord.ButtonStyle.success)
    async def tijeras(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.eleccion = "tijeras"
        self.stop()
async def on_timeout(self):
        # Si se acaba el tiempo sin que el usuario haga una elección
        self.eleccion = None

# Función para jugar una partida contra el bot
async def jugar_partida(ctx, jugador):
    jugador_puntos = 0
    bot_puntos = 0

    await ctx.send(f"🎮 {jugador.mention} ¡Vamos a jugar al mejor de 3 contra el bot!")

    while jugador_puntos < 2 and bot_puntos < 2:
        view = EleccionView(jugador)
        mensaje = await ctx.send("Elegí una opción:", view=view)
        await view.wait()

        # Verificamos si el jugador hizo una elección
        if view.eleccion is None:
            await ctx.send("⏰ No elegiste a tiempo. ¡Se canceló la partida!")
            return

        # Elección aleatoria del bot
        opciones = ["piedra", "papel", "tijeras"]
        eleccion_bot = random.choice(opciones)

        # Determinamos el ganador
        resultado = determinar_ganador(view.eleccion, eleccion_bot)

        if "Ganaste" in resultado:
            jugador_puntos += 1
        elif "Perdiste" in resultado:
            bot_puntos += 1

        # Enviar resultados consolidados
        await ctx.send(f"{EMOJIS[view.eleccion]} vs {EMOJIS[eleccion_bot]} - {resultado}")
        await ctx.send(f"🏆 Marcador: {jugador.name} {jugador_puntos} - Bot {bot_puntos}")

    # Resultados finales
    if jugador_puntos == 2:
        await ctx.send(f"🎉 Felicitaciones {jugador.mention}, ¡ganaste la partida!")
    else:
        await ctx.send(f"💀 El bot ganó la partida. ¡Suerte la próxima!")
