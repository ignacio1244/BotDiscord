import os
import sys
import discord
import GLaDOS
import asyncio
import logging
import datetime
import signal
from comandos.moderacion import borrar_mensajes
from comandos.ppyt import jugar_partida
from dotenv import load_dotenv
from discord.ext import commands
from comandos.dolar import obtener_cotizacion_dolar
from comandos.casino_saldos import casino_manager 
from comandos.reto import Reto
from comandos.horoscopo import obtener_horoscopo
from comandos.clima import obtener_clima
from comandos.casino import Ruleta
from comandos.encuesta import Encuesta
from comandos.crypto import obtener_precio_coincap    
from GLaDOS import GLaDOS 
from comandos.estadisticas_comando import Estadisticas
from comandos.recargar import Recargar
from comandos.ayuda import Ayuda

#no olvidar botpy\Scripts\activate

#-------------------configuración del bot-----------------------

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv(dotenv_path='C:\\Users\\ignac\\Desktop\\cosas PY\\discord\\Token.env')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    """Evento que se ejecuta cuando el bot se conecta exitosamente"""
    print(f'\n{"-"*40}')
    print(f'🔌 Bot conectado como: {bot.user.name} (ID: {bot.user.id})')
    print(f'🕒 Hora de conexión: {datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'📊 Servidores: {len(bot.guilds)}')
    print(f'👥 Usuarios: {sum(g.member_count for g in bot.guilds)}')
    print(f'{"-"*40}\n')
    
    #cambiar el estado del bot
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"!ayuda en {len(bot.guilds)} servidores"
        ),
        status=discord.Status.online
    )

async def load_cogs():
    
    cogs_to_load = [
        ('comandos.recargar', Recargar),
        ('comandos.estadisticas', Estadisticas),
        ('comandos.casino', Ruleta),
        ('GLaDOS', GLaDOS),
        ('comandos.encuesta', Encuesta),
        ('comandos.ayuda', Ayuda),
        ('comandos.reto', Reto),
    ]
    
    loaded = []
    failed = []
    
    print("\n🔧 Cargando módulos:")
    max_name_len = max(len(name) for name, _ in cogs_to_load)
    
    for cog_name, cog_class in cogs_to_load:
        try:
            # Intenta cargar el Cog
            await bot.add_cog(cog_class(bot))
            
            # Verificación adicional
            if bot.get_cog(cog_class.__name__):
                print(f'✅ {cog_name.ljust(max_name_len)} - Cargado correctamente')
                loaded.append(cog_name)
            else:
                raise Exception("El Cog no se registró correctamente")
                
        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)[:100]}"
            print(f'❌ {cog_name.ljust(max_name_len)} - Error: {error_msg}')
            failed.append((cog_name, error_msg))
    
    # Resumen de carga
    print("\n" + "="*50)
    print(f"📦 Resumen de carga:")
    print(f"🟢 Cogs cargados: {len(loaded)}")
    print(f"🔴 Cogs fallidos: {len(failed)}")
    
    if failed:
        print("\nErrores detallados:")
        for cog, error in failed:
            print(f"• {cog}: {error}")
    
    # Verificación de comandos duplicados
    all_commands = [cmd.name for cmd in bot.commands]
    duplicates = set([cmd for cmd in all_commands if all_commands.count(cmd) > 1])
    
    if duplicates:
        print("\n⚠️ Advertencia: Comandos duplicados detectados:")
        for cmd in duplicates:
            print(f"• {cmd}")
    
    return len(failed) == 0  

async def main():
    """Función principal de inicio del bot"""
    print("\n🚀 Iniciando bot...")
    
    # Configurar logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )
    
    # Cargar módulos
    success = await load_cogs()
    
    if not success:
        print("\n⚠️ Algunos módulos no cargaron correctamente")
    
    try:
        await bot.start(os.getenv("DISCORD_TOKEN"))
    except discord.LoginFailure:
        print("❌ Error de autenticación: Token inválido")
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido manualmente")
    except Exception as e:
        print(f"\n💥 Error crítico: {type(e).__name__}: {e}")
    finally:
        print("\n🔌 Desconectando...")
        if not bot.is_closed():
            await bot.close()

#-----------------------------comandos-----------------------------------------------------


# Comando para borrar mensajes
@bot.command()
async def borrar(ctx, cantidad: int = 5):
    await borrar_mensajes(ctx, cantidad)

# Comando para jugar piedra, papel o tijeras (user vs bot)
@bot.command()
async def ppt(ctx):
    jugador = ctx.author
    await jugar_partida(ctx, jugador)  


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

#saldo
@bot.command()
async def saldo(ctx):
    usuario_id = str(ctx.author.id)
    saldo_actual = casino_manager.obtener_saldo(usuario_id)
    await ctx.send(f"💰 {ctx.author.mention}, tu saldo actual es de **{saldo_actual} monedas**.")

#pagos
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














#---------------------inicio del bot-----------------------------------------------------

if __name__ == "__main__":
    def handle_exception(exc_type, exc_value, exc_traceback):
        if not issubclass(exc_type, KeyboardInterrupt):
            logging.error("Excepción no capturada", exc_info=(exc_type, exc_value, exc_traceback))
    
    sys.excepthook = handle_exception

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido manualmente")
        # Asegurar cierre limpio
        asyncio.run(bot.close()) if not bot.is_closed() else None
    except Exception as e:
        logging.critical(f"ERROR: {type(e).__name__}: {e}")