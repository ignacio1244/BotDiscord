# 🤖 GLaDOS - Discord Bot

**GLaDOS** es un bot de Discord inspirado en el personaje de *Portal*, con una personalidad sarcástica y respuestas automáticas personalizadas. Incluye comandos de juegos, utilidades y mensajes automáticos al ingresar o salir del servidor.

---

## 🚀 Características

- Bienvenida y despedida con frases sarcásticas personalizadas.
- Comandos como `!glados_info`, `!cake`, `!ruleta`, `!ppyt`, `!reto`, `!dolar`, `!horoscopo`, entre otros.
- Gestión de saldo de usuario.
- Estilo modular, fácil de mantener y ampliar.

---

## 🛠️ Instalación
```
1. Cloná el repositorio:

git clone https://github.com/tu-usuario/tu-repo.git
cd tu-repo

Creá y activá un entorno virtual:
python -m venv venv 
venv\Scripts\activate      # En Windows 
source venv/bin/activate   # En Linux/Mac

Instalá las dependencias:

pip install -r requirements.txt

Configurá tus variables de entorno

Creá un archivo .env con tu token:  
DISCORD_TOKEN=tu_token_aqui  
```
<br>

## 💡 Estructura del proyecto 

```
📁 tu-repo/ 
│ <br>
├── bot.py               # Archivo principal 
├── GLaDOS.py            # Mensajes automáticos y personalidad 
├── comandos/ <br>
│   ├── casino.py 
│   ├── juego.py 
│   ├── ppyt.py 
│   └── reto.py 
├── utils/ 
│   └── casino_saldos.py 
├── requirements.txt 
└── .env 

```
