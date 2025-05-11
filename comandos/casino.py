import random
import json
import os
from pathlib import Path
import discord
from discord.ext import commands
import sys
from comandos.estadisticas import EstadisticasManager

sys.path.append(str(Path(__file__).parent.parent))


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
                data = json.load(f)
                return data.get(str(usuario_id), 100)
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

casino_manager = CasinoManager()

colores = {
    "rojo": [1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36],
    "negro": [2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35]
}

class Ruleta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stats_manager = EstadisticasManager()

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

        stats = self.stats_manager.obtener_estadisticas(ctx.author.id)
        stats["ruleta"]["apuestas_totales"] += 1
        self.stats_manager.guardar_estadisticas(ctx.author.id, stats)
        
        if tipo_apuesta.isdigit():  
            if int(tipo_apuesta) == numero_ganador:
                ganancia = valor_apuesta * 36
                resultado += f"🎉 ¡Ganaste! Apostaste al número exacto y ganás {ganancia} monedas."
                # Calcular ganancia neta (ganancia - apuesta)
                ganancia_neta = ganancia - valor_apuesta
                self.stats_manager.actualizar_estadisticas_ruleta(ctx.author.id, ganancia_neta)
            else:
                resultado += "😢 No acertaste el número exacto."
                self.stats_manager.actualizar_estadisticas_ruleta(ctx.author.id, -valor_apuesta)
        elif tipo_apuesta.lower() in ["rojo", "negro"]:
            if numero_ganador in colores[tipo_apuesta.lower()]:
                ganancia = valor_apuesta * 2
                resultado += f"🎉 ¡Ganaste! Acertaste el color y ganás {ganancia} monedas."
                # Calcular ganancia neta (ganancia - apuesta)
                ganancia_neta = ganancia - valor_apuesta
                self.stats_manager.registrar_ganancia_ruleta(ctx.author.id, ganancia_neta)
            else:
                resultado += "😢 No acertaste el color."
                self.stats_manager.registrar_perdida_ruleta(ctx.author.id, valor_apuesta)
        elif tipo_apuesta.lower() in ["par", "impar"]:
            if numero_ganador == 0:
                resultado += "😢 Cayó el 0, no es ni par ni impar. Perdiste."
                self.stats_manager.registrar_perdida_ruleta(ctx.author.id, valor_apuesta)
            elif (numero_ganador % 2 == 0 and tipo_apuesta.lower() == "par") or \
                 (numero_ganador % 2 == 1 and tipo_apuesta.lower() == "impar"):
                ganancia = valor_apuesta * 2
                resultado += f"🎉 ¡Ganaste! Acertaste par/impar y ganás {ganancia} monedas."
                # Calcular ganancia neta (ganancia - apuesta)
                ganancia_neta = ganancia - valor_apuesta
                self.stats_manager.registrar_ganancia_ruleta(ctx.author.id, ganancia_neta)
            else:
                resultado += "😢 No acertaste par/impar."
                self.stats_manager.registrar_perdida_ruleta(ctx.author.id, valor_apuesta)
        
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


