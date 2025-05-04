import json
import os
from pathlib import Path
from discord.ext import commands

class EstadisticasManager:
    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / "utils"
        self.data_file = self.data_dir / "estadisticas.json"
        self._initialize_data()

    def _initialize_data(self):
        """Inicializa el archivo si no existe"""
        self.data_dir.mkdir(exist_ok=True)
        if not self.data_file.exists():
            with open(self.data_file, 'w') as f:
                json.dump({}, f)

    def obtener_estadisticas(self, usuario_id):
        try:
            with open(self.data_file, 'r') as f:
                datos = json.load(f)
            return datos.get(str(usuario_id), {"victorias": 0, "derrotas": 0})
        except (FileNotFoundError, json.JSONDecodeError):
            return {"victorias": 0, "derrotas": 0}

    def guardar_estadisticas(self, usuario_id, stats):
        try:
            with open(self.data_file, 'r') as f:
                datos = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            datos = {}

        datos[str(usuario_id)] = stats
        
        with open(self.data_file, 'w') as f:
            json.dump(datos, f, indent=4)

class Estadisticas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = EstadisticasManager()

    @commands.command()
    async def estadisticas(self, ctx):
        stats = self.manager.obtener_estadisticas(ctx.author.id)
        await ctx.send(f"Victorias: {stats['victorias']}\nDerrotas: {stats['derrotas']}")

async def setup(bot):
    await bot.add_cog(Estadisticas(bot))