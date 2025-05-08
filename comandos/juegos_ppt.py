import discord
import random
from discord.ext import commands
from discord.ui import View, Button
from comandos.estadisticas import EstadisticasManager

# Emojis unificados para ambos modos de juego
EMOJIS = {
    "piedra": "🗿",
    "papel": "📄",
    "tijeras": "✂️"
}

class JuegosPPT(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.stats_manager = EstadisticasManager()
    
    #--------------------- Comando para jugar contra el bot ---------------------
    @commands.command(name="ppt")
    async def ppt(self, ctx):
        """Juega a piedra, papel o tijeras contra el bot"""
        jugador = ctx.author
        jugador_puntos = 0
        bot_puntos = 0

        await ctx.send(f"🎮 {jugador.mention} ¡Vamos a jugar al mejor de 3 contra el bot!")

        while jugador_puntos < 2 and bot_puntos < 2:
            view = EleccionView(jugador)
            mensaje = await ctx.send("Elegí una opción:", view=view)
            await view.wait()

            if view.eleccion is None:
                await ctx.send("⏰ No elegiste a tiempo. ¡Se canceló la partida!")
                return

            opciones = ["piedra", "papel", "tijeras"]
            eleccion_bot = random.choice(opciones)
            resultado, ganador = self._determinar_ganador(view.eleccion, eleccion_bot)

            if ganador == 1:  # Jugador gana
                jugador_puntos += 1
                self.stats_manager.actualizar_estadisticas_ppt(jugador.id, 'victoria')
            elif ganador == 2:  # Bot gana
                bot_puntos += 1
                self.stats_manager.actualizar_estadisticas_ppt(jugador.id, 'derrota')
            else:  # Empate
                self.stats_manager.actualizar_estadisticas_ppt(jugador.id, 'empate')

            await ctx.send(f"{EMOJIS[view.eleccion]} vs {EMOJIS[eleccion_bot]} - {resultado}")
            await ctx.send(f"🏆 Marcador: {jugador.name} {jugador_puntos} - Bot {bot_puntos}")

        if jugador_puntos == 2:
            await ctx.send(f"🎉 Felicitaciones {jugador.mention}, ¡ganaste la partida!")
        else:
            await ctx.send(f"💀 El bot ganó la partida. ¡Suerte la próxima!")

    #--------------------- Comando para retar a otro usuario ---------------------
    @commands.command(name="reto", aliases=["duelo", "challenge"])
    async def desafiar_usuario(self, ctx, oponente: discord.Member = None):
        """Inicia un duelo de piedra, papel o tijeras contra otro usuario"""
        
        if not oponente:
            return await self._enviar_error(ctx, "Debes mencionar a un oponente. Ejemplo: `!reto @usuario`")
        
        if oponente.bot:
            return await self._enviar_error(ctx, "No puedes jugar contra un bot. ¡Busca un compañero humano! 🤖")
        
        if oponente == ctx.author:
            return await self._enviar_error(ctx, "¡No puedes jugar contigo mismo! 🤣")

        await self._iniciar_duelo(ctx, ctx.author, oponente)

    async def _enviar_error(self, ctx, mensaje):
        embed = discord.Embed(
            title="❌ Error",
            description=mensaje,
            color=discord.Color.red()
        )
        await ctx.send(embed=embed)

    async def _iniciar_duelo(self, ctx, jugador1, jugador2):
        embed = discord.Embed(
            title="⚔️ Duelo de Piedra, Papel o Tijeras",
            description=f"{jugador1.mention} ha retado a {jugador2.mention}!\n\n"
                       f"Juego al mejor de 3. Cada jugador tiene 30 segundos para elegir en cada ronda.",
            color=discord.Color.blue()
        )
        await ctx.send(embed=embed)

        victorias_j1 = 0
        victorias_j2 = 0
        ronda = 1
        
        while victorias_j1 < 2 and victorias_j2 < 2:
            await ctx.send(f"📢 **Ronda {ronda}** - {jugador1.display_name}: {victorias_j1} | {jugador2.display_name}: {victorias_j2}")
            
            # Obtener elecciones
            eleccion1 = await self._obtener_eleccion(ctx, jugador1)
            if not eleccion1:
                return await ctx.send(f"⏰ {jugador1.mention} no eligió a tiempo. Duelo cancelado.")

            eleccion2 = await self._obtener_eleccion(ctx, jugador2)
            if not eleccion2:
                return await ctx.send(f"⏰ {jugador2.mention} no eligió a tiempo. Duelo cancelado.")

            ganador_ronda = await self._mostrar_resultados_ronda(ctx, jugador1, jugador2, eleccion1, eleccion2, ronda)
            
            if ganador_ronda == 1:
                victorias_j1 += 1
            elif ganador_ronda == 2:
                victorias_j2 += 1
                
            ronda += 1
        
        await self._mostrar_resultado_final(ctx, jugador1, jugador2, victorias_j1, victorias_j2)

    async def _obtener_eleccion(self, ctx, jugador):
        """Muestra los botones y obtiene la elección del jugador"""
        view = EleccionView(jugador)
        mensaje = await ctx.send(
            f"{jugador.mention}, elige tu opción:",
            view=view
        )
        await view.wait()
        await mensaje.delete()  
        return view.eleccion

    async def _mostrar_resultados_ronda(self, ctx, jugador1, jugador2, eleccion1, eleccion2, ronda):
        """Muestra los resultados de una ronda y devuelve el número del jugador ganador (1 o 2) o 0 si es empate"""
        resultado, ganador = self._determinar_ganador(eleccion1, eleccion2)
        
        embed = discord.Embed(
            title=f"🏆 Resultado de la Ronda {ronda}",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name=f"{jugador1.display_name}",
            value=f"{EMOJIS[eleccion1]} {eleccion1.capitalize()}",
            inline=True
        )
        embed.add_field(
            name="VS",
            value="\u200b",
            inline=True
        )
        embed.add_field(
            name=f"{jugador2.display_name}",
            value=f"{EMOJIS[eleccion2]} {eleccion2.capitalize()}",
            inline=True
        )
        
        embed.add_field(
            name="Resultado",
            value=resultado,
            inline=False
        )
        
        await ctx.send(embed=embed)
        return ganador

    async def _mostrar_resultado_final(self, ctx, jugador1, jugador2, victorias_j1, victorias_j2):
        """Muestra el resultado final del duelo"""
        ganador = jugador1 if victorias_j1 > victorias_j2 else jugador2
        perdedor = jugador2 if victorias_j1 > victorias_j2 else jugador1
        
        if victorias_j1 > victorias_j2:
            self.stats_manager.actualizar_estadisticas_reto(jugador1.id, 'victoria')
            self.stats_manager.actualizar_estadisticas_reto(jugador2.id, 'derrota')
        else:
            self.stats_manager.actualizar_estadisticas_reto(jugador2.id, 'victoria')
            self.stats_manager.actualizar_estadisticas_reto(jugador1.id, 'derrota')
        
        embed = discord.Embed(
            title="🏆 ¡Fin del Duelo!",
            description=f"**{ganador.mention} ha ganado el duelo al mejor de 3!**",
            color=discord.Color.gold()
        )
        
        embed.add_field(
            name=f"{jugador1.display_name}",
            value=f"{victorias_j1} victorias",
            inline=True
        )
        embed.add_field(
            name=f"{jugador2.display_name}",
            value=f"{victorias_j2} victorias",
            inline=True
        )
        
        embed.set_thumbnail(url="https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExZXhqcTdmMHF6ODl2c24zc2N4MnV1cml3bTV6dHZmc21mN3ZldDNqMCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/XreQmk7ETCak0/giphy.gif")
        
        await ctx.send(embed=embed)

    def _determinar_ganador(self, eleccion1, eleccion2):
        """Determina el ganador del duelo y devuelve (mensaje, número_ganador)"""
        if eleccion1 == eleccion2:
            return "🤝 ¡Empate! 😐", 0
        
        reglas = {
            "piedra": "tijeras",
            "papel": "piedra",
            "tijeras": "papel"
        }
        
        if reglas[eleccion1] == eleccion2:
            return "🎉 ¡Jugador 1 gana!", 1
        return "🎉 ¡Jugador 2 gana!", 2

class EleccionView(View):
    def __init__(self, jugador):
        super().__init__(timeout=30)
        self.jugador = jugador
        self.eleccion = None

    @discord.ui.button(label=f"{EMOJIS['piedra']} Piedra", style=discord.ButtonStyle.danger)
    async def piedra(self, interaction: discord.Interaction, button: Button):
        await self._procesar_eleccion(interaction, "piedra")

    @discord.ui.button(label=f"{EMOJIS['papel']} Papel", style=discord.ButtonStyle.primary)
    async def papel(self, interaction: discord.Interaction, button: Button):
        await self._procesar_eleccion(interaction, "papel")

    @discord.ui.button(label=f"{EMOJIS['tijeras']} Tijeras", style=discord.ButtonStyle.success)
    async def tijeras(self, interaction: discord.Interaction, button: Button):
        await self._procesar_eleccion(interaction, "tijeras")

    async def _procesar_eleccion(self, interaction, eleccion):
        """Valida y procesa la elección del jugador"""
        if interaction.user != self.jugador:
            await interaction.response.send_message(
                "Este juego no es para ti. Espera tu turno.",
                ephemeral=True
            )
            return
        
        self.eleccion = eleccion
        await interaction.response.defer()
        self.stop()

    async def on_timeout(self):
        self.stop()

async def setup(bot):
    await bot.add_cog(JuegosPPT(bot))