class Dados(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stats_manager = EstadisticasManager()
        self.desafios_pendientes = {}  
        
    @commands.command(name="dado", aliases=["dados"])
    async def jugar_dados(self, ctx, valor_apuesta: int = None, usuario_retado: discord.Member = None):
        """
        Juega a los dados contra el bot o desafía a otro usuario
        Uso: !dado [apuesta] -> Juega contra el bot
             !dado [apuesta] @usuario -> Desafía a otro usuario
        """
        # Verificar que se proporcionó una apuesta
        if valor_apuesta is None:
            embed = discord.Embed(
                title="❌ Uso incorrecto",
                description="Ejemplo: `!dado 100` o `!dado 100 @usuario`",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
            return

        # Verificar que la apuesta sea válida
        if valor_apuesta <= 0:
            await ctx.send("⚠️ La apuesta debe ser mayor a 0.")
            return

        # Verificar que el usuario tenga saldo suficiente
        usuario_id = str(ctx.author.id)
        saldo = casino_manager.obtener_saldo(usuario_id)
        
        if saldo < valor_apuesta:
            embed = discord.Embed(
                title="💸 Saldo insuficiente",
                description=f"Tu saldo actual es {saldo} monedas",
                color=discord.Color.orange()
            )
            await ctx.send(embed=embed)
            return

        # Si no se especificó un usuario, jugar contra el bot
        if usuario_retado is None:
            await self.jugar_contra_bot(ctx, valor_apuesta)
        else:
            # Verificar que no se esté retando a sí mismo
            if usuario_retado.id == ctx.author.id:
                await ctx.send("❌ No puedes retarte a ti mismo.")
                return
                
            # Verificar que no se esté retando al bot
            if usuario_retado.bot:
                await ctx.send("❌ No puedes retar a un bot. Usa `!dado [apuesta]` para jugar contra el bot.")
                return
                
            # Verificar que el usuario retado tenga saldo suficiente
            saldo_retado = casino_manager.obtener_saldo(str(usuario_retado.id))
            if saldo_retado < valor_apuesta:
                await ctx.send(f"❌ {usuario_retado.mention} no tiene suficiente saldo para aceptar este desafío.")
                return
                
            # Crear el desafío
            await self.crear_desafio(ctx, usuario_retado, valor_apuesta)

    async def jugar_contra_bot(self, ctx, valor_apuesta):
        """Juega a los dados contra el bot"""
        # Lanzar los dados
        dado_usuario = random.randint(1, 6) + random.randint(1, 6)
        dado_bot = random.randint(1, 6) + random.randint(1, 6)
        
        # Determinar el resultado
        if dado_usuario > dado_bot:
            resultado = "victoria"
            ganancia = valor_apuesta
            color = discord.Color.green()
            mensaje = f"🎲 ¡Ganaste! Tus dados suman **{dado_usuario}** vs **{dado_bot}** del bot."
        elif dado_usuario < dado_bot:
            resultado = "derrota"
            ganancia = -valor_apuesta
            color = discord.Color.red()
            mensaje = f"🎲 Perdiste. Tus dados suman **{dado_usuario}** vs **{dado_bot}** del bot."
        else:
            resultado = "empate"
            ganancia = 0
            color = discord.Color.gold()
            mensaje = f"🎲 Empate. Ambos sacaron **{dado_usuario}**."
        
        # Actualizar estadísticas y saldo
        if resultado != "empate":
            # Actualizar estadísticas (asumiendo que tienes un método para dados)
            stats = self.stats_manager.obtener_estadisticas(ctx.author.id)
            if "dados" not in stats:
                stats["dados"] = {"victorias": 0, "derrotas": 0}
            
            if resultado == "victoria":
                stats["dados"]["victorias"] = stats["dados"].get("victorias", 0) + 1
            else:
                stats["dados"]["derrotas"] = stats["dados"].get("derrotas", 0) + 1
                
            self.stats_manager.guardar_estadisticas(ctx.author.id, stats)
            
            # Actualizar saldo
            nuevo_saldo = casino_manager.obtener_saldo(str(ctx.author.id)) + ganancia
            casino_manager.actualizar_saldo(str(ctx.author.id), nuevo_saldo)
        else:
            nuevo_saldo = casino_manager.obtener_saldo(str(ctx.author.id))
        
        # Crear y enviar el embed
        embed = discord.Embed(
            title="🎲 Resultado de los Dados",
            description=mensaje,
            color=color
        )
        
        embed.add_field(name="Tu tirada", value=f"🎲 {dado_usuario}", inline=True)
        embed.add_field(name="Tirada del bot", value=f"🎲 {dado_bot}", inline=True)
        embed.add_field(name="💰 Nuevo saldo", value=f"{nuevo_saldo} monedas", inline=False)
        
        if resultado != "empate":
            embed.add_field(
                name="Resultado", 
                value=f"{'Ganaste' if resultado == 'victoria' else 'Perdiste'} {abs(ganancia)} monedas", 
                inline=False
            )
        
        embed.set_footer(text=f"Apuesta: {valor_apuesta} monedas")
        
        await ctx.send(embed=embed)

    async def crear_desafio(self, ctx, usuario_retado, valor_apuesta):
        """Crea un desafío para otro usuario"""
        # Crear botones para aceptar o rechazar
        class BotonesDesafio(discord.ui.View):
            def __init__(self, cog, timeout=60):
                super().__init__(timeout=timeout)
                self.cog = cog
                self.valor = None
            
            @discord.ui.button(label="Aceptar", style=discord.ButtonStyle.green)
            async def aceptar(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != usuario_retado.id:
                    await interaction.response.send_message("❌ Solo el usuario retado puede responder.", ephemeral=True)
                    return
                
                self.valor = True
                self.stop()
                await interaction.response.defer()
            
            @discord.ui.button(label="Rechazar", style=discord.ButtonStyle.red)
            async def rechazar(self, interaction: discord.Interaction, button: discord.ui.Button):
                if interaction.user.id != usuario_retado.id:
                    await interaction.response.send_message("❌ Solo el usuario retado puede responder.", ephemeral=True)
                    return
                
                self.valor = False
                self.stop()
                await interaction.response.defer()
            
            async def on_timeout(self):
                self.valor = None
                self.stop()
        
        # Crear y enviar el mensaje de desafío
        embed = discord.Embed(
            title="🎲 Desafío de Dados",
            description=f"{ctx.author.mention} te desafía a un juego de dados por **{valor_apuesta}** monedas.\n\n"
                       f"Cada jugador lanzará 2 dados de 6 caras. El que saque el número más alto gana.",
            color=discord.Color.blue()
        )
        
        embed.add_field(name="Apuesta", value=f"{valor_apuesta} monedas", inline=True)
        embed.add_field(name="Tiempo para responder", value="60 segundos", inline=True)
        embed.set_footer(text="Presiona un botón para responder al desafío")
        
        view = BotonesDesafio(self)
        mensaje = await ctx.send(content=f"{usuario_retado.mention}", embed=embed, view=view)
        
        # Esperar respuesta
        await view.wait()
        
        # Procesar respuesta
        if view.valor is None:
            await mensaje.edit(
                embed=discord.Embed(
                    title="⏱️ Desafío expirado",
                    description=f"{usuario_retado.mention} no respondió al desafío a tiempo.",
                    color=discord.Color.dark_gray()
                ),
                view=None
            )
        elif view.valor is False:
            await mensaje.edit(
                embed=discord.Embed(
                    title="❌ Desafío rechazado",
                    description=f"{usuario_retado.mention} ha rechazado el desafío.",
                    color=discord.Color.red()
                ),
                view=None
            )
        else:
            await mensaje.edit(
                embed=discord.Embed(
                    title="✅ Desafío aceptado",
                    description=f"{usuario_retado.mention} ha aceptado el desafío. ¡Lanzando los dados!",
                    color=discord.Color.green()
                ),
                view=None
            )
            
            # Jugar la partida
            await self.jugar_entre_usuarios(ctx, ctx.author, usuario_retado, valor_apuesta)
    
    async def jugar_entre_usuarios(self, ctx, usuario1, usuario2, valor_apuesta):
        """Juega una partida de dados entre dos usuarios"""
        # Lanzar los dados
        dado_usuario1 = random.randint(1, 6) + random.randint(1, 6)
        dado_usuario2 = random.randint(1, 6) + random.randint(1, 6)
        
        # Determinar el resultado
        if dado_usuario1 > dado_usuario2:
            ganador = usuario1
            perdedor = usuario2
            dado_ganador = dado_usuario1
            dado_perdedor = dado_usuario2
        elif dado_usuario1 < dado_usuario2:
            ganador = usuario2
            perdedor = usuario1
            dado_ganador = dado_usuario2
            dado_perdedor = dado_usuario1
        else:
            # En caso de empate
            embed = discord.Embed(
                title="🎲 Empate en el Desafío de Dados",
                description=f"¡Empate! Ambos jugadores sacaron **{dado_usuario1}**.\nLa apuesta se devuelve a ambos jugadores.",
                color=discord.Color.gold()
            )
            
            embed.add_field(name=f"Tirada de {usuario1.display_name}", value=f"🎲 {dado_usuario1}", inline=True)
            embed.add_field(name=f"Tirada de {usuario2.display_name}", value=f"🎲 {dado_usuario2}", inline=True)
            
            await ctx.send(embed=embed)
            return
            
        # Actualizar estadísticas
        stats_ganador = self.stats_manager.obtener_estadisticas(ganador.id)
        stats_perdedor = self.stats_manager.obtener_estadisticas(perdedor.id)
        
        if "dados" not in stats_ganador:
            stats_ganador["dados"] = {"victorias": 0, "derrotas": 0}
        if "dados" not in stats_perdedor:
            stats_perdedor["dados"] = {"victorias": 0, "derrotas": 0}
        
        stats_ganador["dados"]["victorias"] = stats_ganador["dados"].get("victorias", 0) + 1
        stats_perdedor["dados"]["derrotas"] = stats_perdedor["dados"].get("derrotas", 0) + 1
        
        self.stats_manager.guardar_estadisticas(ganador.id, stats_ganador)
        self.stats_manager.guardar_estadisticas(perdedor.id, stats_perdedor)
        
        # Actualizar saldos - El ganador recibe la apuesta de ambos jugadores
        saldo_ganador = casino_manager.obtener_saldo(str(ganador.id))
        saldo_perdedor = casino_manager.obtener_saldo(str(perdedor.id))
        
        # El perdedor pierde su apuesta
        nuevo_saldo_perdedor = saldo_perdedor - valor_apuesta
        casino_manager.actualizar_saldo(str(perdedor.id), nuevo_saldo_perdedor)
        
        # El ganador recibe el doble de la apuesta
        premio_total = valor_apuesta * 2
        nuevo_saldo_ganador = saldo_ganador + valor_apuesta
        casino_manager.actualizar_saldo(str(ganador.id), nuevo_saldo_ganador)
        
        # Crear y enviar el embed
        embed = discord.Embed(
            title="🎲 Resultado del Desafío de Dados",
            description=f"🏆 **{ganador.mention}** ha ganado el desafío contra {perdedor.mention}!\n\n"
                       f"**{ganador.display_name}** sacó **{dado_ganador}** vs **{dado_perdedor}** de **{perdedor.display_name}**",
            color=discord.Color.green()
        )
        
        embed.add_field(name="💰 Premio total", value=f"{premio_total} monedas", inline=True)
        embed.add_field(name="💵 Nuevo saldo del ganador", value=f"{nuevo_saldo_ganador} monedas", inline=True)
        embed.add_field(name="💸 Nuevo saldo del perdedor", value=f"{nuevo_saldo_perdedor} monedas", inline=True)
        
        await ctx.send(embed=embed)