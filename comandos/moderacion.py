import discord
import sys
import os
from discord.ext import commands

class Moderacion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    async def cog_check(self, ctx):
        """Verifica que el usuario tenga el rol de administrador para todos los comandos de este Cog"""
        
        if not ctx.guild:
            await ctx.send("❌ Este comando solo puede usarse en un servidor.")
            return False
            
        
        if not ctx.author.guild_permissions.administrator:
            await ctx.send("❌ Necesitás tener permisos de administrador para usar este comando.")
            return False
            
        return True

    @commands.command(name="borrar")
    async def borrar(self, ctx, cantidad: int = 5):
        """Borra una cantidad específica de mensajes del canal"""
        if cantidad < 1 or cantidad > 100:
            await ctx.send("⚠️ Tenés que elegir un número entre 1 y 100.")
            return

        await ctx.channel.purge(limit=cantidad + 1)  
        confirmacion = await ctx.send(f"🧹 Se borraron {cantidad} mensajes.")
        await confirmacion.delete(delay=5)  

    @commands.command(name="ping")
    async def ping(self, ctx):
        """Muestra la latencia del bot"""
        latencia = round(self.bot.latency * 1000)
        await ctx.send(f"🏓 Pong! Latencia: **{latencia}ms**")



    @commands.command(name="limpiar_chat", aliases=["purgar"])
    async def limpiar(self, ctx, usuario: discord.Member, cantidad: int = 5):
        """Borra una cantidad específica de mensajes de un usuario"""
        if cantidad < 1 or cantidad > 100:
            await ctx.send("⚠️ La cantidad debe estar entre 1 y 100 mensajes.")
            return
            
        def check(message):
            return message.author == usuario
            
        try:
            await ctx.message.delete()  
            borrados = await ctx.channel.purge(limit=100, check=check, bulk=True)
            
            
            borrados = borrados[:cantidad]
            
            confirmacion = await ctx.send(f"🧹 Se borraron {len(borrados)} mensajes de {usuario.mention}.")
            await confirmacion.delete(delay=5)
        except discord.Forbidden:
            await ctx.send("❌ No tengo permisos para borrar mensajes.")
        except Exception as e:
            await ctx.send(f"❌ Error al limpiar mensajes: {str(e)}")

async def setup(bot):
    await bot.add_cog(Moderacion(bot))

