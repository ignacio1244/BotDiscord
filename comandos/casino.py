import random
from casino_saldos import obtener_saldo, actualizar_saldo

colores = {
    "rojo": [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36],
    "negro": [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]
}

async def manejar_comando_ruleta(ctx, tipo_apuesta, valor_apuesta):
    usuario_id = str(ctx.author.id)

    if not tipo_apuesta or valor_apuesta is None:
        await ctx.send("❌ Uso incorrecto. Ejemplo: `!ruleta rojo 100` o `!ruleta 17 50`.")
        return

    saldo = obtener_saldo(usuario_id)
    if valor_apuesta <= 0:
        await ctx.send("⚠️ La apuesta debe ser mayor a 0.")
        return

    if saldo < valor_apuesta:
        await ctx.send(f"💸 No tienes saldo suficiente. Tu saldo actual es {saldo}.")
        return
    
    if tipo_apuesta.isdigit():
        numero_apuesta = int(tipo_apuesta)
        if numero_apuesta < 0 or numero_apuesta > 36:
            await ctx.send(f"{ctx.author.mention} el número debe estar entre 0 y 36.")
            return

    numero_ganador = random.randint(0, 36)
    resultado = f"🎡 La ruleta giró y cayó en el número **{numero_ganador}**.\n"
    ganancia = 0

    if tipo_apuesta.isdigit():  # Apuesta a número exacto
        if int(tipo_apuesta) == numero_ganador:
            ganancia = valor_apuesta * 36
            resultado += f"🎉 ¡Ganaste! Apostaste al número exacto y ganás {ganancia} monedas."
        else:
            resultado += "😢 No acertaste el número exacto."
    elif tipo_apuesta.lower() in ["rojo", "negro"]:
        if numero_ganador in colores[tipo_apuesta.lower()]:
            ganancia = valor_apuesta * 2
            resultado += f"🎉 ¡Ganaste! Acertaste el color y ganás {ganancia} monedas."
        else:
            resultado += "😢 No acertaste el color."
    elif tipo_apuesta.lower() in ["par", "impar"]:
        if numero_ganador == 0:
            resultado += "😢 Cayó el 0, no es ni par ni impar. Perdiste."
        elif (numero_ganador % 2 == 0 and tipo_apuesta.lower() == "par") or \
             (numero_ganador % 2 == 1 and tipo_apuesta.lower() == "impar"):
            ganancia = valor_apuesta * 2
            resultado += f"🎉 ¡Ganaste! Acertaste par/impar y ganás {ganancia} monedas."
        else:
            resultado += "😢 No acertaste par/impar."
    else:
        await ctx.send("❌ Tipo de apuesta inválido. Usa un número (0-36), 'rojo', 'negro', 'par' o 'impar'.")
        return

    # Actualizar saldo
    nuevo_saldo = saldo - valor_apuesta + ganancia
    actualizar_saldo(usuario_id, nuevo_saldo)

    resultado += f"\n💰 Tu nuevo saldo es: {nuevo_saldo} monedas."
    await ctx.send(resultado)
