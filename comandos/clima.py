import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os
from urllib.parse import quote_plus

# Cargar las variables de entorno desde el archivo .env
load_dotenv(dotenv_path='C:\\Users\\ignac\\Desktop\\cosas PY\\discord\\Token.env')

# Obtener la API Key de OpenWeatherMap desde la variable de entorno
API_KEY = os.getenv("API_KEY")

class Clima(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("API_KEY")

    @commands.command(name="clima")
    async def clima(self, ctx, *, ciudad: str):
        """Muestra información del clima para una ciudad específica"""
        # Reemplazar los espacios con %20 usando quote_plus
        ciudad = quote_plus(ciudad) 

        # Construir la URL de la API
        url = f"http://api.openweathermap.org/data/2.5/weather?q={ciudad}&appid={self.api_key}&units=metric&lang=es"
        
        # Hacer la petición a la API
        response = requests.get(url)
        data = response.json()

        if data.get("cod") != 200:
            error_message = data.get("message", "Desconocido")
            await ctx.send(f"🌧️ No se pudo obtener información del clima para '{ciudad}'. Error: {error_message}")
            return

        nombre_ciudad = data["name"]
        pais = data["sys"]["country"]
        temperatura = data["main"]["temp"]
        descripcion = data["weather"][0]["description"].capitalize()
        humedad = data["main"]["humidity"]
        viento = data["wind"]["speed"]

        embed = discord.Embed(
            title=f"🌤️ Clima en {nombre_ciudad}, {pais}",
            description=f"Información actual del clima en {nombre_ciudad}:",
            color=discord.Color.blue()
        )
        embed.add_field(name="🌡️ Temperatura", value=f"{temperatura}°C", inline=False)
        embed.add_field(name="☁️ Descripción", value=descripcion, inline=False)
        embed.add_field(name="💧 Humedad", value=f"{humedad}%", inline=False)
        embed.add_field(name="🌬️ Velocidad del viento", value=f"{viento} m/s", inline=False)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Clima(bot))