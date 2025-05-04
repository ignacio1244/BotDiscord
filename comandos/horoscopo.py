# horoscopo.py
import random

def obtener_horoscopo(signo: str = None):
    if signo is None:
        return "¿Qué haces usando este comando? El horóscopo no sirve para nada. ¡No pierdas tu tiempo!"

    # Mensajes sarcásticos y divertidos
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
    ]
    
    # Elegir una respuesta al azar

    return random.choice(respuestas)

