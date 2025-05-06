import random
import json
import os
from pathlib import Path
import discord
from discord.ext import commands

class CasinoManager:
    def __init__(self):
        self.data_path = Path("utils/saldos_casino.json")
        self._ensure_data_file()

    def _ensure_data_file(self):
        """Crea el archivo si no existe"""
        self.data_path.parent.mkdir(exist_ok=True)
        if not self.data_path.exists():
            with open(self.data_path, 'w') as f:
                json.dump({}, f)

    def obtener_saldo(self, usuario_id):
        try:
            with open(self.data_path, 'r') as f:
                return json.load(f).get(str(usuario_id), 100)
        except (FileNotFoundError, json.JSONDecodeError):
            return 100

    def actualizar_saldo(self, usuario_id, monto):
        try:
            with open(self.data_path, 'r') as f:
                data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}
        
        data[str(usuario_id)] = monto
        
        with open(self.data_path, 'w') as f:
            json.dump(data, f, indent=4)

# Crear una instancia del administrador de casino
casino_manager = CasinoManager()

colores = {
    "rojo": [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36],
    "negro": [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]
}

class Ruleta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def obtener_color_numero(self, numero):
        """Determina el color del número ganador"""
        if numero == 0:
            return "verde (0)"
        for color, numeros in colores.items():
            if numero in numeros:
                return color
        return ""

    @commands.command(name="ruleta")
    async def manejar_comando_ruleta(self, ctx, tipo_apuesta: str = None, valor_apuesta: int = None):
        """Juega a la ruleta con diferentes tipos de apuestas"""
        usuario_id = str(ctx.author.id)
        saldo = casino_manager.obtener_saldo(usuario_id)

        
        if not tipo_apuesta or valor_apuesta is None:
            embed = discord.Embed(
                title="❌ Uso incorrecto",
                description="Ejemplo: `!ruleta rojo 100` o `!ruleta 17 50`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        if valor_apuesta <= 0:
            await ctx.send("⚠️ La apuesta debe ser mayor a 0.")
            return

        if saldo < valor_apuesta:
            embed = discord.Embed(
                title="💸 Saldo insuficiente",
                description=f"Tu saldo actual es {saldo} monedas",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return
        
        
        if tipo_apuesta.isdigit():
            numero_apuesta = int(tipo_apuesta)
            if numero_apuesta < 0 or numero_apuesta > 36:
                await ctx.send(f"{ctx.author.mention} El número debe estar entre 0 y 36.")
                return

        
        numero_ganador = random.randint(0, 36)
        color_ganador = self.obtener_color_numero(numero_ganador)
        
        
        resultado = f"🎡 La ruleta giró y cayó en el **{numero_ganador} {color_ganador}**.\n"
        ganancia = 0

        
        if tipo_apuesta.isdigit():  
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
            embed = discord.Embed(
                title="❌ Apuesta inválida",
                description="Usa un número (0-36), 'rojo', 'negro', 'par' o 'impar'",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        
        nuevo_saldo = saldo - valor_apuesta + ganancia
        casino_manager.actualizar_saldo(usuario_id, nuevo_saldo)

        embed = discord.Embed(
            title="🎡 Resultado de la ruleta",
            description=resultado,
            color=discord.Color.green() if ganancia > 0 else discord.Color.red()
        )
        embed.add_field(name="💰 Nuevo saldo", value=f"{nuevo_saldo} monedas", inline=False)
        embed.set_footer(text=f"Apuesta: {valor_apuesta} monedas")
        
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Ruleta(bot))