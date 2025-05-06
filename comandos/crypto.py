import os, aiohttp
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv(dotenv_path='C:\\Users\\ignac\\Desktop\\cosas PY\\discord\\Token.env')
API_KEY = os.getenv("API_COINCAP")  

BASE = "https://rest.coincap.io/v3/assets/{id}?apiKey=" + API_KEY
SEARCH = "https://rest.coincap.io/v3/assets?search={query}&apiKey=" + API_KEY

class Crypto(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    @commands.command(name="crypto")
    async def crypto(self, ctx, moneda: str = None):
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
    await bot.add_cog(Crypto(bot))
