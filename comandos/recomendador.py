import discord
import random
import aiohttp
import os
from discord.ext import commands
from discord import app_commands

class Recomendador(commands.Cog):
    """Cog para recomendar películas y series"""
    
    def __init__(self, bot):
        self.bot = bot
        self.api_key = os.getenv("TMDB_API_KEY", "")  # Necesitarás una API key de TMDB
        self.base_url = "https://api.themoviedb.org/3"
        # ID del canal donde se permite usar el comando (cámbialo por el ID de tu canal)
        self.canal_permitido = os.getenv("CANAL_RECOMENDACIONES", None)
        self.generos = {
            "acción": 28,
            "aventura": 12,
            "animación": 16,
            "comedia": 35,
            "crimen": 80,
            "documental": 99,
            "drama": 18,
            "familiar": 10751,
            "fantasía": 14,
            "historia": 36,
            "terror": 27,
            "música": 10402,
            "misterio": 9648,
            "romance": 10749,
            "ciencia ficción": 878,
            "thriller": 53,
            "bélica": 10752,
            "western": 37
        }
        
        # Recomendaciones predefinidas en caso de no tener API key
        self.peliculas_predefinidas = {
            "acción": ["John Wick", "Mad Max: Fury Road", "Die Hard", "The Matrix"],
            "comedia": ["Superbad", "Anchorman", "The Hangover", "Bridesmaids"],
            "drama": ["The Shawshank Redemption", "The Godfather", "Schindler's List", "Forrest Gump"],
            "ciencia ficción": ["Blade Runner", "Interstellar", "Arrival", "The Martian"],
            "terror": ["The Shining", "Hereditary", "Get Out", "A Quiet Place"]
        }
        
        self.series_predefinidas = {
            "acción": ["Breaking Bad", "The Boys", "Daredevil", "24"],
            "comedia": ["The Office", "Friends", "Brooklyn Nine-Nine", "Parks and Recreation"],
            "drama": ["The Wire", "The Sopranos", "Better Call Saul", "Mad Men", "Game of Thrones"],
            "ciencia ficción": ["Stranger Things", "Black Mirror", "Westworld", "The Expanse"],
            "terror": ["The Haunting of Hill House", "American Horror Story", "The Walking Dead", "Hannibal"]
        }

    async def cog_check(self, ctx):
        """Verifica si el comando se está usando en el canal permitido"""
        # Si no hay canal configurado, permitir en todos los canales
        if not self.canal_permitido:
            return True
            
        # Verificar si el comando se está usando en el canal permitido
        if str(ctx.channel.id) != self.canal_permitido:
            await ctx.send(f"⚠️ Este comando solo se puede usar en el canal <#{self.canal_permitido}>")
            return False
        return True

    @commands.command(name="recomendar", aliases=["recomendacion", "rec"])
    async def recomendar(self, ctx, tipo: str = None, genero: str = None):
        """
        Recomienda una película o serie
        
        Uso: !recomendar [pelicula/serie] [género]
        Ejemplo: !recomendar pelicula acción
        """
        
        # Verificar argumentos
        if not tipo or tipo.lower() not in ["pelicula", "película", "serie"]:
            embed = discord.Embed(
                title="🎬 Recomendador",
                description="Por favor, especifica si quieres una recomendación de película o serie.\n\n"
                           "**Uso:** `!recomendar [pelicula/serie] [género]`\n"
                           "**Ejemplo:** `!recomendar pelicula acción`\n\n"
                           "**Géneros disponibles:** " + ", ".join(self.generos.keys()),
                color=discord.Color.blue()
            )
            return await ctx.send(embed=embed)
        
        # Normalizar tipo
        tipo = "película" if tipo.lower() in ["pelicula", "película"] else "serie"
        
        # Si no se especifica género, elegir uno al azar
        if not genero:
            genero = random.choice(list(self.generos.keys()))
        elif genero.lower() not in self.generos:
            embed = discord.Embed(
                title=f"🎬 Géneros de {tipo}s disponibles",
                description="El género especificado no está disponible. Por favor, elige un género de la lista:\n\n" + 
                           "\n".join([f"• {g.capitalize()}" for g in self.generos.keys()]) +
                           f"\n\n**Ejemplo:** `!recomendar {tipo} acción`",
                color=discord.Color.blue()
            )
            return await ctx.send(embed=embed)
        
        # Normalizar género
        genero = genero.lower()
        
        # Mensaje de carga
        mensaje = await ctx.send(f"🔍 Buscando {tipo}s de {genero}...")
        
        # Intentar obtener recomendación de la API si hay key
        if self.api_key:
            recomendacion = await self._obtener_recomendacion_api(tipo, genero)
            if recomendacion:
                await mensaje.delete()
                return await ctx.send(embed=recomendacion)
        
        # Si no hay API key o falló la petición, usar recomendaciones predefinidas
        recomendacion = await self._obtener_recomendacion_predefinida(tipo, genero)
        await mensaje.delete()
        await ctx.send(embed=recomendacion)

    async def _obtener_recomendacion_api(self, tipo, genero):
        """Obtiene una recomendación de la API de TMDB"""
        try:
            # Determinar endpoint según tipo
            endpoint = "movie" if tipo == "película" else "tv"
            
            url = f"{self.base_url}/discover/{endpoint}?api_key={self.api_key}&with_genres={self.generos[genero]}&language=es-ES&sort_by=popularity.desc&vote_average.gte=7.5"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        return None
                    
                    data = await response.json()
                    
                    if not data.get("results") or len(data["results"]) == 0:
                        return None
                    
                    # Elegir una recomendación aleatoria entre las 10 primeras
                    max_index = min(10, len(data["results"]))
                    recomendacion = random.choice(data["results"][:max_index])
                    
                    # Verificar que la valoración sea mayor a 7.5
                    if recomendacion.get('vote_average', 0) < 7.5:
                        # Buscar una alternativa con valoración mayor a 7.5
                        alternativas = [r for r in data["results"] if r.get('vote_average', 0) >= 7.5]
                        if alternativas:
                            recomendacion = random.choice(alternativas)
                    
                    # Crear embed
                    embed = discord.Embed(
                        title=recomendacion.get("title" if tipo == "película" else "name", "Sin título"),
                        description=recomendacion.get("overview", "Sin descripción disponible."),
                        color=discord.Color.gold()
                    )
                    
                    # Agregar imagen si está disponible
                    if recomendacion.get("poster_path"):
                        embed.set_thumbnail(url=f"https://image.tmdb.org/t/p/w500{recomendacion['poster_path']}")
                    
                    # Agregar información adicional
                    embed.add_field(
                        name="Valoración",
                        value=f"⭐ {round(recomendacion.get('vote_average', 0), 1)}/10",
                        inline=True
                    )
                    
                    # Obtener y formatear la fecha
                    fecha_original = recomendacion.get("release_date" if tipo == "película" else "first_air_date", "Desconocida")
                    
                    # Convertir formato de fecha de YYYY-MM-DD a DD-MM-YYYY si es posible
                    if fecha_original != "Desconocida" and len(fecha_original) == 10:
                        try:
                            año, mes, dia = fecha_original.split('-')
                            fecha = f"{dia}-{mes}-{año}"
                        except:
                            fecha = fecha_original
                    else:
                        fecha = fecha_original
                    
                    embed.add_field(
                        name="Fecha de lanzamiento",
                        value=fecha,
                        inline=True
                    )
                    
                    embed.add_field(
                        name="Género",
                        value=genero.capitalize(),
                        inline=True
                    )
                    
                    embed.set_footer(text=f"Recomendación de {tipo} de {genero} | Datos de TMDB")
                    
                    return embed
                    
        except Exception as e:
            print(f"Error al obtener recomendación de API: {e}")
            return None

    async def _obtener_recomendacion_predefinida(self, tipo, genero):
        """Obtiene una recomendación de la lista predefinida"""
        # Usar el género más cercano si el solicitado no está en las predefinidas
        generos_disponibles = list(self.peliculas_predefinidas.keys())
        if genero not in generos_disponibles:
            genero = random.choice(generos_disponibles)
        
        # Obtener lista según tipo
        lista = self.peliculas_predefinidas if tipo == "película" else self.series_predefinidas
        
        # Elegir recomendación aleatoria
        recomendacion = random.choice(lista[genero])
        
        # Crear embed
        embed = discord.Embed(
            title=f"🎬 Recomendación de {tipo}",
            description=f"Te recomiendo ver: **{recomendacion}**",
            color=discord.Color.purple()
        )
        
        embed.add_field(
            name="Género",
            value=genero.capitalize(),
            inline=True
        )
        
        embed.set_footer(text=f"Usa !recomendar {tipo} [género] para más recomendaciones específicas")
        
        return embed

async def setup(bot):
    await bot.add_cog(Recomendador(bot))