import random
from discord.ext import commands

class Horoscopo(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="horoscopo")
    async def horoscopo(self, ctx, signo: str = None):
        if signo is None:
            await ctx.send("¿Qué haces usando este comando? El horóscopo no sirve para nada. ¡No pierdas tu tiempo!")
            return

        respuestas = [
            f"¡Vaya! Estás usando el horóscopo... Claro, porque la astrología tiene respuestas para todo. Aquí va: {signo} está destinado a tener un día increíble... si te tomas una siesta.",
            f"¿Estás en serio? ¡El horóscopo no sabe nada! Pero bueno, aquí tienes: {signo}, prepárate para un día lleno de... ¿nada especial?",
            f"¿De verdad confías en los horóscopos? Vamos, {signo}, ni el sol sabe qué te depara. ¡Que tengas un día promedio!",
            f"¡Ajá! Claro, porque el horóscopo predice el futuro... {signo}, tendrás un día normal, como todos los demás, ¡y ya está!",
            f"{signo}, si piensas que este horóscopo cambiará tu vida, te vas a decepcionar. ¡Vas a tener un día como cualquier otro!",
            f"¡Claro, {signo}, el horóscopo sabe todo! Prepárate para un día donde absolutamente nada extraordinario sucederá.",
            f"Bueno, {signo}, según los astros, hoy será un día tan genial como mirar el reloj esperando que pase la hora. ¡Qué emoción!",
            f"Los astros dicen que hoy te enfrentarás a grandes desafíos. Como elegir entre pizza o hamburguesa para la cena. ¡Gran elección, {signo}!",
            f"¡Hoy es tu día, {signo}! De hecho, lo es para todos, porque el horóscopo no tiene ni idea de qué está pasando. ¡A seguir con la rutina!",
            f"Los planetas están alineados para que tengas un día... como cualquier otro. ¡Te lo dijo el horóscopo, {signo}!",
            f"El universo te está mirando, {signo}, y está pensando... '¿Realmente confías en un horóscopo?' Bueno, ¡es lo que hay!"
            f"¡Atención {signo}! Las estrellas dicen que hoy es un buen día para... ¡espera! Las estrellas no hablan. Qué raro, ¿no?",
            f"Según mi bola de cristal, {signo}, hoy tendrás la misma suerte que un paraguas en el desierto. ¡Totalmente inútil!",
            f"¡Felicidades {signo}! Hoy es tu día de suerte... o no. En realidad, es solo otro día más en el calendario.",
            f"Los astros me dicen que {signo} debería dejar de creer en los astros. ¿Irónico, verdad?",
            f"¡{signo}! Hoy es el día perfecto para hacer algo productivo, como dejar de leer horóscopos.",
            f"Mercurio retrógrado afectará a {signo} hoy... igual que afecta a todos: ¡absolutamente nada!",
            f"Las cartas astrales revelan que {signo} gastará su tiempo leyendo tonterías como esta. ¡Qué precisión!",
            f"¡Alerta cósmica para {signo}! Hoy podrías encontrarte con alguien... o no. Las probabilidades son 50/50.",
            f"El cosmos ha hablado, {signo}: deberías invertir en un buen libro de ciencia en lugar de creer en estas cosas.",
            f"¡{signo}! Tu planeta regente dice que deberías tomar decisiones basadas en la lógica, no en un bot de Discord.",
            f"Hoy {signo} tendrá un día tan especial como todos los otros 7 mil millones de habitantes del planeta. ¡Qué coincidencia!",
            f"Las constelaciones sugieren que {signo} debería considerar que las constelaciones son solo estrellas muy lejanas sin ninguna influencia en su vida.",
            f"¡Buenas noticias, {signo}! Tu futuro está determinado por tus decisiones, no por un montón de planetas girando por ahí.",
            f"Según la posición de Júpiter, {signo} debería recordar que Júpiter está a unos 588 millones de kilómetros y le importa un comino tu vida.",
            f"¡{signo}! Tu número de la suerte es... ¡espera! Los números no tienen poderes mágicos. Qué decepción, ¿verdad?",
            f"La Luna está en la séptima casa, lo que significa que {signo} debería considerar mudarse a una octava casa. O no. Da igual.",
            f"¡Predicción exclusiva para {signo}! Hoy respirarás aproximadamente 20,000 veces. Impresionante, ¿no?",

        ]
        await ctx.send(random.choice(respuestas))

async def setup(bot):
    await bot.add_cog(Horoscopo(bot))

