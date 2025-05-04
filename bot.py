import os
import discord
import GLaDOS
from moderacion import borrar_mensajes
from ppyt import jugar_partida
from dotenv import load_dotenv
from discord.ext import commands
from dolar import obtener_cotizacion_dolar
from casino_saldos import obtener_saldo, actualizar_saldo
from reto import determinar_ganador,EleccionView as RetoEleccionView 
from horoscopo import obtener_horoscopo
from clima import obtener_clima
from casino import manejar_comando_ruleta
from encuesta import crear_encuesta
from crypto import obtener_precio_coincap    

#no olvidar botpy\Scripts\activate


# Cargar token desde archivo .env
load_dotenv(dotenv_path='C:\\Users\\ignac\\Desktop\\cosas PY\\discord\\Token.env')
TOKEN = os.getenv("DISCORD_TOKEN")


# Configurar intents y el bot
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  

bot = commands.Bot(command_prefix="!", intents=intents)


# Evento de inicio
@bot.event
async def on_ready():
    print(f"Bot conectado como {bot.user}")

# Comando para borrar mensajes
@bot.command()
async def borrar(ctx, cantidad: int = 5):
    await borrar_mensajes(ctx, cantidad)

# Comando para jugar piedra, papel o tijeras (user vs bot)
@bot.command()
async def ppt(ctx):
    jugador = ctx.author
    await jugar_partida(ctx, jugador)  

# Comando de ayuda
@bot.command()
async def ayuda(ctx):
    embed = discord.Embed(
        title="🆘 Comandos Disponibles",
        description="Aquí tienes todos los comandos que puedes usar.",
        color=discord.Color.blue()
    )

    comandos = [
        
        ("🤖 !glados_info", "Muestra información sobre GLaDOS."),
        ("🪨📄✂️ !ppt", "Juega piedra, papel o tijeras contra el bot."),
        ("⚔️ !reto @usuario", "Desafía a otro usuario a un duelo de piedra, papel o tijeras."),
        ("💵 !dolar", "Muestra la cotización actual del dólar en Argentina."),
        ("🔮 !horoscopo [signo]", "Recibe un horóscopo 100% confiable para tu signo."),
        ("🌤️ !clima [ciudad]", "Obtén información del clima de la ciudad que elijas."),
        ("🎡 !ruleta [numero] [apuesta]", "Simula una ruleta. ¡Apuesta por número, color o par/impar!"),
        ("💸 !pagos", "Muestra los pagos de la ruleta según el tipo de apuesta."),
        ("⟳ !recargar", "Recarga tu saldo con 100 monedas."),
        ("💰 !saldo", "Muestra tu saldo actual."),
        ("📊 !encuesta pregunta | opción1 | opción2 | opción3 ... opción10", "Crea una encuesta."),
        ("🪙 !crypto [criptomoneda]", "precios de criptomonedas."),
        ("🗑️ !borrar [cantidad]", "Borra la cantidad de mensajes que elijas.(uso excusivo de admins)"),
    ]

    for nombre, descripcion in comandos:
        embed.add_field(name=nombre, value=descripcion, inline=False)

    await ctx.send(embed=embed)

# Comando para iniciar el reto entre dos jugadores
@bot.command()
async def reto(ctx, oponente: discord.Member):
    jugador1 = ctx.author
    jugador2 = oponente

    if not oponente:
        await ctx.send("¡Por favor menciona a un oponente para retarlo! Usa: `!reto @jugador`.")
        return

    if oponente.bot:
        await ctx.send("No puedes jugar contra un bot. ¡Busca un compañero humano! 🤖")
        return

    if oponente == jugador1:
        await ctx.send("¡No puedes jugar contigo mismo! 🤣")
        return

    await ctx.send(f"¡{jugador1.mention} ha retado a {jugador2.mention} a un Piedra, Papel o Tijeras! ¡Que comience el juego!")

    view1 = RetoEleccionView(jugador1)
    await ctx.send(f"{jugador1.mention}, elegí tu opción:", view=view1)
    await view1.wait()
    if view1.eleccion is None:
        await ctx.send("⏰ Tiempo agotado para el Jugador 1.")
        return

    view2 = RetoEleccionView(jugador2)
    await ctx.send(f"{jugador2.mention}, elegí tu opción:", view=view2)
    await view2.wait()
    if view2.eleccion is None:
        await ctx.send("⏰ Tiempo agotado para el Jugador 2.")
        return

    await ctx.send(f"🧑‍🎮 {jugador1.name} eligió: {view1.eleccion}")
    await ctx.send(f"🧑‍🎮 {jugador2.name} eligió: {view2.eleccion}")

    resultado = determinar_ganador(view1.eleccion, view2.eleccion)
    await ctx.send(f"🏆 Resultado: {resultado}")

