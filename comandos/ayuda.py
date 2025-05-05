import discord
from discord.ext import commands

class Ayuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.categorias = {
            "🎮 Juegos": [
                ("🪨📄✂️ !ppt", "Juega piedra, papel o tijeras contra el bot"),
                ("⚔️ !reto @usuario", "Desafía a otro usuario a un duelo"),
                ("🎡 !ruleta [tipo] [apuesta]", "Ruleta del casino"),
                ("💸 !pagos", "Multiplicadores de la ruleta")
            ],
            "💰 Economía": [
                ("💰 !saldo", "Muestra tu saldo actual"),
                ("⟳ !recargar", "Recarga 100 monedas"),
                ("📊 !estadisticas", "Tus estadísticas de juego")
            ],
            "🌍 Utilidades": [
                ("💵 !dolar", "Cotización del dólar"),
                ("🔮 !horoscopo [signo]", "Horóscopo zodiacal"),
                ("🌤️ !clima [ciudad]", "Información meteorológica"),
                ("🪙 !crypto [moneda]", "Precios de criptomonedas")
            ],
            "🛠️ Moderación": [
                ("🗑️ !borrar [cantidad]", "Borra mensajes (admins)"),
                ("📊 !encuesta", "Crea encuestas")
            ],
            "🤖 GLaDOS": [
                ("🤖 !glados_info", "Información sobre GLaDOS"),
                ("🎂 !cake", "**???**")
            ]
        }
        self.alias_categorias = {
            'juegos': '🎮 Juegos',
            'economia': '💰 Economía',
            'utilidades': '🌍 Utilidades',
            'moderacion': '🛠️ Moderación',
            'glados': '🤖 GLaDOS'
        }

    @commands.command(name="ayuda", aliases=["comandos"])
    async def mostrar_ayuda(self, ctx, categoria: str = None):
        """Muestra todos los comandos o los de una categoría específica"""
        if categoria:
            await self.mostrar_categoria(ctx, categoria.lower())
        else:
            await self.mostrar_menu_principal(ctx)

    async def mostrar_menu_principal(self, ctx):
        """Muestra el menú principal de categorías"""
        embed = discord.Embed(
            title="🆘 Centro de Ayuda",
            description="Usa `!ayuda [categoría]` para ver comandos específicos\nEjemplo: `!ayuda juegos`",
            color=discord.Color.blue()
        )

        for nombre_categoria in self.categorias.keys():
            nombre_corto = nombre_categoria.split()[1].lower()
            embed.add_field(
                name=nombre_categoria,
                value=f"`{nombre_corto}` - {len(self.categorias[nombre_categoria])} comandos",
                inline=False
            )

        await ctx.send(embed=embed)

    async def mostrar_categoria(self, ctx, categoria_input: str):
        """Muestra los comandos de una categoría específica"""
        
        categoria = self.alias_categorias.get(categoria_input, None)
        
        if not categoria:
            categorias_disponibles = "\n".join(
                f"- `{alias}` ({nombre})" 
                for alias, nombre in self.alias_categorias.items()
            )
            embed = discord.Embed(
                title="❌ Categoría no encontrada",
                description=f"Categorías disponibles:\n{categorias_disponibles}",
                color=discord.Color.red()
            )
            return await ctx.send(embed=embed)

        embed = discord.Embed(
            title=f"{categoria} - Comandos Disponibles",
            color=discord.Color.green()
        )

        for nombre, descripcion in self.categorias[categoria]:
            embed.add_field(name=nombre, value=descripcion, inline=False)

        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ayuda(bot))