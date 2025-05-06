import discord
from discord.ext import commands
from datetime import datetime

EMOJIS = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
MAX_OPCIONES = 10
MIN_OPCIONES = 2

class Encuesta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="encuesta")
    async def crear_encuesta(self, ctx, *, raw: str = None):
        """Crea una encuesta con hasta 10 opciones"""
        
        if not raw or "|" not in raw:
            return await self.mostrar_ayuda(ctx)

        
        parts = [p.strip() for p in raw.split("|") if p.strip()]
        pregunta = parts[0]
        opciones = parts[1:]

        
        if len(opciones) < MIN_OPCIONES:
            return await ctx.send(f"❌ Necesitas al menos {MIN_OPCIONES} opciones válidas.")
        if len(opciones) > MAX_OPCIONES:
            return await ctx.send(f"❌ Máximo {MAX_OPCIONES} opciones permitidas.")

        
        embed = self.crear_embed_encuesta(ctx, pregunta, opciones)
        mensaje = await ctx.send(embed=embed)
        
        
        await self.agregar_reacciones(mensaje, len(opciones))

    def crear_embed_encuesta(self, ctx, pregunta, opciones):
        """Crea un embed visualmente atractivo para la encuesta"""
        embed = discord.Embed(
            title=f"📊 {pregunta}",
            color=discord.Color.blue(),
            timestamp=datetime.utcnow()
        )
        
        
        descripcion = "\n".join(
            f"{EMOJIS[i]} {opt.capitalize()}" 
            for i, opt in enumerate(opciones)
        )
        embed.description = descripcion
        embed.set_footer(
            text=f"Encuesta creada por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url
        )
        
        
        embed.add_field(
            name="Instrucciones",
            value="Reacciona con el emoji correspondiente a tu elección",
            inline=False
        )
        
        return embed

    async def agregar_reacciones(self, mensaje, cantidad_opciones):
        """Añade las reacciones al mensaje de forma eficiente"""
        for i in range(cantidad_opciones):
            try:
                await mensaje.add_reaction(EMOJIS[i])
            except discord.HTTPException:
                continue  

    async def mostrar_ayuda(self, ctx):
        """Muestra mensaje de ayuda con formato embed"""
        embed = discord.Embed(
            title="❓ Uso correcto del comando !encuesta",
            color=discord.Color.orange()
        )
        
        embed.add_field(
            name="Formato",
            value="`!encuesta pregunta | opción1 | opción2 [| opción3 ...]`",
            inline=False
        )
        
        embed.add_field(
            name="Ejemplo",
            value="`!encuesta ¿Mejor comida? | Pizza | Hamburguesa | Sushi`",
            inline=False
        )
        
        embed.add_field(
            name="Requisitos",
            value=f"- Mínimo {MIN_OPCIONES} opciones\n- Máximo {MAX_OPCIONES} opciones",
            inline=False
        )
        
        embed.set_footer(text="Separa cada elemento con el carácter |")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Encuesta(bot))