# Comando para obtener la cotización del dolar
@bot.command()
async def dolar(ctx):
    await obtener_cotizacion_dolar(ctx)

# Comando para obtener el horoscopo
@bot.command()
async def horoscopo(ctx, signo: str = None):
    mensaje = obtener_horoscopo(signo)
    await ctx.send(mensaje)

#clima
@bot.command()
async def clima(ctx, *, ciudad: str): 
    await obtener_clima(ctx, ciudad)

#ruleta
@bot.command()
async def ruleta(ctx, tipo_apuesta: str = None, valor_apuesta: int = None):
    await manejar_comando_ruleta(ctx, tipo_apuesta, valor_apuesta)

#recargar
@bot.command()
async def recargar(ctx):
    usuario_id = str(ctx.author.id)
    saldo_actual = obtener_saldo(usuario_id)

    if saldo_actual > 0:
        await ctx.send(f"💰 Aún tienes saldo suficiente ({saldo_actual}). Solo puedes recargar cuando tu saldo sea 0.")
    else:
        actualizar_saldo(usuario_id, 100)
        await ctx.send("🔄 Tu saldo ha sido recargado con 100 monedas. ¡Buena suerte!")

#saldo
@bot.command()
async def saldo(ctx):
    usuario_id = str(ctx.author.id)
    saldo_actual = obtener_saldo(usuario_id)
    await ctx.send(f"💰 {ctx.author.mention}, tu saldo actual es de **{saldo_actual} monedas**.")

#payouts
@bot.command()
async def pagos(ctx):
    mensaje = (
        "**📊 pagos de la ruleta:**\n"
        "- Apostar a un **número exacto (0-36)**: x36\n"
        "- Apostar a **rojo o negro**: x2\n"
        "- Apostar a **par o impar**: x2\n"
        "Ejemplo: si apostás 100 monedas a 'rojo' y ganás, recibís 200 (100 tu apuesta + 100 ganancia)."
    )
    await ctx.send(mensaje)

#encuesta
@bot.command()
async def encuesta(ctx, *, raw: str = None):
       await crear_encuesta(ctx, raw)



#precio de criptomonedas
@bot.command(name="crypto")
async def crypto(ctx, moneda: str = None):
    if not moneda:
        return await ctx.send("❌ Indica una criptomoneda. Ejemplo: `!crypto bitcoin` o `!crypto btc`")
    res = await obtener_precio_coincap(moneda)
    if not res:
        return await ctx.send(f"❌ No encontré `{moneda}` en CoinCap.")
    id, sym, price = res
    await ctx.send(f"💱 **{sym.upper()}** (id:`{id}`) → **${price:,.2f} USD**")


#GLaDOS
@bot.event
async def on_member_join(member):
    await GLaDOS.on_member_join(member)

@bot.event
async def on_member_remove(member):
    await GLaDOS.on_member_remove(member)


@bot.command()
async def cake(ctx):
    await GLaDOS.comando_cake(ctx)


@bot.command(name="glados_info")
async def glados_info_command(ctx):
    await GLaDOS.glados_info(ctx)




#Error en los comandos
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("❌ Faltan argumentos para este comando. Escribe `!ayuda` para ver cómo usarlo.")
    elif isinstance(error, commands.CommandNotFound):
        await ctx.send("❌ Ese comando no existe. Usa `!ayuda` para ver la lista.")
    else:
        await ctx.send(f"⚠️ Ha ocurrido un error inesperado: `{str(error)}`")











#---------------------ESTO SIEMPRE VA AL FINAL-----------------------------------------------------

#mensaje si se menciona a GLaDOS en el chat
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # Evita activar si es un comando
    ctx = await bot.get_context(message)
    if ctx.valid:
        await bot.process_commands(message)
        return

    if "glados" in message.content.lower() or bot.user.mentioned_in(message):

        await GLaDOS.respuesta_mencion(message)

    await bot.process_commands(message)


# Iniciar el bot con el token correcto
bot.run(TOKEN)
