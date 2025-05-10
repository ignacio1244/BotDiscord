import discord
from discord.ext import commands

class Ayuda(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.categorias = {
            "🎮 Juegos": [
                ("🪨📄✂️ !ppt", "Juega piedra, papel o tijeras contra el bot"),
                ("⚔️ !reto @usuario", "Desafía a otro usuario a un duelo"),
                ("🔠 !wordle", "Juega a wordle"),
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
            'moderacion': '🛠️ Moderacion',
            'glados': '🤖 GLaDOS'
        }

    @commands.command(name="ayuda", aliases=["comandos"])
    async def mostrar_ayuda(self, ctx, categoria_o_comando: str = None):
        """Muestra todos los comandos o los de una categoría específica"""
        if not categoria_o_comando:
            await self.mostrar_menu_principal(ctx)
            return
            
        # Verificar si es un comando específico
        comando = self.bot.get_command(categoria_o_comando)
        if comando:
            await self.mostrar_ayuda_comando(ctx, comando)
            return
            
        # Si no es un comando, tratar como categoría
        await self.mostrar_categoria(ctx, categoria_o_comando.lower())
        
    async def mostrar_ayuda_comando(self, ctx, comando):
        """Muestra ayuda detallada para un comando específico"""
        embed = discord.Embed(
            title=f"📚 Ayuda: !{comando.name}",
            description=comando.help or "No hay descripción disponible.",
            color=discord.Color.purple()
        )
        
        # Mostrar aliases si existen
        if comando.aliases:
            embed.add_field(
                name="🔄 Aliases",
                value=", ".join([f"`!{alias}`" for alias in comando.aliases]),
                inline=False
            )
        
        # Mostrar uso si está disponible
        if hasattr(comando, 'usage') and comando.usage:
            embed.add_field(
                name="📝 Uso",
                value=f"`!{comando.name} {comando.usage}`",
                inline=False
            )
        else:
            embed.add_field(
                name="📝 Uso",
                value=f"`!{comando.name}`",
                inline=False
            )
            
        embed.set_footer(text=f"Solicitado por {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        
        await ctx.send(embed=embed)

    async def mostrar_menu_principal(self, ctx):
        """Muestra el menú principal de categorías"""
        embed = discord.Embed(
            title="🤖 Centro de Ayuda de GLaDOS",
            description="Bienvenido al centro de ayuda. Selecciona una categoría para ver los comandos disponibles.\n\n"
                       "**Uso:** `!ayuda [categoría]`\n"
                       "**Ejemplo:** `!ayuda juegos`",
            color=discord.Color.purple()
        )

        for nombre_categoria in self.categorias.keys():
            nombre_corto = nombre_categoria.split()[1].lower()
            comandos = self.categorias[nombre_categoria]
            ejemplos = ", ".join([f"`!{cmd[0].split()[1]}`" for cmd in comandos[:2]])
            
            embed.add_field(
                name=nombre_categoria,
                value=f"**{len(comandos)} comandos** • Ejemplo: {ejemplos}\n"
                     f"Ver todos: `!ayuda {nombre_corto}`",
                inline=False
            )

        embed.set_footer(text="Tip: Usa !ayuda [comando] para ver información detallada de un comando específico")
        
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