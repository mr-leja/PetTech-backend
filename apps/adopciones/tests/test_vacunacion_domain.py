"""
Tests unitarios — dominio de vacunación (vaccination.py)
Cubre: VaccinationScheduleGenerator, protocolos por especie,
       detección cachorro/adulto, filtrado por historial.
"""
from datetime import date

from apps.adopciones.domain.vaccination import (
    VaccinationScheduleGenerator,
    ProtocoloPerro,
    ProtocoloGato,
    ProtocoloConejo,
    ProtocoloGenerico,
    CalendarioGenerado,
    VacunaRecomendada,
    _es_cachorro,
    _ya_vacunado,
)

# ---------------------------------------------------------------------------
# Helpers internos
# ---------------------------------------------------------------------------


class TestEsCachorro:
    def test_perro_3_meses_es_cachorro(self):
        assert _es_cachorro(3, "MESES") is True

    def test_perro_12_meses_es_cachorro(self):
        assert _es_cachorro(12, "MESES") is True

    def test_perro_13_meses_no_es_cachorro(self):
        assert _es_cachorro(13, "MESES") is False

    def test_perro_1_anio_es_cachorro(self):
        # 1 año = 12 meses → límite exacto → sigue siendo cachorro
        assert _es_cachorro(1, "ANIOS") is True

    def test_perro_2_anios_no_es_cachorro(self):
        assert _es_cachorro(2, "ANIOS") is False

    def test_perro_0_meses_es_cachorro(self):
        assert _es_cachorro(0, "MESES") is True


class TestYaVacunado:
    def test_detecta_vacuna_exacta(self):
        assert _ya_vacunado("Rabia", {"Rabia"}) is True

    def test_detecta_vacuna_case_insensitive(self):
        assert _ya_vacunado("rabia", {"RABIA"}) is True

    def test_deteccion_parcial_subword(self):
        # "parvovirus" contiene "parvo"
        assert _ya_vacunado("parvo", {"Parvovirus"}) is True

    def test_no_detecta_vacuna_ausente(self):
        assert _ya_vacunado("Rabia", {"Parvovirus"}) is False

    def test_historial_vacio(self):
        assert _ya_vacunado("Rabia", set()) is False


# ---------------------------------------------------------------------------
# Protocolo Perro
# ---------------------------------------------------------------------------


class TestProtocoloPerro:
    FECHA = date(2026, 1, 1)
    protocolo = ProtocoloPerro()

    def _gen(self, edad_anios, edad_unidad, historial=None):
        return self.protocolo.generar(self.FECHA, edad_anios, edad_unidad, historial or set())

    def test_cachorro_tiene_parvovirus(self):
        vacunas = self._gen(3, "MESES")
        nombres = [v.nombre for v in vacunas]
        assert "Parvovirus" in nombres

    def test_cachorro_tiene_refuerzo_parvovirus(self):
        vacunas = self._gen(3, "MESES")
        refuerzos = [v for v in vacunas if v.es_refuerzo and "Parvovirus" in v.nombre]
        assert len(refuerzos) >= 1

    def test_cachorro_tiene_rabia(self):
        vacunas = self._gen(3, "MESES")
        assert any("Rabia" in v.nombre for v in vacunas)

    def test_adulto_no_tiene_refuerzo_parvovirus(self):
        vacunas = self._gen(5, "ANIOS")
        refuerzo_parvo = [v for v in vacunas if v.es_refuerzo and "Parvovirus" in v.nombre]
        assert len(refuerzo_parvo) == 0

    def test_adulto_tiene_polivalente_refuerzo(self):
        vacunas = self._gen(5, "ANIOS")
        assert any("Polivalente" in v.nombre and v.es_refuerzo for v in vacunas)

    def test_vacuna_existente_se_excluye(self):
        vacunas = self._gen(3, "MESES", historial={"Parvovirus"})
        assert not any(v.nombre == "Parvovirus" for v in vacunas)

    def test_rabia_excluida_si_esta_en_historial(self):
        vacunas = self._gen(3, "MESES", historial={"rabia"})
        assert not any("Rabia" in v.nombre for v in vacunas)

    def test_fechas_son_futuras_desde_adopcion(self):
        vacunas = self._gen(3, "MESES")
        for v in vacunas:
            assert v.fecha_sugerida > self.FECHA

    def test_cachorro_tiene_moquillo(self):
        vacunas = self._gen(2, "MESES")
        assert any("Moquillo" in v.nombre for v in vacunas)

    def test_cachorro_tiene_hepatitis(self):
        vacunas = self._gen(2, "MESES")
        assert any("Hepatitis" in v.nombre for v in vacunas)


# ---------------------------------------------------------------------------
# Protocolo Gato
# ---------------------------------------------------------------------------


