import os
import sys
import signal
import GLaDOS
import discord
import asyncio
import logging
import datetime
import codecs
from GLaDOS import GLaDOS
from comandos.ppyt import PPT
from dotenv import load_dotenv
from comandos.reto import Reto
from discord.ext import commands
from comandos.clima import Clima
from comandos.ayuda import Ayuda
from comandos.casino import Ruleta
from comandos.wordle import Wordle
from comandos.economia import Economia
from comandos.encuesta import Encuesta
from comandos.horoscopo import Horoscopo
from comandos.billetera import Billetera
from comandos.moderacion import Moderacion
from comandos.estadisticas import Estadisticas
from comandos.recomendador import Recomendador

#-------------------NO OLVIDAR ACTIVAR-------------------------

#                  botpy\Scripts\activate

#-------------------configuración del bot-----------------------

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Cargar variables de entorno
try:
    token = os.environ.get("DISCORD_TOKEN")
    if not token:
        load_dotenv(dotenv_path='C:\\Users\\ignac\\Desktop\\cosas PY\\discord\\Token.env')
        token = os.getenv("DISCORD_TOKEN")
        if not token:
            raise ValueError("No se encontró el token de Discord")
except Exception as e:
    print(f"❌ Error al cargar variables de entorno: {e}")
    sys.exit(1)

# Configurar los intents    
intents = discord.Intents.default()
intents.message_content = True
intents.members = True  
bot = commands.Bot(command_prefix="!", intents=intents)

#-------------------Eventos del bot-----------------------
@bot.event
async def on_ready():
    """Evento que se ejecuta cuando el bot se conecta exitosamente"""

    start_time = datetime.datetime.now()
    
    print(f'\n{"-"*40}')
    print(f'🔌 Bot conectado como: {bot.user.name} (ID: {bot.user.id})')
    print(f'🕒 Hora de conexión: {start_time.strftime("%Y-%m-%d %H:%M:%S")}')
    
    asyncio.create_task(update_bot_status())
    
    elapsed = (datetime.datetime.now() - start_time).total_seconds()
    print(f'⏱️ Tiempo de inicio: {elapsed:.2f} segundos')
    print(f'{"-"*40}\n')

async def update_bot_status():
    """Actualiza el estado del bot sin bloquear on_ready"""
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"!ayuda en {len(bot.guilds)} servidores"
        ),
        status=discord.Status.online
    )
    
    
    print(f'📊 Servidores: {len(bot.guilds)}')
    print(f'👥 Usuarios: {sum(g.member_count for g in bot.guilds)}')
    print(f'{"-"*40}\n')
    
    
    await bot.change_presence(
        activity=discord.Activity(
            type=discord.ActivityType.watching,
            name=f"pruebas para Aperture Science | !ayuda"
        ),
        status=discord.Status.online
    )

#-------------------Carga de módulos-----------------------
async def load_cogs():
    cogs_to_load = [
        ('GLaDOS', GLaDOS),
        ('comandos.ppyt', PPT),
        ('comandos.reto', Reto),
        ('comandos.ayuda', Ayuda),
        ('comandos.clima', Clima),
        ('comandos.casino', Ruleta),
        ('comandos.wordle', Wordle),
        ('comandos.encuesta', Encuesta),
        ('comandos.economia', Economia),
        ('comandos.billetera', Billetera),
        ('comandos.horoscopo', Horoscopo),
        ('comandos.moderacion', Moderacion),
        ('comandos.estadisticas', Estadisticas),
        ('comandos.recomendador', Recomendador),
    ]
    
    # Cargar cogs en paralelo para mejorar el tiempo de inicio
    tasks = []
    for cog_name, cog_class in cogs_to_load:
        tasks.append(load_cog(cog_name, cog_class))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    loaded = []
    failed = []
    
    for i, (cog_name, _) in enumerate(cogs_to_load):
        result = results[i]
        if isinstance(result, Exception):
            error_msg = f"{type(result).__name__}: {str(result)[:100]}"
            print(f'❌ {cog_name} - Error: {error_msg}')
            failed.append((cog_name, error_msg))
        else:
            print(f'✅ {cog_name} - Cargado correctamente')
            loaded.append(cog_name)
    
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

#-------------------Funciones auxiliares---------------------
async def load_cog(cog_name, cog_class):
    """Función auxiliar para cargar un cog individual"""
    await bot.add_cog(cog_class(bot))
    if not bot.get_cog(cog_class.__name__):
        raise Exception("El Cog no se registró correctamente")
    return True


#-------------------Función principal-----------------------
async def main():
   
    print("\n🚀 Iniciando bot...")
        
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s | %(levelname)s | %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )
    
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

# Arreglar la codificación de la consola para soportar emojis
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

#----------------------INICIO DEL BOT-----------------------

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

