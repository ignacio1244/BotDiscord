import os
import sys
import signal
import GLaDOS
import discord
import asyncio
import logging
import datetime
from GLaDOS import GLaDOS
from dotenv import load_dotenv
from comandos.reto import Reto
from discord.ext import commands
from comandos.dolar import Dolar
from comandos.clima import Clima
from comandos.ayuda import Ayuda
from comandos.casino import Ruleta
from comandos.crypto import Crypto
from comandos.musica import Musica
from comandos.economia import Economia
from comandos.encuesta import Encuesta
from comandos.horoscopo import Horoscopo
from comandos.moderacion import Moderacion
from comandos.ppyt import PiedraPapelTijeras
from comandos.estadisticas_comando import Estadisticas

#-------------------NO OLVIDAR ACTIVAR-----------------------

#                  botpy\Scripts\activate

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
        
        
        ('GLaDOS', GLaDOS),
        ('comandos.reto', Reto),
        ('comandos.ayuda', Ayuda),
        ('comandos.dolar', Dolar),
        ('comandos.clima', Clima),
        ('comandos.casino', Ruleta),
        ('comandos.crypto', Crypto),
        ('comandos.musica', Musica),
        ('comandos.encuesta', Encuesta),
        ('comandos.economia', Economia),
        ('comandos.horoscopo', Horoscopo),
        ('comandos.moderacion', Moderacion),
        ('comandos.ppyt', PiedraPapelTijeras),
        ('comandos.estadisticas', Estadisticas),


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


















#-------------------------INICIO DEL BOT-------------------------------------------------

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