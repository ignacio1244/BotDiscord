import aiohttp
import asyncio
import logging
from typing import Dict, Any, Optional, Union, List
from cache import Cache

class HttpClient:
    """Cliente HTTP asíncrono para realizar peticiones"""
    
    def __init__(self, cache: Optional[Cache] = None):
        """
        Inicializa el cliente HTTP
        
        Args:
            cache: Instancia de caché opcional para almacenar respuestas
        """
        self.session = None
        self.cache = cache or Cache()
        self.default_headers = {
            "User-Agent": "DiscordBot/1.0"
        }
    
    async def initialize(self):
        """Inicializa la sesión HTTP"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(headers=self.default_headers)
    
    async def close(self):
        """Cierra la sesión HTTP"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get(self, 
                 url: str, 
                 params: Optional[Dict[str, Any]] = None, 
                 headers: Optional[Dict[str, str]] = None,
                 use_cache: bool = True,
                 cache_ttl: Optional[int] = None) -> Dict[str, Any]:
        """
        Realiza una petición GET
        
        Args:
            url: URL para la petición
            params: Parámetros de consulta
            headers: Cabeceras HTTP adicionales
            use_cache: Si se debe usar la caché
            cache_ttl: Tiempo de vida en caché
            
        Returns:
            Respuesta JSON como diccionario
        """
        await self.initialize()
        
        # Crear clave de caché
        cache_key = f"get_{url}_{str(params)}"
        
        # Verificar caché si está habilitada
        if use_cache:
            cached_response = self.cache.get(cache_key)
            if cached_response:
                return cached_response
        
        # Combinar cabeceras
        merged_headers = self.default_headers.copy()
        if headers:
            merged_headers.update(headers)
        
        try:
            async with self.session.get(url, params=params, headers=merged_headers) as response:
                response.raise_for_status()
                data = await response.json()
                
                # Almacenar en caché si está habilitada
                if use_cache:
                    self.cache.set(cache_key, data, cache_ttl)
                
                return data
        except aiohttp.ClientResponseError as e:
            logging.error(f"Error HTTP {e.status} al obtener {url}: {e.message}")
            raise
        except aiohttp.ClientError as e:
            logging.error(f"Error de cliente al obtener {url}: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Error inesperado al obtener {url}: {str(e)}")
            raise
    
    async def post(self, 
                  url: str, 
                  data: Optional[Dict[str, Any]] = None,
                  json: Optional[Dict[str, Any]] = None,
                  headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Realiza una petición POST
        
        Args:
            url: URL para la petición
            data: Datos de formulario
            json: Datos JSON
            headers: Cabeceras HTTP adicionales
            
        Returns:
            Respuesta JSON como diccionario
        """
        await self.initialize()
        
        # Combinar cabeceras
        merged_headers = self.default_headers.copy()
        if headers:
            merged_headers.update(headers)
        
        try:
            async with self.session.post(url, data=data, json=json, headers=merged_headers) as response:
                response.raise_for_status()
                return await response.json()
        except aiohttp.ClientResponseError as e:
            logging.error(f"Error HTTP {e.status} al enviar POST a {url}: {e.message}")
            raise
        except aiohttp.ClientError as e:
            logging.error(f"Error de cliente al enviar POST a {url}: {str(e)}")
            raise
        except Exception as e:
            logging.error(f"Error inesperado al enviar POST a {url}: {str(e)}")
            raise