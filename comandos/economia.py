import discord
from discord.ext import commands
from comandos.casino import casino_manager

class Economia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="saldo")
    async def saldo(self, ctx):
        """Muestra el saldo actual del usuario"""
        usuario_id = str(ctx.author.id)
        saldo_actual = casino_manager.obtener_saldo(usuario_id)
        await ctx.send(f"💰 {ctx.author.mention}, tu saldo actual es de **{saldo_actual} monedas**.")

    @commands.command(name="pagos")
    async def pagos(self, ctx):
        """Muestra información sobre los pagos de la ruleta"""
        mensaje = (
            "**📊 pagos de la ruleta:**\n"
            "- Apostar a un **número exacto (0-36)**: x36\n"
            "- Apostar a **rojo o negro**: x2\n"
            "- Apostar a **par o impar**: x2\n"
            "Ejemplo: si apostás 100 monedas a 'rojo' y ganás, recibís 200 (100 tu apuesta + 100 ganancia)."
        )
        await ctx.send(mensaje)
        
    @commands.command(
        name="recargar",
        aliases=["recarga"],
        help="Recarga tu saldo con 100 monedas cuando llegues a cero"
    )
    @commands.cooldown(1, 3600, commands.BucketType.user)   # Cooldown de 1 hora
    async def recargar(self, ctx):
        """Recarga tu saldo con 100 monedas cuando tu saldo actual es cero"""
        usuario_id = str(ctx.author.id)
        saldo_actual = casino_manager.obtener_saldo(usuario_id)

        embed = discord.Embed(color=discord.Color.gold())
        
        if saldo_actual > 0:
            embed.title = "❌ Recarga no disponible"
            embed.description = (
                f"Actualmente tienes **{saldo_actual} monedas**.\n"
                "Solo puedes recargar cuando tu saldo sea **0**."
            )
            embed.set_footer(text="Vuelve a intentarlo cuando te quedes sin saldo")
        else:
            casino_manager.actualizar_saldo(usuario_id, 100)
            embed.title = "✅ Recarga exitosa"
            embed.description = (
                "Tu saldo ha sido recargado con **100 monedas**.\n"
                "¡Buena suerte en tus próximas apuestas!"
            )
            embed.set_footer(text="Puedes recargar nuevamente en 30 minutos")
            embed.set_thumbnail(url="https://media4.giphy.com/media/v1.Y2lkPTc5MGI3NjExbnBxMG0wcHhjbm1kZnV2czhzdGhmMzloOHQ5dGs1NnB3c2o4a3g3eSZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/67ThRZlYBvibtdF9JH/giphy.gif")

        await ctx.send(embed=embed)

    @recargar.error
    async def recargar_error(self, ctx, error):
        if isinstance(error, commands.CommandOnCooldown):
            minutes = int(error.retry_after // 60)
            embed = discord.Embed(
                title="⏳ Recarga en cooldown",
                description=f"Debes esperar {minutes} minutos antes de recargar nuevamente.",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
        else:
            print(f"Error en comando recargar: {error}")
            raise error

async def setup(bot):
    await bot.add_cog(Economia(bot))