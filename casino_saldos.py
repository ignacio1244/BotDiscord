import json
import os

# Archivo donde se guardan los saldos
ARCHIVO_SALDOS = "saldos_casino.json"

# Inicializar saldos si no existe
if not os.path.exists(ARCHIVO_SALDOS) or os.stat(ARCHIVO_SALDOS).st_size == 0:
    with open(ARCHIVO_SALDOS, "w") as f:
        json.dump({}, f)

# Cargar saldos
with open(ARCHIVO_SALDOS, "r") as f:
    try:
        saldos = json.load(f)
    except json.JSONDecodeError:
        saldos = {}

def guardar_saldos():
    with open(ARCHIVO_SALDOS, "w") as f:
        json.dump(saldos, f)

def obtener_saldo(usuario_id):
    return saldos.get(str(usuario_id), 100)

def actualizar_saldo(usuario_id, nuevo_saldo):
    saldos[str(usuario_id)] = nuevo_saldo
    guardar_saldos()

# Colores estándar de ruleta europea
rojo = {1,3,5,7,9,12,14,16,18,19,21,23,25,27,30,32,34,36}
negro = {2,4,6,8,10,11,13,15,17,20,22,24,26,28,29,31,33,35}
verde = {0}
