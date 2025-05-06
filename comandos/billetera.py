import os
import aiohttp
from discord.ext import commands
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(dotenv_path='C:\\Users\\ignac\\Desktop\\cosas PY\\discord\\Token.env')
API_KEY = os.getenv("API_COINCAP")  

# URLs para la API de CoinCap
BASE = "https://rest.coincap.io/v3/assets/{id}?apiKey=" + API_KEY
SEARCH = "https://rest.coincap.io/v3/assets?search={query}&apiKey=" + API_KEY

class Billetera(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="dolar")
    async def dolar(self, ctx):
        """Muestra la cotización del dólar en Argentina"""
        url = "https://dolarapi.com/v1/dolares"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status != 200:
                        await ctx.send("⚠️ No se pudo obtener la cotización del dólar.")
                        return

                    data = await response.json()
                    cotizaciones = {item['casa']: item for item in data}

                    oficial = cotizaciones.get("oficial")
                    blue = cotizaciones.get("blue")
                    tarjeta = cotizaciones.get("tarjeta")
                    cripto = cotizaciones.get("cripto")
                    ccl = cotizaciones.get("contadoconliqui")

                    if not all([oficial, blue, tarjeta, cripto, ccl]):
                        await ctx.send("⚠️ No se encontraron todas las cotizaciones necesarias.")
                        return

                    mensaje = (
                        "💵 **Cotización del dólar hoy en Argentina**\n\n"
                        f"🏛️ **Oficial**: Compra ${oficial['compra']} / Venta ${oficial['venta']}\n"
                        f"🧢 **Blue**: Compra ${blue['compra']} / Venta ${blue['venta']}\n"
                        f"💳 **Tarjeta**: Compra ${tarjeta['compra']} / Venta ${tarjeta['venta']}\n"
                        f"🪙 **Cripto**: Compra ${cripto['compra']} / Venta ${cripto['venta']}\n"
                        f"📈 **CCL**: Compra ${ccl['compra']} / Venta ${ccl['venta']}"
                    )
                    await ctx.send(mensaje)
        except Exception as e:
            await ctx.send("🚨 Ocurrió un error al obtener los datos.")
            print(f"Error: {e}")

    @commands.command(name="crypto")
    async def crypto(self, ctx, moneda: str = None):
        """Muestra el precio de una criptomoneda"""
        if not moneda:
            return await ctx.send("❌ Indica una criptomoneda. Ejemplo: `!crypto bitcoin` o `!crypto btc`")
        res = await self.obtener_precio_coincap(moneda)
        if not res:
            return await ctx.send(f"❌ No encontré `{moneda}` en CoinCap.")
        id, sym, price = res
        await ctx.send(f"💱 **{sym.upper()}** (id:`{id}`) → **${price:,.2f} USD**")
    
    async def obtener_precio_coincap(self, query: str):
        """
        Intenta obtener (id,symbol,priceUsd) de:
          1) GET /v3/assets/{id}
          2) GET /v3/assets?search={query}
        """
        async with aiohttp.ClientSession() as s:
            # 1) por id
            url = BASE.format(id=query.lower())
            r = await s.get(url)
            if r.status == 200:
                j = await r.json()
                d = j.get("data")
                if d and "priceUsd" in d:
                    return d["id"], d["symbol"], float(d["priceUsd"])
            # 2) por search
            url = SEARCH.format(query=query)
            r = await s.get(url)
            if r.status != 200:
                return None
            arr = (await r.json()).get("data", [])
            if not arr:
                return None
            first = arr[0]
            return first["id"], first["symbol"], float(first["priceUsd"])

async def setup(bot):
    await bot.add_cog(Billetera(bot))