class TestProtocoloGato:
    FECHA = date(2026, 1, 1)
    protocolo = ProtocoloGato()

    def _gen(self, edad_anios, edad_unidad, historial=None):
        return self.protocolo.generar(self.FECHA, edad_anios, edad_unidad, historial or set())

    def test_cachorro_tiene_panleucopenia(self):
        vacunas = self._gen(2, "MESES")
        assert any("Panleucopenia" in v.nombre for v in vacunas)

    def test_cachorro_tiene_calicivirus(self):
        vacunas = self._gen(2, "MESES")
        assert any("Calicivirus" in v.nombre for v in vacunas)

    def test_cachorro_tiene_rinotraqueitis(self):
        vacunas = self._gen(2, "MESES")
        assert any("Rinotraqueítis" in v.nombre for v in vacunas)

    def test_adulto_tiene_triple_felina_refuerzo(self):
        vacunas = self._gen(4, "ANIOS")
        assert any("Triple Felina" in v.nombre and v.es_refuerzo for v in vacunas)

    def test_panleucopenia_excluida_si_esta_en_historial(self):
        vacunas = self._gen(2, "MESES", historial={"panleucopenia"})
        assert not any("Panleucopenia" in v.nombre for v in vacunas)


# ---------------------------------------------------------------------------
# Protocolo Conejo
# ---------------------------------------------------------------------------


class TestProtocoloConejo:
    FECHA = date(2026, 1, 1)
    protocolo = ProtocoloConejo()

    def _gen(self, historial=None):
        return self.protocolo.generar(self.FECHA, 2, "ANIOS", historial or set())

    def test_tiene_mixomatosis(self):
        vacunas = self._gen()
        assert any("Mixomatosis" in v.nombre for v in vacunas)

    def test_tiene_rhd(self):
        vacunas = self._gen()
        assert any("RHD" in v.nombre for v in vacunas)

    def test_mixomatosis_excluida_si_en_historial(self):
        vacunas = self._gen(historial={"Mixomatosis"})
        assert not any("Mixomatosis" in v.nombre for v in vacunas)


# ---------------------------------------------------------------------------
# Protocolo Genérico
# ---------------------------------------------------------------------------


class TestProtocoloGenerico:
    FECHA = date(2026, 1, 1)
    protocolo = ProtocoloGenerico()

    def test_genera_consulta_veterinaria(self):
        vacunas = self.protocolo.generar(self.FECHA, 1, "ANIOS", set())
        assert len(vacunas) == 1
        assert "veterinaria" in vacunas[0].nombre.lower() or "veterinario" in vacunas[0].descripcion.lower()


# ---------------------------------------------------------------------------
# VaccinationScheduleGenerator (servicio de dominio completo)
# ---------------------------------------------------------------------------


class TestVaccinationScheduleGenerator:
    generator = VaccinationScheduleGenerator()
    FECHA = date(2026, 3, 1)

    def test_retorna_calendario_generado(self):
        result = self.generator.generate("PERRO", 3, "MESES", [], self.FECHA)
        assert isinstance(result, CalendarioGenerado)

    def test_vacunas_son_instancias_correctas(self):
        result = self.generator.generate("GATO", 2, "MESES", [], self.FECHA)
        for v in result.vacunas:
            assert isinstance(v, VacunaRecomendada)

    def test_especie_desconocida_usa_generico(self):
        result = self.generator.generate("DRAGÓN", 1, "ANIOS", [], self.FECHA)
        assert len(result.vacunas) >= 1

    def test_historial_previo_filtra_vacunas(self):
        """Con historial completo de rabia no debe haber vacuna de rabia."""
        historial = [{"nombre": "Rabia"}, {"nombre": "Parvovirus"}, {"nombre": "Moquillo"}]
        result = self.generator.generate("PERRO", 3, "MESES", historial, self.FECHA)
        nombres = [v.nombre for v in result.vacunas]
        assert "Rabia" not in nombres

    def test_notas_incluyen_especie(self):
        result = self.generator.generate("GATO", 4, "ANIOS", [], self.FECHA)
        assert "Gato" in result.notas or "gato" in result.notas.lower()

    def test_notas_mencionan_historial_vacio(self):
        result = self.generator.generate("PERRO", 2, "ANIOS", [], self.FECHA)
        assert "vacunas previas" in result.notas.lower() or "No se registraron" in result.notas

    def test_notas_mencionan_historial_existente(self):
        historial = [{"nombre": "Rabia"}]
        result = self.generator.generate("PERRO", 2, "ANIOS", historial, self.FECHA)
        assert "1" in result.notas

    def test_fecha_adopcion_none_usa_hoy(self):
        """Cuando fecha_adopcion es None no debe lanzar excepción."""
        result = self.generator.generate("CONEJO", 1, "ANIOS", [])
        assert isinstance(result, CalendarioGenerado)

    def test_gato_cachorro_genera_vacunas(self):
        result = self.generator.generate("GATO", 1, "MESES", [], self.FECHA)
        assert len(result.vacunas) > 0

    def test_perro_adulto_genera_vacunas(self):
        result = self.generator.generate("PERRO", 5, "ANIOS", [], self.FECHA)
        assert len(result.vacunas) > 0

    def test_especie_case_insensitive(self):
        result_upper = self.generator.generate("PERRO", 3, "MESES", [], self.FECHA)
        result_lower = self.generator.generate("perro", 3, "MESES", [], self.FECHA)
        assert len(result_upper.vacunas) == len(result_lower.vacunas)

    def test_conejo_genera_vacunas(self):
        result = self.generator.generate("CONEJO", 2, "ANIOS", [], self.FECHA)
        assert len(result.vacunas) >= 2
