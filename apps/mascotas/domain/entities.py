from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class EstadoMascota(str, Enum):
    DISPONIBLE = 'DISPONIBLE'
    EN_PROCESO = 'EN_PROCESO'
    ADOPTADO = 'ADOPTADO'
    NO_DISPONIBLE = 'NO_DISPONIBLE'


class EspecieMascota(str, Enum):
    PERRO = 'PERRO'
    GATO = 'GATO'
    OTRO = 'OTRO'


@dataclass
class MascotaEntity:
    nombre: str
    especie: EspecieMascota
    raza: str
    edad_anios: int
    descripcion: str
    id: Optional[int] = None
    estado: EstadoMascota = EstadoMascota.DISPONIBLE
    foto_url: Optional[str] = None
    fecha_ingreso: Optional[datetime] = None
    registrado_por_id: Optional[int] = None
