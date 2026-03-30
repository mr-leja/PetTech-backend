
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Protocol, runtime_checkable


@dataclass(frozen=True)
class VacunaRecomendada:
    nombre: str
    descripcion: str
    fecha_sugerida: date
    es_refuerzo: bool = False


@dataclass(frozen=True)
class CalendarioGenerado:
    vacunas: list[VacunaRecomendada]
    notas: str = ''


@runtime_checkable
class EspecieProtocolo(Protocol):
    """SRP + ISP: cada especie implementa únicamente su propio protocolo."""

    def generar(
        self,
        fecha_adopcion: date,
        edad_anios: int,
        edad_unidad: str,
        historial_nombres: set[str],
    ) -> list[VacunaRecomendada]: ...


_ES_CACHORRO_LIMITE_MESES = 12   # ≤ 12 meses → cachorro


def _es_cachorro(edad_anios: int, edad_unidad: str) -> bool:
    meses_totales = edad_anios if edad_unidad == 'MESES' else edad_anios * 12
    return meses_totales <= _ES_CACHORRO_LIMITE_MESES


def _ya_vacunado(vacuna: str, historial: set[str]) -> bool:
    """Compara de forma insensible a mayúsculas/tildes."""
    vacuna_norm = vacuna.lower().strip()
    return any(vacuna_norm in h.lower() for h in historial)


def _fecha(base: date, dias: int) -> date:
    return base + timedelta(days=dias)


class ProtocoloPerro:
    """Protocolo canino: Parvovirus, Moquillo, Hepatitis, Rabia, Bivalente."""

    def generar(
        self,
        fecha_adopcion: date,
        edad_anios: int,
        edad_unidad: str,
        historial_nombres: set[str],
    ) -> list[VacunaRecomendada]:
        cachorro = _es_cachorro(edad_anios, edad_unidad)
        vacunas: list[VacunaRecomendada] = []

        # Parvovirus
        if not _ya_vacunado('parvovirus', historial_nombres):
            vacunas.append(VacunaRecomendada(
                nombre='Parvovirus',
                descripcion='Protege contra el parvovirus canino, letal en cachorros.',
                fecha_sugerida=_fecha(fecha_adopcion, 7),
            ))
            if cachorro:
                vacunas.append(VacunaRecomendada(
                    nombre='Parvovirus (refuerzo)',
                    descripcion='Refuerzo a las 3-4 semanas de la primera dosis.',
                    fecha_sugerida=_fecha(fecha_adopcion, 28),
                    es_refuerzo=True,
                ))

        # Moquillo (Distemper)
        if not _ya_vacunado('moquillo', historial_nombres) and not _ya_vacunado('distemper', historial_nombres):
            vacunas.append(VacunaRecomendada(
                nombre='Moquillo (Distemper)',
                descripcion='Vacuna contra el distemper canino.',
                fecha_sugerida=_fecha(fecha_adopcion, 7),
            ))
            if cachorro:
                vacunas.append(VacunaRecomendada(
                    nombre='Moquillo (refuerzo)',
                    descripcion='Refuerzo a las 3-4 semanas.',
                    fecha_sugerida=_fecha(fecha_adopcion, 28),
                    es_refuerzo=True,
                ))

        # Hepatitis infecciosa canina
        if not _ya_vacunado('hepatitis', historial_nombres):
            vacunas.append(VacunaRecomendada(
                nombre='Hepatitis Infecciosa Canina',
                descripcion='Protege contra el adenovirus canino tipo 1.',
                fecha_sugerida=_fecha(fecha_adopcion, 14),
            ))

        # Rabia
        if not _ya_vacunado('rabia', historial_nombres):
            vacunas.append(VacunaRecomendada(
                nombre='Rabia',
                descripcion='Vacuna antirrábica. Obligatoria por ley en Colombia.',
                fecha_sugerida=_fecha(fecha_adopcion, 30) if cachorro else _fecha(fecha_adopcion, 14),
            ))

        # Refuerzo anual
        if not cachorro:
            vacunas.append(VacunaRecomendada(
                nombre='Polivalente canina (refuerzo anual)',
                descripcion='Refuerzo anual de Parvovirus + Moquillo + Hepatitis + Parainfluenza.',
                fecha_sugerida=_fecha(fecha_adopcion, 365),
                es_refuerzo=True,
            ))

        return vacunas


