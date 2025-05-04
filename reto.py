# reto.py
import discord
from discord.ui import View, Button
import asyncio

# Opciones disponibles
opciones = ["piedra", "papel", "tijeras"]

# Función para determinar el ganador
def determinar_ganador(eleccion1, eleccion2):
    if eleccion1 == eleccion2:
        return "¡Empate! 😐"
    elif (eleccion1 == "piedra" and eleccion2 == "tijeras") or \
         (eleccion1 == "papel" and eleccion2 == "piedra") or \
         (eleccion1 == "tijeras" and eleccion2 == "papel"):
        return "🎉 ¡Jugador 1 gana!"
    else:
        return "🎉 ¡Jugador 2 gana!"

# Clase para los botones de elección
class EleccionView(View):
    def __init__(self, jugador):
        super().__init__(timeout=30)
        self.jugador = jugador
        self.eleccion = None

    # Botón para elegir "Piedra"
    @discord.ui.button(label="🪨 Piedra", style=discord.ButtonStyle.primary)
    async def piedra(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.jugador:
            await interaction.response.send_message("Este botón no es para vos.", ephemeral=True)
            return
        self.eleccion = "piedra"
        self.stop()  # Detener la espera
        await interaction.response.defer()

    # Botón para elegir "Papel"
    @discord.ui.button(label="📄 Papel", style=discord.ButtonStyle.success)
    async def papel(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.jugador:
            await interaction.response.send_message("Este botón no es para vos.", ephemeral=True)
            return
        self.eleccion = "papel"
        self.stop()  # Detener la espera
        await interaction.response.defer()

    # Botón para elegir "Tijeras"
    @discord.ui.button(label="✂️ Tijeras", style=discord.ButtonStyle.danger)
    async def tijeras(self, interaction: discord.Interaction, button: Button):
        if interaction.user != self.jugador:
            await interaction.response.send_message("Este botón no es para vos.", ephemeral=True)
            return
        self.eleccion = "tijeras"
        self.stop()  # Detener la espera
        await interaction.response.defer()



