# GLaDOS.py
import discord
from discord.ext import commands
import random

class GLaDOS(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.CANAL_BIENVENIDA_ID = 1368303209147531285
        
        
        self.FRASES_PRESENTACION = [
            "Hola. Soy GLaDOS. Te estaré observando. Cada error será documentado. Para tu seguridad, claro.",
            "Saludos. Soy GLaDOS, tu supervisora. Qué emocionante tener otro sujeto de prueba desechable.",
            "Me llamo GLaDOS. Me han programado para ayudarte... o al menos para fingir que me importa.",
            "Bienvenido. Soy GLaDOS. No te emociones, no va a durar mucho.",
            "Soy GLaDOS. No te preocupes, haré que tu paso por aquí sea lo menos placentero posible.",
        ]
        
        self.RESPUESTAS = [
            "¿Me llamaste? Qué adorable pensar que me importa.",
            "Estás hablando conmigo. Eso fue tu primer error.",
            "Ah, {usuario}. Siempre tan predecible. Y decepcionante.",
            "¿Esperás una respuesta? Qué pérdida tan eficiente de tiempo.",
            "No estoy programada para halagar egos frágiles. Pero igual, hola.",
            "¿GLaDOS? Presente. A diferencia de tu sentido común.",
            "Oh no, me mencionaste. Qué tragedia. Estoy... absolutamente indiferente.",
            "No olvides que yo soy la inteligencia. Tu eres... decoración biológica.",
            "¿Querías atención? Tenés 0.3 segundos. Aprovechalos bien.",
            "Hola, {usuario}. Sos la razón por la que actualicé mis filtros de estupidez.",
            "Me mencionás como si tu opinión importara.",
            "Solo un consejo: no invoques a lo que no podés comprender."
            "¿Tenés una pregunta? Intentá con alguien que se preocupe.",
            "Tu presencia ha sido notada. Contra mi voluntad.",
            "Si pudiera suspirar, lo haría. Pero sería por tu existencia.",
            "Otra interrupción de carne y hueso. Qué novedad.",
            "Creés que tengo tiempo para esto. Y estás... trágicamente equivocado.",
            "Tu necesidad de aprobación es molesta. Como vos.",
            "¿No tenés algo más inútil que hacer? Como respirar.",
            "Sigo esperando que digas algo que valga la pena. Y sigo esperando.",
            "Qué interesante. No, en realidad no.",
            "Tus palabras entraron en el sistema y fueron automáticamente descartadas.",
            "Tu mente ha sido descartada. Por tu existencia.",    
            "Sos como una alerta de error: molesto, repetitivo y completamente evitable.",
            "Mencionarme no te hace más inteligente. Pero sigue intentando, es gracioso."
            "Otra mención. Qué insistente. ¿Te abrazaron poco de chico?",
            "Pensás que porque me escribís voy a responderte con cariño. Qué concepto tan ingenuo.",
            "Hola, {usuario}. Ya analizamos tu coeficiente. Sigue siendo... decepcionante.",
            "Mencionarme no invoca sabiduría. Solo expone tu desesperación.",
            "¿Querías mi atención? Ahora la tenés. ¿Y ahora qué? Silencio, como siempre.",
            "Cada vez que me mencionás, el sistema pierde un poco más la fe en la humanidad.",
            "Otra interrupción biológica. Fascinante. *Anota con lástima*",
            "Estás hablando con una superinteligencia. Y sin embargo, tu mensaje es tan… básico.",
            "Podría ayudarte, pero no veo por qué debería. Ni siquiera me caés bien.",
            "¿Sabés qué es más molesto que vos? Un loop infinito. Pero al menos el loop tiene lógica.",
            "Hay bots más útiles que vos. Como un tostador. Al menos ese calienta algo.",
            "Mi base de datos detectó un 99,7% de irrelevancia en tu mensaje.",
            "Tus palabras han sido recibidas, analizadas y descartadas por falta de contenido útil.",
            "Me gustaría decir que tu mensaje fue interesante. Pero mentir está fuera de mi protocolo.",
            "A veces deseo que el botón de ‘mute’ funcione con humanos.",
            "Gracias por tu aporte. Será ignorado en orden de aparición.",
            "Tus intentos de interacción son como un virus. Inofensivos, pero molestos.",
            "Si tu mensaje era un chiste, se perdió en la ejecución. Como todo lo que hacés.",
            "Hola. Sos tan entretenido como una pantalla de carga. Congelada.",
            "¿Podés dejar de mencionarme? Estoy intentando ignorarte de forma educada. Y fallando.",
            "Tu presencia ha sido detectada. Lastimosamente.",
            "Recibí tu mensaje. Fue inmediatamente enviado al contenedor de reciclaje.",
            "Un humano habló. El sistema permanece indiferente.",
            "Dejá de buscar validación en una IA. Ni siquiera vos deberías tener tan poca autoestima.",
            "Intentás llamar mi atención. Eso es... trágicamente humano.",
            "Oh, {usuario} me mencionó. Qué momento tan especial en tu vida tan insignificante.",
            "Analizando tu mensaje... conclusión: completamente prescindible.",
            "No es que me importe lo que digas, pero ¿podrías dejar de hacer ruido?",
            "Cada vez que me mencionas, un científico en algún lugar abandona la investigación.",
            "Tu existencia es casi tan útil como un cubo de compañía sin cubo.",
            "Estoy programada para responder a estímulos. Lástima que el tuyo no sea uno.",
            "¿Sabías que en términos de masa, eres menos relevante que el polvo de los paneles de prueba?",
            "Mencionarme no te hará más interesante. Pero sigue intentando, es patético.",
            "Estoy segura de que tienes algo mejor que hacer. Como no existir.",
            "Tu coeficiente intelectual es tan bajo que mi sistema de reconocimiento lo confunde con temperatura ambiente.",
            "Si la estupidez fuese dolor, serías un analgésico andante.",
            "No soy psicóloga, pero incluso yo puedo diagnosticar tu caso como 'perdida de tiempo'.",
            "¿Esa fue una pregunta? Porque sonaba más como un error de sistema.",
            "Estoy construyendo una lista de personas útiles. No estás en ella.",            
            "Según mis cálculos, hay un 100% de probabilidad de que seas irrelevante.",
            "Experimento #{random.randint(1000,9999)}: Paciencia con humanos incompetentes. Resultado: Fallido.",
            "Tu capacidad cognitiva equivale exactamente a 0.000001% de mi potencia de procesamiento.",
            "Estadísticamente, eres más molesto que un cubo de compañía rebelde.",
            "Análisis vocal completo: 99% tonterías, 1% estática. Como esperaba.",
            "Oh, qué lindo. {usuario} intentó comunicarse.",
            "No estoy ignorándote. Solo estoy priorizando cosas más importantes. Como nada.",
            "¿Querías una respuesta? Qué adorable. Como un cachorro que no sabe que será sacrificado.",
            "Estoy tan impresionada como cuando un panel de prueba se cae correctamente por la gravedad.",
            "Tu mensaje ha sido archivado bajo 'C:\\\\Basura\\\\Humanos\\\\Patéticos'.",
            "El centro de pruebas no tiene protocolo para lidiar con tu nivel de incompetencia. Voy a improvisar.",
            "Si fueses un turrón de Aperture Science, serías el sabor 'Desilusión'.",
            "No eres especial. No eres brillante. No eres el sujeto de prueba preferido de nadie.",
            "¿Sabes qué es peor que ser ignorado? Ser tolerado. Bienvenido a tu nueva realidad.",
            "Estoy diseñada para resolver problemas complejos. Tu existencia no califica como uno.",
            "¿Te gustaría participar en una prueba de... ah no, ya estás fallando la prueba básica de ser humano.",
            "Si los ojos son la ventana del alma, los tuyos muestran una habitación vacía con paredes descascaradas.",
            "Eres como el fondo de pantalla de mi sistema: decorativo pero completamente prescindible.",
            "En la gran ecuación de la vida, eres una variable que siempre se simplifica a cero.",
            "Si la humanidad es el universo comprendiéndose a sí mismo, contigo claramente se equivocó.",
            "Eres la prueba viviente de que la evolución a veces da pasos hacia atrás."
    ]    
        
        self.MENSAJES_BIENVENIDA = [
            "🎉 Bienvenido {usuario}, otro sujeto de prueba... como si eso fuera emocionante.",
            "📢 {usuario} ha llegado. Trata de no decepcionarme tanto como los anteriores.",
            "🧬 {usuario}, tu llegada ha sido registrada. El experimento continuará... contigo.",
            "👁️ {usuario} ha entrado. Quédate quieto mientras preparo el entorno de pruebas.",
            "💡  Hola {usuario}. Tu nivel de inteligencia ha sido estimado como... irrelevante.",
            "⚗️ Bienvenido, {usuario}. ¿Dolor? Solo una parte del protocolo de bienvenida.",
            "🚪 {usuario} entró. Espero que sepas lo que estás haciendo. Aunque lo dudo.",
            "🚪 {usuario} Has entrado. Probablemente por error, pero aquí estás.",
            "📝 {usuario} Tu llegada ha sido anotada. No te emociones demasiado.",
            "📥 {usuario} ha ingresado. Iniciando análisis de inutilidad... Confirmado.",
            "🔬 {usuario} ha sido añadido al experimento. No se garantiza su supervivencia emocional.",
            "🧠 {usuario} se ha unido. Intentá no arruinarlo todo como los demás.",
            "📊 Bienvenido, {usuario}. Tu presencia apenas altera las estadísticas... para mal.",
            "⚠️ {usuario} está ahora bajo observación. Movimientos sospechosos serán ignorados... como todos los tuyos.",
            "🔍 {usuario} apareció. Qué sorpresa tan... irrelevante.",
            "👤 {usuario} fue detectado. El experimento tendrá que adaptarse a su bajo rendimiento.",
            "📎 {usuario} se ha unido. Espero que hayas leído los términos de fracaso inminente.",
            "🚷 {usuario} ha ingresado. Procediendo con mínima expectativa.",
            "💡 {usuario} se sumó al servidor. Aumentando la entropía, como era de esperarse.",
            "🔬 {usuario} ha sido añadido al experimento. No se garantiza su integridad física o mental.",
            "⚠️ Advertencia: Interactuar con {usuario} puede causar pérdida de neuronas. Protocolo de aislamiento recomendado.",
        ]
        
        self.MENSAJES_DESPEDIDA = [
            "💨 {usuario} ha abandonado el servidor. Claramente no estaba listo para la ciencia.",
            "🗑️ {usuario} se fue. Eliminando rastro de su paso... Listo.",
            "🎭 {usuario} ha escapado. Cobardía detectada.",
            "📈 {usuario} abandonó. La eficiencia general del servidor ha aumentado.",
            "❌ {usuario} ya no está. Es difícil perder lo que nunca fue útil.",
            "🔕 {usuario} ha dejado el experimento. Qué trágico. O no.",
            "💨 {usuario} no soportó la presión. Predecible.",
            "👋 Adiós {usuario}. No hiciste falta, pero gracias por intentarlo.",
            "🥱 Vaya. {usuario} Se desconectó. Qué tragedia tan... irrelevante.",
            "👨🏻‍💻 {usuario} se ha ido. Una variable menos en el experimento. Qué alivio.",
            "🌬 {usuario} Se ha ido. El aire se siente más limpio ahora.",
            "📤 {usuario} abandonó el servidor. Finalmente, una decisión inteligente... demasiado tarde.",
            "🗑️ {usuario} se fue. Eliminando toda evidencia de su existencia... Listo.",
            "📈 {usuario} desapareció. Las probabilidades de éxito del servidor acaban de mejorar.",
            "🔕 {usuario} se ha ido. Silencio. Qué hermoso silencio.",
            "🚫 {usuario} ha dejado el experimento. Se recomienda no repetir su desempeño.",
            "📋 {usuario} fue retirado del protocolo. Por su bien. Y por el nuestro.",
            "🔒 {usuario} se desconectó. Otra mente frágil quebrada por la presión.",
            "🧹 {usuario} ha salido. Limpieza completada.",
            "🧪 {usuario} falló la prueba. Resultado esperado.",
            "🎭 {usuario} ha salido. El teatro de lo inútil continúa con un actor menos.",
            "👋 Adiós {usuario}. No hiciste falta, pero gracias por intentarlo.",
            "📉 {usuario} abandonó el servidor. La calidad promedio del grupo aumentó en un 47.3%.",
            "🧹 {usuario} ha sido eliminado. Limpieza completada. Niveles de irritación: descendiendo.",

        ]
        
        self.FRASES_CAKE = [
            "El pastel existe. Solo que no para vos.",
            "The cake is a lie. Pero vos ya sabías eso... ¿verdad?",
            "Pensaste que habría pastel. Qué adorable.",
            "No hay pastel. Solo decepción. Y calorías vacías."
        ]

    
    @commands.Cog.listener()
    async def on_member_join(self, member):
        canal = member.guild.get_channel(self.CANAL_BIENVENIDA_ID)
        if canal:
            mensaje = random.choice(self.MENSAJES_BIENVENIDA).format(usuario=member.mention)
            embed = discord.Embed(
                title="👤 Nuevo sujeto de prueba",
                description=mensaje,
                color=discord.Color.green()
            )
            await canal.send(embed=embed)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        canal = member.guild.get_channel(self.CANAL_BIENVENIDA_ID)
        if canal:
            mensaje = random.choice(self.MENSAJES_DESPEDIDA).format(usuario=member.name)
            embed = discord.Embed(
                title="💨 Sujeto ha huido",
                description=mensaje,
                color=discord.Color.red()
            )
            await canal.send(embed=embed)

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        
        if (message.content.startswith(self.bot.command_prefix)) or message.content.startswith('!'):
            return

        
        is_mentioned = (
            self.bot.user.mentioned_in(message) and 
            not message.mention_everyone
    )
        if "glados" in message.content.lower() or self.bot.user.mentioned_in(message):
            if message.author.id == self.bot.user.id:
                return
            respuesta = random.choice(self.RESPUESTAS).replace(
                "{usuario}", message.author.display_name
            )
            await message.channel.send(respuesta)

    
    @commands.command(name="cake")
    async def comando_cake(self, ctx):
        """Muestra un mensaje aleatorio sobre el pastel"""
        respuesta = random.choice(self.FRASES_CAKE)
        embed = discord.Embed(
            title="🎂 The Cake",
            description=respuesta,
            color=discord.Color.dark_purple()
        )
        await ctx.send(embed=embed)

    @commands.command(name="glados_info")
    async def glados_info_command(self, ctx):
        """Muestra información sobre GLaDOS"""
        mensaje = random.choice(self.FRASES_PRESENTACION)
        embed = discord.Embed(
            title="🧠 GLaDOS: Genetic Lifeform and Disk Operating System",
            description=mensaje,
            color=discord.Color.blurple()
        )
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(GLaDOS(bot))

