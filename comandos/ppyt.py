import sys
import os
import random
import discord
from discord.ext import commands
from discord.ui import View, Button

from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from comandos.estadisticas import EstadisticasManager

EMOJIS = {
    "piedra": "✊",
    "papel": "✋",
    "tijeras": "✌"
}

def determinar_ganador(usuario, bot):
    if usuario == bot:
        return "¡Empate! 😐"
    elif (usuario == "piedra" and bot == "tijeras") or \
         (usuario == "papel" and bot == "piedra") or \
         (usuario == "tijeras" and bot == "papel"):
        return "¡Ganaste! 🎉"
    else:
        return "¡Perdiste! 💀"

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
        self.eleccion = None

class PPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stats_manager = EstadisticasManager()

    @commands.command(name="ppt")
    async def ppt(self, ctx):
        jugador = ctx.author
        jugador_puntos = 0
        bot_puntos = 0

        await ctx.send(f"🎮 {jugador.mention} ¡Vamos a jugar al mejor de 3 contra el bot!")

        while jugador_puntos < 2 and bot_puntos < 2:
            view = EleccionView(jugador)
            mensaje = await ctx.send("Elegí una opción:", view=view)
            await view.wait()

            if view.eleccion is None:
                await ctx.send("⏰ No elegiste a tiempo. ¡Se canceló la partida!")
                return

            opciones = ["piedra", "papel", "tijeras"]
            eleccion_bot = random.choice(opciones)
            resultado = determinar_ganador(view.eleccion, eleccion_bot)

            if "Ganaste" in resultado:
                jugador_puntos += 1
                self.stats_manager.actualizar_estadisticas_ppt(jugador.id, 'victoria')
            elif "Perdiste" in resultado:
                bot_puntos += 1
                self.stats_manager.actualizar_estadisticas_ppt(jugador.id, 'derrota')
            else:
                self.stats_manager.actualizar_estadisticas_ppt(jugador.id, 'empate')

            await ctx.send(f"{EMOJIS[view.eleccion]} vs {EMOJIS[eleccion_bot]} - {resultado}")
            await ctx.send(f"🏆 Marcador: {jugador.name} {jugador_puntos} - Bot {bot_puntos}")

        if jugador_puntos == 2:
            await ctx.send(f"🎉 Felicitaciones {jugador.mention}, ¡ganaste la partida!")
        else:
            await ctx.send(f"💀 El bot ganó la partida. ¡Suerte la próxima!")

async def setup(bot):
    await bot.add_cog(PPT(bot))
