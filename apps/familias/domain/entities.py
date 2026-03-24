from dataclasses import dataclass, field
from typing import Optional, List
from enum import Enum


class TipoVivienda(str, Enum):
    CASA = 'CASA'
    APARTAMENTO = 'APARTAMENTO'
    FINCA = 'FINCA'
    OTRO = 'OTRO'


@dataclass
class FamiliaEntity:
    usuario_id: int
    nombre_familia: str
    telefono: str
    ciudad: str
    departamento: str
    id: Optional[int] = None


@dataclass
class CondicionesHogarEntity:
    familia_id: int
    tipo_vivienda: TipoVivienda
    tiene_patio: bool
    numero_personas: int
    tiene_mascotas_actualmente: bool
    experiencia_mascotas: str
    acuerdo_responsabilidad: bool
    id: Optional[int] = None
