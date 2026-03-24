from dataclasses import dataclass
from enum import Enum


class RolUsuario(str, Enum):
    ADMIN = 'ADMIN'
    FAMILIA = 'FAMILIA'


@dataclass
class UsuarioEntity:
    id: int
    email: str
    rol: RolUsuario
    nombre: str = ''
    is_active: bool = True
