from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Optional


class EstadoSolicitud(str, Enum):
    PENDIENTE = 'PENDIENTE'
    APROBADA = 'APROBADA'
    RECHAZADA = 'RECHAZADA'


@dataclass
class SolicitudAdopcionEntity:
    mascota_id: int
    familia_id: int
    id: Optional[int] = None
    estado: EstadoSolicitud = EstadoSolicitud.PENDIENTE
    mensaje: str = ''
    notas_admin: str = ''
    fecha_solicitud: Optional[datetime] = None
    fecha_decision: Optional[datetime] = None


@dataclass
class AdopcionEntity:
    solicitud_id: int
    id: Optional[int] = None
    fecha_adopcion: Optional[datetime] = None
    notas: str = ''
