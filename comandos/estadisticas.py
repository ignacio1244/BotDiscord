import json
import os
import discord
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
            
            stats_default = {
                "ppt": {"victorias": 0, "derrotas": 0},  
                "reto": {"victorias": 0, "derrotas": 0},
                "ruleta": {"ganancias": 0, "perdidas": 0, "apuestas_totales": 0},
                "wordle": {"partidas_jugadas": 0, "partidas_ganadas": 0, "partidas_perdidas": 0,},
                "ahorcado": {"partidas_jugadas": 0, "victorias": 0, "derrotas": 0, "ganancias": 0, "perdidas": 0}
            }
            
            if str(usuario_id) in datos:
                user_stats = datos[str(usuario_id)]
                if "ppt" not in user_stats:
                    user_stats["ppt"] = stats_default["ppt"]
                elif "empates" in user_stats["ppt"]:
                    del user_stats["ppt"]["empates"]
                if "reto" not in user_stats:
                    user_stats["reto"] = stats_default["reto"]
                elif "empates" in user_stats["reto"]:
                    del user_stats["reto"]["empates"]
                if "ruleta" not in user_stats:
                    user_stats["ruleta"] = stats_default["ruleta"]
                if "wordle" not in user_stats:
                    user_stats["wordle"] = stats_default["wordle"]
                if "ahorcado" not in user_stats:
                    user_stats["ahorcado"] = stats_default["ahorcado"]
                return user_stats
            
            return stats_default
            
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "ppt": {"victorias": 0, "derrotas": 0},  
                "reto": {"victorias": 0, "derrotas": 0},
                "ruleta": {"ganancias": 0, "perdidas": 0, "apuestas_totales": 0},
                "wordle": {"partidas_jugadas": 0, "partidas_ganadas": 0, "partidas_perdidas": 0},
                "dados": {"victorias": 0, "derrotas": 0},
                "ahorcado": {"partidas_jugadas": 0, "victorias": 0, "derrotas": 0, "ganancias": 0, "perdidas": 0}
            }

    def guardar_estadisticas(self, usuario_id, stats):
        try:
            with open(self.data_file, 'r') as f:
                datos = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            datos = {}

        datos[str(usuario_id)] = stats
        
        with open(self.data_file, 'w') as f:
            json.dump(datos, f, indent=4)
            
    def actualizar_estadisticas_ppt(self, usuario_id, resultado):
        """
        Actualiza las estadísticas de piedra, papel o tijeras
        resultado: 'victoria', 'derrota' 
        """
        stats = self.obtener_estadisticas(usuario_id)
        
        if resultado == 'victoria':
            stats["ppt"]["victorias"] += 1
        elif resultado == 'derrota':
            stats["ppt"]["derrotas"] += 1
            
        self.guardar_estadisticas(usuario_id, stats)
        return stats
        
    def actualizar_estadisticas_reto(self, usuario_id, resultado):
        """
        Actualiza las estadísticas del juego de reto
        resultado: 'victoria' o 'derrota'
        """
        stats = self.obtener_estadisticas(usuario_id)
        
        if resultado == 'victoria':
            stats["reto"]["victorias"] += 1
        elif resultado == 'derrota':
            stats["reto"]["derrotas"] += 1
            
        self.guardar_estadisticas(usuario_id, stats)
        return stats
        
    def actualizar_estadisticas_ruleta(self, usuario_id, ganancia):
        """
        Actualiza las estadísticas de la ruleta
        ganancia: cantidad ganada (positivo) o perdida (negativo)
        La ganancia ya debe ser neta (ganancia - apuesta)
        """
        stats = self.obtener_estadisticas(usuario_id)
        
        # No incrementamos apuestas_totales aquí porque ya se hace en el comando ruleta
        
        if ganancia > 0:
            stats["ruleta"]["ganancias"] += ganancia
        else:
            stats["ruleta"]["perdidas"] += abs(ganancia)
            
        self.guardar_estadisticas(usuario_id, stats)
        return stats

    def registrar_ganancia_ruleta(self, usuario_id, cantidad):
        """
        Método de conveniencia para registrar una ganancia en la ruleta
        cantidad: ganancia neta (después de restar la apuesta)
        """
        return self.actualizar_estadisticas_ruleta(usuario_id, cantidad)
        
    def registrar_perdida_ruleta(self, usuario_id, cantidad):
        """
        Método de conveniencia para registrar una pérdida en la ruleta
        cantidad: valor de la apuesta perdida
        """
        return self.actualizar_estadisticas_ruleta(usuario_id, -abs(cantidad))

    def actualizar_estadisticas_ahorcado(self, usuario_id, resultado, ganancia=0):
        """
        Actualiza las estadísticas del juego del ahorcado
        resultado: 'victoria' o 'derrota'
        ganancia: cantidad ganada (positivo) o perdida (negativo)
        """
        stats = self.obtener_estadisticas(usuario_id)
        
        stats["ahorcado"]["partidas_jugadas"] += 1
        
        if resultado == 'victoria':
            stats["ahorcado"]["victorias"] += 1
            if ganancia > 0:
                stats["ahorcado"]["ganancias"] += ganancia
        elif resultado == 'derrota':
            stats["ahorcado"]["derrotas"] += 1
            if ganancia < 0:
                stats["ahorcado"]["perdidas"] += abs(ganancia)
            
        self.guardar_estadisticas(usuario_id, stats)
        return stats
        
    def registrar_victoria_ahorcado(self, usuario_id, ganancia):
        """
        Método de conveniencia para registrar una victoria en el ahorcado
        ganancia: cantidad ganada
        """
        return self.actualizar_estadisticas_ahorcado(usuario_id, 'victoria', ganancia)
        
    def registrar_derrota_ahorcado(self, usuario_id, perdida):
        """
        Método de conveniencia para registrar una derrota en el ahorcado
        perdida: cantidad perdida (valor positivo)
        """
        return self.actualizar_estadisticas_ahorcado(usuario_id, 'derrota', -abs(perdida))

