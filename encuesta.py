import discord

# Emojis del 1️⃣ al 🔟
EMOJIS = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]

async def crear_encuesta(ctx, raw: str = None):
    # Si no vino nada o no hay separador |
    if not raw or "|" not in raw:
        await ctx.send(
            "❌ **Uso incorrecto de `!encuesta`**\n\n"
            "Debes separar la pregunta y las opciones con `|`.\n"
            "Formato:\n"
            "`!encuesta pregunta | opción1 | opción2 [| opción3 ... opción10]`\n\n"
            "Ejemplo:\n"
            "`!encuesta ¿Pizza o empanadas? | Pizza | Empanadas`"
        )
        return

    parts = [p.strip() for p in raw.split("|")]
    pregunta, opciones = parts[0], parts[1:]

    if len(opciones) < 2:
        await ctx.send("❌ Debes dejar al menos 2 opciones. Máximo 10.\n`!encuesta pregunta | o1 | o2 [| o3 ...]`")
        return
    if len(opciones) > 10:
        await ctx.send("❌ Máximo 10 opciones permitidas.")
        return

    embed = discord.Embed(
        title="📊 " + pregunta,
        description="\n".join(f"{EMOJIS[i]} {opt}" for i, opt in enumerate(opciones)),
        color=discord.Color.green()
    )
    embed.set_footer(text=f"Encuesta por {ctx.author.display_name}")

    mensaje = await ctx.send(embed=embed)
    for i in range(len(opciones)):
        await mensaje.add_reaction(EMOJIS[i])
