import os
import sys
import signal
import discord
import asyncio
import logging
import datetime
import codecs
import psutil
import time
import aiohttp
from GLaDOS import GLaDOS
from dotenv import load_dotenv
from functools import lru_cache
from discord.ext import commands
from comandos.clima import Clima
from comandos.ayuda import Ayuda
from comandos.casino import Ruleta
from comandos.wordle import Wordle
from comandos.economia import Economia
from comandos.encuesta import Encuesta
from comandos.horoscopo import Horoscopo
from comandos.billetera import Billetera
from comandos.casino import Ruleta, Dados
from comandos.juegos_ppt import JuegosPPT
from comandos.moderacion import Moderacion
from comandos.estadisticas import Estadisticas
from comandos.ahorcado import Ahorcado
from comandos.recomendador import Recomendador
from comandos.musica import Musica

#-------------------NO OLVIDAR ACTIVAR-------------------------

#                  botpy\Scripts\activate




class PerformanceMonitor:
    def __init__(self, log_interval=300):  
        self.process = psutil.Process(os.getpid())
        self.start_time = time.time()
        self.log_interval = log_interval
        self.last_log_time = 0
        
    def get_memory_usage(self):
        """Obtiene el uso de memoria en MB"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def get_cpu_usage(self):
        """Obtiene el uso de CPU en porcentaje"""
        return self.process.cpu_percent(interval=0.1)
    
    def get_uptime(self):
        """Obtiene el tiempo de actividad en segundos"""
        return time.time() - self.start_time
    
    def log_metrics(self, force=False):
        """Registra las métricas de rendimiento"""
        current_time = time.time()
        if force or (current_time - self.last_log_time) >= self.log_interval:
            memory_mb = self.get_memory_usage()
            cpu_percent = self.get_cpu_usage()
            uptime_hours = self.get_uptime() / 3600
            
            logging.info(f"Rendimiento: RAM: {memory_mb:.2f} MB | CPU: {cpu_percent:.1f}% | Uptime: {uptime_hours:.2f} horas")
            
            self.last_log_time = current_time
            return True
        return False

performance_monitor = PerformanceMonitor()



#-------------------configuración del bot-----------------------

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

session = None

cache = {}

try:
    load_dotenv()
    token = os.getenv("DISCORD_TOKEN")
    
    if not token:
        load_dotenv(dotenv_path='C:\\Users\\ignac\\Desktop\\cosas PY\\discord\\Token.env')
        token = os.getenv("DISCORD_TOKEN")
        
    if not token:
        raise ValueError("No se encontró el token de Discord")
except Exception as e:
    print(f"❌ Error al cargar variables de entorno: {e}")
    sys.exit(1)

intents = discord.Intents.default()
intents.message_content = True
intents.members = True  
bot = commands.Bot(command_prefix="!", intents=intents)

#-------------------Eventos del bot-----------------------
@bot.event
async def on_ready():
    global session
    session = aiohttp.ClientSession()
    
    start_time = datetime.datetime.now()
    
    print(f'\n{"-"*40}')
    print(f'🔌 Bot conectado como: {bot.user.name} (ID: {bot.user.id})')
    print(f'🕒 Hora de conexión: {start_time.strftime("%Y-%m-%d %H:%M:%S")}')
    
    asyncio.create_task(update_bot_status())
    asyncio.create_task(monitor_performance_task())
    
    elapsed = (datetime.datetime.now() - start_time).total_seconds()
    print(f'⏱️ Tiempo de inicio: {elapsed:.2f} segundos')
    print(f'{"-"*40}\n')

@bot.event
async def on_disconnect():
    if session and not session.closed:
        await session.close()

async def monitor_performance_task():
    """Tarea para monitorear el rendimiento periódicamente"""
    while True:
        performance_monitor.log_metrics()
        if performance_monitor.get_memory_usage() > 200:
            clear_cache()
            logging.info("Caché limpiado debido a alto uso de memoria")
        await asyncio.sleep(60)  

def clear_cache():
    """Limpia la caché global"""
    cache.clear()
    for func in [get_guild_data, get_user_data]:
        if hasattr(func, "cache_clear"):
            func.cache_clear()

async def update_bot_status():
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
        ('comandos.ayuda', Ayuda),
        ('comandos.clima', Clima),
        ('comandos.casino', Ruleta),
        ('comandos.casino', Dados),
        ('comandos.wordle', Wordle),
        ('comandos.musica', Musica),
        ('comandos.ahorcado', Ahorcado),
        ('comandos.encuesta', Encuesta),
        ('comandos.economia', Economia),
        ('comandos.billetera', Billetera),
        ('comandos.horoscopo', Horoscopo),
        ('comandos.juegos_ppt', JuegosPPT),
        ('comandos.moderacion', Moderacion),
        ('comandos.estadisticas', Estadisticas),
        ('comandos.recomendador', Recomendador),
    ]
    
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
    
    print("\n" + "="*50)
    print(f"📦 Resumen de carga:")
    print(f"🟢 Cogs cargados: {len(loaded)}")
    print(f"🔴 Cogs fallidos: {len(failed)}")
    
    if failed:
        print("\nErrores detallados:")
        for cog, error in failed:
            print(f"• {cog}: {error}")
    
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
    try:
        await bot.add_cog(cog_class(bot))
        if not bot.get_cog(cog_class.__name__):
            raise Exception("El Cog no se registró correctamente")
        return True
    except Exception as e:
        return e

#-------------------Funciones de caché-----------------------
@lru_cache(maxsize=100)
def get_guild_data(guild_id):
    """Obtiene datos de un servidor con caché"""
    return {"id": guild_id, "cached": True}

@lru_cache(maxsize=1000)
def get_user_data(user_id):
    """Obtiene datos de un usuario con caché"""
    return {"id": user_id, "cached": True}

async def fetch_url(url, headers=None, params=None):
    """Realiza una petición HTTP usando aiohttp"""
    if url in cache:
        if time.time() - cache[url]["timestamp"] < 1800:
            return cache[url]["data"]
    
    if not session or session.closed:
        return None
    
    try:
        async with session.get(url, headers=headers, params=params) as response:
            if response.status == 200:
                data = await response.json()
                # Guardar en caché
                cache[url] = {
                    "data": data,
                    "timestamp": time.time()
                }
                return data
            else:
                logging.warning(f"Error en petición HTTP: {response.status} - {url}")
                return None
    except Exception as e:
        logging.error(f"Error al hacer petición HTTP: {str(e)}")
        return None

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
    
    performance_monitor.log_metrics(force=True)
    
    success = await load_cogs()
    if not success:
        print("\n⚠️ Algunos módulos no cargaron correctamente")
    
    try:
        await bot.start(token) 
    except discord.LoginFailure:
        print("❌ Error de autenticación: Token inválido")
        return
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido manualmente")
    except Exception as e:
        print(f"\n💥 Error crítico: {type(e).__name__}: {e}")
        logging.critical(f"Error crítico: {type(e).__name__}: {e}")
    finally:
        performance_monitor.log_metrics(force=True)
        
        if session and not session.closed:
            await session.close()
            
        if not bot.is_closed():
            await bot.close()
        print("\n🔌 Desconectando...")

#----------------------INICIO DEL BOT-----------------------

if __name__ == "__main__":
    sys.excepthook = lambda exc_type, exc_value, exc_traceback: (
        logging.error("Excepción no capturada", exc_info=(exc_type, exc_value, exc_traceback))
        if not issubclass(exc_type, KeyboardInterrupt) else None
    )
    
    if sys.platform == 'win32':
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Bot detenido manualmente")
    except Exception as e:
        logging.critical(f"ERROR: {type(e).__name__}: {e}")

