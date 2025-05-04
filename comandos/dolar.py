import aiohttp

async def obtener_cotizacion_dolar(ctx):
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
