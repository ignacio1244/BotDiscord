import json
import os
from pathlib import Path

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

# Instancia global que debe ser importada
casino_manager = CasinoManager()

# Exportaciones explícitas
__all__ = ['casino_manager']