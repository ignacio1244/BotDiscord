import discord
from discord.ext import commands

class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="borrar")
    async def borrar(self, ctx, cantidad: int = 5):
        """Borra una cantidad específica de mensajes del canal"""
        if not ctx.author.guild_permissions.manage_messages:
            await ctx.send("❌ No tenés permisos para borrar mensajes.")
            return

        if cantidad < 1 or cantidad > 100:
            await ctx.send("⚠️ Tenés que elegir un número entre 1 y 100.")
            return

        await ctx.channel.purge(limit=cantidad + 1)  # +1 para borrar el comando también
        confirmacion = await ctx.send(f"🧹 Se borraron {cantidad} mensajes.")
        await confirmacion.delete(delay=5)  # Borra el mensaje de confirmación tras 5 segundos

async def setup(bot):
    await bot.add_cog(Moderacion(bot))

