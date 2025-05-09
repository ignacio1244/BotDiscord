# 🤖 GLaDOS - Discord Bot

**GLaDOS** es un bot de Discord inspirado en el personaje de *Portal*, con una personalidad sarcástica y respuestas automáticas personalizadas. Incluye comandos de juegos, utilidades, sistema de economía, estadísticas y mensajes automáticos al ingresar o salir del servidor.

---

## 🚀 Características

- **Personalidad**: Bienvenida y despedida con frases sarcásticas personalizadas.
- **Juegos**: 
  - `!ppt` - Piedra, papel o tijeras contra el bot
  - `!reto` - Duelos de piedra, papel o tijeras al mejor de 3 contra otros usuarios
  - `!ruleta` - Juego de casino con apuestas
  - `!wordle` - Juego de Wordle
- **Economía**:
  - `!dolar` - Cotización del dólar en argentina 
  - `!crypto` - precio de la criptomonedas 
- **Utilidades**:
  - `!clima` - Consulta el clima de una ciudad
  - `!horoscopo` - Obtén tu horóscopo diario
  - `!encuesta` - Crea encuestas interactivas
  - `!stats` - Consulta tus estadísticas de juegos
  - `!recomendar` - Obtén recomendaciones de películas y series
  - `!ayuda` - Lista de comandos disponibles
- **Moderación**:
  - Comandos para gestionar el servidor
- **GLaDOS**:
  - `!glados_info` - Información sobre el bot
  - `!cake` - ¿Será verdad o mentira?

---

## 📊 Estadísticas

El bot ahora cuenta con un sistema de estadísticas que registra:
- Victorias y derrotas en juegos de Piedra, Papel o Tijeras
- Victorias y derrotas en duelos contra otros usuarios
- Ganancias y pérdidas en la ruleta

Usa `!stats` para ver tus estadísticas generales o `!stats [juego]` para ver estadísticas específicas.

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
📁 repo/
│
├── bot.py                # Archivo principal
├── GLaDOS.py             # Mensajes automáticos y personalidad
├── comandos/             # Módulos de comandos
│   ├── ayuda.py          # Comando de ayuda
│   ├── billetera.py      # Cotización del dólar en ARG y precio de la criptomonedas
│   ├── casino.py         # Juego de ruleta
│   ├── clima.py          # Consulta del clima
│   ├── economia.py       # Sistema económico
│   ├── encuesta.py       # Creación de encuestas
│   ├── estadisticas.py   # Estadísticas de juegos
│   ├── horoscopo.py      # Consulta de horóscopo
│   ├── moderacion.py     # Comandos de moderación
│   ├── juegos_ppt.py     # Piedra, papel o tijeras
│   ├── recomendador.py   # Recomendaciones de películas y series
│   └──wordle.py          # Juego de Wordle
├── utils/                # Utilidades y datos
│   ├── estadisticas.json # Datos de estadísticas
│   └── saldos.json       # Datos de economía
├── requirements.txt      # Dependencias
└── Token.env             # Variables de entorno

```