class Estadisticas(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = EstadisticasManager()

    @commands.command(name="stats", aliases=["estadisticas"])
    async def estadisticas(self, ctx, juego: str = None):
        """Muestra las estadísticas del usuario"""
        stats = self.manager.obtener_estadisticas(ctx.author.id)
        
        if juego and juego.lower() in ["ppt", "piedra", "papel", "tijeras"]:
            ppt_stats = stats["ppt"]
            total_partidas = ppt_stats["victorias"] + ppt_stats["derrotas"]
            
            embed = discord.Embed(
                title=f"🎮 Estadísticas de Piedra, Papel o Tijeras",
                description=f"Estadísticas de {ctx.author.mention}",
                color=discord.Color.blue()
            )
            
            embed.add_field(name="✅ Victorias", value=str(ppt_stats["victorias"]), inline=True)
            embed.add_field(name="❌ Derrotas", value=str(ppt_stats["derrotas"]), inline=True)
            
            if total_partidas > 0:
                porcentaje = round((ppt_stats["victorias"] / total_partidas) * 100, 2)
                embed.add_field(name="📊 Porcentaje de victorias", value=f"{porcentaje}%", inline=False)
                
            embed.add_field(name="🎯 Total de partidas", value=str(total_partidas), inline=False)
            
        elif juego and juego.lower() in ["reto", "duelo", "challenge"]:
            reto_stats = stats["reto"]
            total_partidas = reto_stats["victorias"] + reto_stats["derrotas"]
            
            embed = discord.Embed(
                title=f"⚔️ Estadísticas de Duelos",
                description=f"Estadísticas de {ctx.author.mention}",
                color=discord.Color.dark_gold()
            )
            
            embed.add_field(name="✅ Victorias", value=str(reto_stats["victorias"]), inline=True)
            embed.add_field(name="❌ Derrotas", value=str(reto_stats["derrotas"]), inline=True)
            
            if total_partidas > 0:
                porcentaje = round((reto_stats["victorias"] / total_partidas) * 100, 2)
                embed.add_field(name="📊 Porcentaje de victorias", value=f"{porcentaje}%", inline=False)
                
            embed.add_field(name="🎯 Total de duelos", value=str(total_partidas), inline=False)
            
        elif juego and juego.lower() in ["ruleta", "casino"]:
            ruleta_stats = stats["ruleta"]
            
            embed = discord.Embed(
                title=f"🎰 Estadísticas de Ruleta",
                description=f"Estadísticas de {ctx.author.mention}",
                color=discord.Color.gold()
            )
            
            embed.add_field(name="💰 Ganancias totales", value=str(ruleta_stats["ganancias"]), inline=True)
            embed.add_field(name="💸 Pérdidas totales", value=str(ruleta_stats["perdidas"]), inline=True)
            embed.add_field(name="🎲 Apuestas realizadas", value=str(ruleta_stats["apuestas_totales"]), inline=True)
            
            # Calcular balance total
            
            balance = ruleta_stats["ganancias"] - ruleta_stats["perdidas"]
            color = "🟢" if balance >= 0 else "🔴"
            embed.add_field(name="💵 Balance total", value=f"{color} {balance}", inline=False)
            
        elif juego and juego.lower() in ["ahorcado", "hangman"]:
            ahorcado_stats = stats["ahorcado"]
            
            embed = discord.Embed(
                title=f"🎮 Estadísticas del Ahorcado",
                description=f"Estadísticas de {ctx.author.mention}",
                color=discord.Color.dark_green()
            )
            
            embed.add_field(name="🎯 Partidas jugadas", value=str(ahorcado_stats["partidas_jugadas"]), inline=True)
            embed.add_field(name="✅ Victorias", value=str(ahorcado_stats["victorias"]), inline=True)
            embed.add_field(name="❌ Derrotas", value=str(ahorcado_stats["derrotas"]), inline=True)
            
            if ahorcado_stats["partidas_jugadas"] > 0:
                porcentaje = round((ahorcado_stats["victorias"] / ahorcado_stats["partidas_jugadas"]) * 100, 2)
                embed.add_field(name="📊 Porcentaje de victorias", value=f"{porcentaje}%", inline=False)
            
            embed.add_field(name="💰 Ganancias totales", value=str(ahorcado_stats["ganancias"]), inline=True)
            embed.add_field(name="💸 Pérdidas totales", value=str(ahorcado_stats["perdidas"]), inline=True)
            
            # Calcular balance total
            balance_ahorcado = ahorcado_stats["ganancias"] - ahorcado_stats["perdidas"]
            color_ahorcado = "🟢" if balance_ahorcado >= 0 else "🔴"
            embed.add_field(name="💵 Balance total", value=f"{color_ahorcado} {balance_ahorcado}", inline=False)
            
        else:
            embed = discord.Embed(
                title=f"📊 Estadísticas de {ctx.author.name}",
                description="Usa `!stats ppt`, `!stats reto`, `!stats ruleta`, `!stats ahorcado` o `!wordle_stats` para ver estadísticas específicas.",
                color=discord.Color.purple()
            )
            
            ppt_stats = stats["ppt"]
            total_ppt = ppt_stats["victorias"] + ppt_stats["derrotas"]
            
            reto_stats = stats["reto"]
            total_reto = reto_stats["victorias"] + reto_stats["derrotas"]
            
            ruleta_stats = stats["ruleta"]
            balance_ruleta = ruleta_stats["ganancias"] - ruleta_stats["perdidas"]
            
            wordle_stats = stats["wordle"]
            total_wordle = wordle_stats["partidas_jugadas"]
            
            ahorcado_stats = stats["ahorcado"]
            total_ahorcado = ahorcado_stats["partidas_jugadas"]
            balance_ahorcado = ahorcado_stats["ganancias"] - ahorcado_stats["perdidas"]
            
            embed.add_field(name="🎮 Piedra, Papel o Tijeras", 
                           value=f"Victorias: {ppt_stats['victorias']}\nDerrotas: {ppt_stats['derrotas']}\nTotal: {total_ppt}", 
                           inline=True)
            
            embed.add_field(name="⚔️ Duelos", 
                           value=f"Victorias: {reto_stats['victorias']}\nDerrotas: {reto_stats['derrotas']}\nTotal: {total_reto}", 
                           inline=True)
            
            embed.add_field(name="🎰 Ruleta", 
                           value=f"Ganancias: {ruleta_stats['ganancias']}\nPérdidas: {ruleta_stats['perdidas']}\nBalance: {balance_ruleta}", 
                           inline=True)
                
            embed.add_field(name="🔠 Wordle", 
                               value=f"Partidas: {total_wordle}\nVictorias: {wordle_stats['partidas_ganadas']}\nDerrotas: {wordle_stats['partidas_perdidas']}", 
                               inline=True)
                               
            embed.add_field(name="🎮 Ahorcado", 
                               value=f"Partidas: {total_ahorcado}\nVictorias: {ahorcado_stats['victorias']}\nBalance: {balance_ahorcado}", 
                               inline=True)
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Estadisticas(bot))