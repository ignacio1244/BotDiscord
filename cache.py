import time
import asyncio
import logging
from typing import Any, Dict, Optional, Callable, Tuple

class Cache:
    """Sistema de caché para almacenar datos temporalmente"""
    
    def __init__(self, default_ttl: int = 3600):
        """
        Inicializa el sistema de caché
        
        Args:
            default_ttl: Tiempo de vida predeterminado en segundos (1 hora por defecto)
        """
        self.cache: Dict[str, Tuple[Any, float]] = {}
        self.default_ttl = default_ttl
        self.hit_count = 0
        self.miss_count = 0
        
        # Iniciar tarea de limpieza automática
        asyncio.create_task(self._cleanup_task())
    
    def get(self, key: str) -> Optional[Any]:
        """
        Obtiene un valor de la caché
        
        Args:
            key: Clave para buscar en la caché
            
        Returns:
            El valor almacenado o None si no existe o expiró
        """
        if key in self.cache:
            value, expiry = self.cache[key]
            if expiry > time.time():
                self.hit_count += 1
                return value
            else:
                # Eliminar entrada expirada
                del self.cache[key]
        
        self.miss_count += 1
        return None
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Almacena un valor en la caché
        
        Args:
            key: Clave para almacenar el valor
            value: Valor a almacenar
            ttl: Tiempo de vida en segundos (usa el predeterminado si es None)
        """
        if ttl is None:
            ttl = self.default_ttl
        
        expiry = time.time() + ttl
        self.cache[key] = (value, expiry)
    
    def delete(self, key: str) -> bool:
        """
        Elimina una entrada de la caché
        
        Args:
            key: Clave a eliminar
            
        Returns:
            True si se eliminó, False si no existía
        """
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Limpia toda la caché"""
        self.cache.clear()
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas de la caché
        
        Returns:
            Diccionario con estadísticas
        """
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests * 100) if total_requests > 0 else 0
        
        return {
            "size": len(self.cache),
            "hits": self.hit_count,
            "misses": self.miss_count,
            "hit_rate": hit_rate,
            "total_requests": total_requests
        }
    
    async def _cleanup_task(self) -> None:
        """Tarea para limpiar entradas expiradas periódicamente"""
        while True:
            try:
                current_time = time.time()
                keys_to_delete = [
                    key for key, (_, expiry) in self.cache.items()
                    if expiry <= current_time
                ]
                
                for key in keys_to_delete:
                    del self.cache[key]
                
                if keys_to_delete:
                    logging.debug(f"Caché: Se eliminaron {len(keys_to_delete)} entradas expiradas")
                
                # Registrar estadísticas cada hora
                if len(self.cache) > 0 or self.hit_count + self.miss_count > 0:
                    stats = self.get_stats()
                    logging.info(
                        f"Estadísticas de caché: {stats['size']} entradas | "
                        f"Tasa de aciertos: {stats['hit_rate']:.2f}% | "
                        f"Solicitudes: {stats['total_requests']}"
                    )
            except Exception as e:
                logging.error(f"Error en la tarea de limpieza de caché: {e}")
            
            # Ejecutar cada 30 minutos
            await asyncio.sleep(1800)
    
    async def cached(self, key_prefix: str, ttl: Optional[int] = None):
        """
        Decorador para cachear resultados de funciones asíncronas
        
        Args:
            key_prefix: Prefijo para la clave de caché
            ttl: Tiempo de vida en segundos
            
        Returns:
            Decorador para funciones asíncronas
        """
        def decorator(func):
            async def wrapper(*args, **kwargs):
                # Crear clave única basada en argumentos
                arg_str = "_".join(str(arg) for arg in args)
                kwarg_str = "_".join(f"{k}={v}" for k, v in sorted(kwargs.items()))
                cache_key = f"{key_prefix}_{func.__name__}_{arg_str}_{kwarg_str}"
                
                # Intentar obtener de la caché
                cached_result = self.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # Ejecutar función y almacenar resultado
                result = await func(*args, **kwargs)
                self.set(cache_key, result, ttl)
                return result
            return wrapper
        return decorator