class ProtocoloGato:
    """Protocolo felino: Panleucopenia, Calicivirus, Rinotraqueítis, Rabia."""

    def generar(
        self,
        fecha_adopcion: date,
        edad_anios: int,
        edad_unidad: str,
        historial_nombres: set[str],
    ) -> list[VacunaRecomendada]:
        cachorro = _es_cachorro(edad_anios, edad_unidad)
        vacunas: list[VacunaRecomendada] = []

        # Panleucopenia felina
        if not _ya_vacunado('panleucopenia', historial_nombres):
            vacunas.append(VacunaRecomendada(
                nombre='Panleucopenia Felina',
                descripcion='Protege contra el Parvovirus felino, altamente contagioso.',
                fecha_sugerida=_fecha(fecha_adopcion, 7),
            ))
            if cachorro:
                vacunas.append(VacunaRecomendada(
                    nombre='Panleucopenia (refuerzo)',
                    descripcion='Refuerzo a las 3-4 semanas.',
                    fecha_sugerida=_fecha(fecha_adopcion, 28),
                    es_refuerzo=True,
                ))

        # Calicivirus
        if not _ya_vacunado('calicivirus', historial_nombres):
            vacunas.append(VacunaRecomendada(
                nombre='Calicivirus Felino',
                descripcion='Protege contra infecciones respiratorias y úlceras orales.',
                fecha_sugerida=_fecha(fecha_adopcion, 7),
            ))

        # Rinotraqueítis (Herpesvirus)
        if not _ya_vacunado('rinotraqueítis', historial_nombres) and not _ya_vacunado('rinotraquetis', historial_nombres) and not _ya_vacunado('herpesvirus', historial_nombres):
            vacunas.append(VacunaRecomendada(
                nombre='Rinotraqueítis Felina (Herpesvirus)',
                descripcion='Protege contra el herpesvirus felino tipo 1.',
                fecha_sugerida=_fecha(fecha_adopcion, 14),
            ))

        # Rabia
        if not _ya_vacunado('rabia', historial_nombres):
            vacunas.append(VacunaRecomendada(
                nombre='Rabia',
                descripcion='Vacuna antirrábica felina. Recomendada para todos los gatos.',
                fecha_sugerida=_fecha(fecha_adopcion, 30) if cachorro else _fecha(fecha_adopcion, 14),
            ))

        # Refuerzo anual triple felina
        if not cachorro:
            vacunas.append(VacunaRecomendada(
                nombre='Triple Felina (refuerzo anual)',
                descripcion='Refuerzo anual de Panleucopenia + Calicivirus + Rinotraqueítis.',
                fecha_sugerida=_fecha(fecha_adopcion, 365),
                es_refuerzo=True,
            ))

        return vacunas


class ProtocoloConejo:
    """Protocolo cunícula: Mixomatosis y Enfermedad Hemorrágica Vírica (RHD)."""

    def generar(
        self,
        fecha_adopcion: date,
        edad_anios: int,
        edad_unidad: str,
        historial_nombres: set[str],
    ) -> list[VacunaRecomendada]:
        vacunas: list[VacunaRecomendada] = []

        if not _ya_vacunado('mixomatosis', historial_nombres):
            vacunas.append(VacunaRecomendada(
                nombre='Mixomatosis',
                descripcion='Protege contra el virus de la mixomatosis en conejos.',
                fecha_sugerida=_fecha(fecha_adopcion, 14),
            ))

        if not _ya_vacunado('rhd', historial_nombres) and not _ya_vacunado('hemorrágica', historial_nombres):
            vacunas.append(VacunaRecomendada(
                nombre='Enfermedad Hemorrágica Vírica (RHD)',
                descripcion='Protege contra el calicivirus RHD, mortal en conejos.',
                fecha_sugerida=_fecha(fecha_adopcion, 14),
            ))

        return vacunas


class ProtocoloGenerico:
    """Protocolo genérico para especies sin protocolo específico (ej. hámster)."""

    def generar(
        self,
        fecha_adopcion: date,
        edad_anios: int,
        edad_unidad: str,
        historial_nombres: set[str],
    ) -> list[VacunaRecomendada]:
        return [
            VacunaRecomendada(
                nombre='Consulta veterinaria preventiva',
                descripcion=(
                    'Visita al veterinario para establecer el esquema de vacunación '
                    'específico para esta especie. El sistema no dispone de un protocolo '
                    'predefinido para esta especie.'
                ),
                fecha_sugerida=_fecha(fecha_adopcion, 7),
            )
        ]


_PROTOCOLO_POR_ESPECIE: dict[str, EspecieProtocolo] = {
    'PERRO':   ProtocoloPerro(),
    'GATO':    ProtocoloGato(),
    'CONEJO':  ProtocoloConejo(),
    'HAMSTER': ProtocoloGenerico(),
}


class VaccinationScheduleGenerator:
    """
    Genera un CalendarioGenerado dado los atributos de la mascota.

    Diseñado como servicio de dominio stateless (sin estado compartido),
    inyectable y fácilmente testeable sin base de datos.
    """

    def generate(
        self,
        especie: str,
        edad_anios: int,
        edad_unidad: str,
        historial_vacunas: list[dict],
        fecha_adopcion: date | None = None,
    ) -> CalendarioGenerado:
        if fecha_adopcion is None:
            fecha_adopcion = date.today()

        historial_nombres: set[str] = {
            v.get('nombre', '') for v in historial_vacunas if v.get('nombre')
        }

        protocolo = _PROTOCOLO_POR_ESPECIE.get(especie.upper(), ProtocoloGenerico())
        vacunas = protocolo.generar(
            fecha_adopcion=fecha_adopcion,
            edad_anios=edad_anios,
            edad_unidad=edad_unidad,
            historial_nombres=historial_nombres,
        )

        cachorro = _es_cachorro(edad_anios, edad_unidad)
        nota_edad = 'cachorro' if cachorro else 'adulto'
        nota_historial = (
            f'Se tomaron en cuenta {len(historial_nombres)} vacuna(s) del historial existente.'
            if historial_nombres else
            'No se registraron vacunas previas.'
        )
        notas = (
            f'Calendario generado para {especie.capitalize()} ({nota_edad}). '
            f'{nota_historial} '
            'Este calendario es orientativo — consulta siempre con un veterinario.'
        )

        return CalendarioGenerado(vacunas=vacunas, notas=notas)


schedule_generator = VaccinationScheduleGenerator()
