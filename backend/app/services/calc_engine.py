from __future__ import annotations

from decimal import Decimal, ROUND_CEILING
from typing import Any, Dict, List
import hashlib
import json

from app.seeds.parameters_2026 import PARAMETERS_2026
from app.seeds.catalog_seed import SURFACES, CHEMICALS, MACHINERY, CONSUMABLES
from app.schemas.quote import QuoteCalculationRequest
from app.utils.money import to_decimal, to_money

PCT = Decimal("100.0")
TWOPLACES = Decimal("0.01")
FOURPLACES = Decimal("0.0001")


class CalculationEngine:
    """Motor paramétrico determinista (cero alucinación de números).

    Reproduce las fórmulas del informe maestro Klintec v2.0:
      - MOD: suma(area_i / rendimiento_i * frecuencia_i) -> operarios -> costo legal IESS.
      - CIQ: dosificación por dilución + merma.
      - CMAQ: depreciación horaria + mantenimiento + consumibles de desgaste.
      - Consolidación: COD -> gastos administrativos + imprevistos + margen.
    """

    def __init__(self) -> None:
        self.params = PARAMETERS_2026
        self.surfaces = {s["id"]: s for s in SURFACES}
        self.chemicals = {c["id"]: c for c in CHEMICALS}
        self.machinery = {m["id"]: m for m in MACHINERY}
        self.consumables = {c["id"]: c for c in CONSUMABLES}

    @staticmethod
    def _ceil_int(value: Decimal) -> int:
        if value <= 0:
            return 0
        return int(value.to_integral_value(rounding=ROUND_CEILING))

    # ------------------------------------------------------------------- motor
    def calculate(self, req: QuoteCalculationRequest) -> Dict[str, Any]:
        lab = self.params["laborales"]
        sbu = to_decimal(lab["sbu"])
        bonus = to_decimal(req.bonificacion_especialidad or "0.00")
        horas_turno = Decimal(str(lab["horas_efectivas_por_turno"]))
        recargo_noct_pct = Decimal(str(lab["recargo_nocturno_pct"]))
        iess_patronal_pct = Decimal(str(lab["iess_patronal_pct"]))
        fondo_reserva_pct = Decimal(str(lab["fondo_reserva_pct"]))
        decimo_tercero_pct = Decimal(str(lab["decimo_tercero_pct"]))
        decimo_cuarto = to_decimal(lab["decimo_cuarto_monto"])
        vacaciones_pct = Decimal(str(lab["vacaciones_pct"]))
        factor_reemplazo = Decimal(str(lab["factor_reemplazo_ausentismo"]))
        merma_pct = Decimal(str(self.params["quimicos"]["merma_pct"]))

        dias_mes = Decimal(str(req.periodo.dias_operacion_mes))
        prop_noct = (
            Decimal(str(req.turno.proporcion_horas_nocturnas_pct)) / PCT
            if req.turno.proporcion_horas_nocturnas_pct
            else Decimal("0")
        )

        advertencias: List[Dict[str, Any]] = []

        # -------------------------------------------------------------------- MOD
        horas_dia = Decimal("0")
        for idx, surf in enumerate(req.superficies):
            cfg = self.surfaces.get(surf.superficie_id)
            if cfg is None:
                advertencias.append({
                    "codigo": "SUPERFICIE_DESCONOCIDA",
                    "mensaje": f"La superficie '{surf.superficie_id}' no existe en el catalogo y fue ignorada.",
                    "severidad": "advertencia",
                    "campo": f"superficies[{idx}].superficie_id",
                })
                continue
            if surf.rendimiento_m2_h_override:
                rend = Decimal(str(surf.rendimiento_m2_h_override))
                advertencias.append({
                    "codigo": "OVERRIDE_RENDIMIENTO",
                    "mensaje": "Se uso un rendimiento distinto al del catalogo.",
                    "severidad": "advertencia",
                    "campo": f"superficies[{idx}].rendimiento_m2_h_override",
                })
            else:
                rend = Decimal(str(cfg["rendimiento_m2_h"]))
            if rend <= 0:
                rend = Decimal("1")
            horas_dia += (Decimal(str(surf.area_m2)) / rend) * Decimal(str(surf.frecuencia_diaria))

        horas_mes = horas_dia * dias_mes
        operarios_base = self._ceil_int(horas_dia / horas_turno) if horas_turno > 0 else 0

        recargo_nocturno = (sbu + bonus) * recargo_noct_pct / PCT * prop_noct
        remuneracion_base = sbu + bonus + recargo_nocturno
        iess_patronal = remuneracion_base * iess_patronal_pct / PCT
        fondo_reserva = remuneracion_base * fondo_reserva_pct / PCT
        decimo_tercero = remuneracion_base * decimo_tercero_pct / PCT
        vacaciones = remuneracion_base * vacaciones_pct / PCT
        costo_operario = (
            remuneracion_base + iess_patronal + fondo_reserva
            + decimo_tercero + decimo_cuarto + vacaciones
        )
        mod_total = costo_operario * factor_reemplazo * Decimal(str(operarios_base))

        # Segundo escenario: plantilla definida por el horario indicado por el usuario.
        horario = req.horario_usuario
        dias_laborables = Decimal(str(horario.dias_laborables_mes))
        horas_dia_laborable = Decimal(str(horario.horas_por_dia_laborable))
        dias_fin_semana = Decimal(str(horario.dias_fin_semana_mes))
        horas_dia_fin_semana = Decimal(str(horario.horas_por_dia_fin_semana))
        horas_extra_usuario = Decimal(str(horario.horas_extra_mes))
        horas_laborables_usuario = dias_laborables * horas_dia_laborable
        horas_fin_semana_usuario = dias_fin_semana * horas_dia_fin_semana
        horas_disponibles_usuario = horas_laborables_usuario + horas_fin_semana_usuario + horas_extra_usuario
        operarios_usuario = self._ceil_int(horas_mes / horas_disponibles_usuario) if horas_disponibles_usuario > 0 else 0

        laborales_config = self.params["laborales"]
        horas_mes_jornada = Decimal(str(laborales_config["horas_mes_jornada_completa"]))
        divisor_hora_suplementaria = Decimal(str(laborales_config["divisor_hora_suplementaria"]))
        recargo_suplementarias = Decimal(str(laborales_config["recargo_hora_suplementaria_pct"]))
        recargo_fin_semana = Decimal(str(laborales_config["recargo_hora_fin_semana_pct"]))
        factor_jornada = min(Decimal("1"), (horas_laborables_usuario + horas_fin_semana_usuario) / horas_mes_jornada)
        sbu_usuario = sbu * factor_jornada
        bonus_usuario = bonus * factor_jornada
        recargo_nocturno_usuario = (sbu_usuario + bonus_usuario) * recargo_noct_pct / PCT * prop_noct
        remuneracion_base_usuario = sbu_usuario + bonus_usuario + recargo_nocturno_usuario
        valor_hora_base = (sbu_usuario + bonus_usuario) / divisor_hora_suplementaria
        prima_fin_semana = horas_fin_semana_usuario * valor_hora_base * recargo_fin_semana / PCT
        prima_horas_extra = horas_extra_usuario * valor_hora_base * recargo_suplementarias / PCT
        remuneracion_usuario = remuneracion_base_usuario + prima_fin_semana + prima_horas_extra
        iess_usuario = remuneracion_usuario * iess_patronal_pct / PCT
        fondo_usuario = remuneracion_usuario * fondo_reserva_pct / PCT
        decimo_tercero_usuario = remuneracion_usuario * decimo_tercero_pct / PCT
        vacaciones_usuario = remuneracion_usuario * vacaciones_pct / PCT
        costo_operario_usuario = (
            remuneracion_usuario + iess_usuario + fondo_usuario
            + decimo_tercero_usuario + decimo_cuarto * factor_jornada + vacaciones_usuario
        )
        mod_total_usuario = costo_operario_usuario * factor_reemplazo * Decimal(str(operarios_usuario))
        costo_mensual_usuario = {
            "sbu": to_money(sbu_usuario),
            "bonificacion_especialidad": to_money(bonus_usuario),
            "recargo_nocturno": to_money(recargo_nocturno_usuario),
            "remuneracion_base": to_money(remuneracion_usuario),
            "iess_patronal": to_money(iess_usuario),
            "fondo_reserva": to_money(fondo_usuario),
            "decimo_tercero": to_money(decimo_tercero_usuario),
            "decimo_cuarto": to_money(decimo_cuarto * factor_jornada),
            "vacaciones": to_money(vacaciones_usuario),
            "total": to_money(costo_operario_usuario),
        }

        # -------------------------------------------------------------------- CIQ
        quimico_acc: Dict[str, Dict[str, Any]] = {}
        for idx, surf in enumerate(req.superficies):
            if surf.superficie_id not in self.surfaces:
                continue
            # Contrato: si falta quimico_id, esa superficie no consume quimico
            # (sin sustituciones silenciosas).
            chem_id = surf.quimico_id
            if not chem_id:
                advertencias.append({
                    "codigo": "QUIMICO_NO_DECLARADO",
                    "mensaje": "La superficie no declara solucion quimica: no se computa consumo quimico.",
                    "severidad": "info",
                    "campo": f"superficies[{idx}].quimico_id",
                })
                continue
            chem = self.chemicals.get(chem_id)
            if chem is None:
                advertencias.append({
                    "codigo": "QUIMICO_DESCONOCIDO",
                    "mensaje": f"El quimico '{chem_id}' no existe en el catalogo y fue ignorado.",
                    "severidad": "advertencia",
                    "campo": f"superficies[{idx}].quimico_id",
                })
                continue

            rend_quim = Decimal(str(chem["rendimiento_m2_por_litro"] or 1))
            area = Decimal(str(surf.area_m2))
            freq_mes = Decimal(str(surf.frecuencia_diaria)) * dias_mes
            litros_solucion = (area * freq_mes) / rend_quim if rend_quim > 0 else Decimal("0")

            factor_dil = Decimal(str(chem["factor_dilucion"] or 1))
            if chem["convencion_dilucion"] == "solucion_total" and factor_dil > 0:
                litros_concentrado = litros_solucion / factor_dil
            else:
                litros_concentrado = litros_solucion / (Decimal("1") + factor_dil)
            litros_concentrado *= Decimal("1") + merma_pct / PCT

            acc = quimico_acc.setdefault(chem_id, {
                "chem": chem,
                "litros_solucion": Decimal("0"),
                "litros_concentrado": Decimal("0"),
            })
            acc["litros_solucion"] += litros_solucion
            acc["litros_concentrado"] += litros_concentrado

        ciq_lineas: List[Dict[str, Any]] = []
        subtotal_quimicos = Decimal("0")
        for chem_id, acc in quimico_acc.items():
            pu = to_decimal(acc["chem"]["precio_unitario"])
            costo = acc["litros_concentrado"] * pu
            subtotal_quimicos += costo
            ciq_lineas.append({
                "quimico_id": chem_id,
                "nombre": acc["chem"]["nombre"],
                "litros_solucion": float(acc["litros_solucion"].quantize(FOURPLACES)),
                "litros_concentrado": float(acc["litros_concentrado"].quantize(FOURPLACES)),
                "convencion_dilucion": acc["chem"]["convencion_dilucion"],
                "merma_pct": float(merma_pct),
                "precio_unitario_litro": to_money(pu),
                "costo": to_money(costo),
            })

        subtotal_consumibles = Decimal("0")
        subtotal_kits_epp = Decimal("0")
        detalle_consumibles: List[Dict[str, Any]] = []
        detalle_kits: List[Dict[str, Any]] = []
        for cons in req.consumibles:
            item = self.consumables.get(cons.consumible_id)
            if item is None:
                advertencias.append({
                    "codigo": "CONSUMIBLE_DESCONOCIDO",
                    "mensaje": f"El consumible '{cons.consumible_id}' no existe en el catalogo y fue ignorado.",
                    "severidad": "advertencia",
                    "campo": "consumibles",
                })
                continue
            cantidad = Decimal(str(cons.cantidad_mensual))
            pu = to_decimal(item["precio_unitario"])
            costo = cantidad * pu
            registro = {
                "id": item["id"],
                "nombre": item["nombre"],
                "unidad": item["unidad"],
                "cantidad": float(cantidad),
                "precio_unitario": to_money(pu),
                "costo": to_money(costo),
            }
            if item["categoria"] == "kit_epp":
                subtotal_kits_epp += costo
                detalle_kits.append(registro)
            else:
                subtotal_consumibles += costo
                detalle_consumibles.append(registro)

        ciq_total = subtotal_quimicos + subtotal_consumibles + subtotal_kits_epp

        # ------------------------------------------------------------------- CMAQ
        cmaq_lineas: List[Dict[str, Any]] = []
        cmaq_total = Decimal("0")
        for mq in req.maquinaria:
            m = self.machinery.get(mq.maquinaria_id)
            if m is None:
                advertencias.append({
                    "codigo": "MAQUINARIA_DESCONOCIDA",
                    "mensaje": f"La maquinaria '{mq.maquinaria_id}' no existe en el catalogo y fue ignorada.",
                    "severidad": "advertencia",
                    "campo": "maquinaria",
                })
                continue
            valor_adquisicion = to_decimal(m["valor_adquisicion"])
            valor_residual = to_decimal(m["valor_residual"])
            vida = Decimal(str(m["vida_util_horas"])) or Decimal("1")
            depreciacion_hora = (valor_adquisicion - valor_residual) / vida
            mantenimiento_hora = to_decimal(m["mantenimiento_por_hora"])
            consumibles_hora = to_decimal(m["consumibles_desgaste_por_hora"])
            costo_horario = depreciacion_hora + mantenimiento_hora + consumibles_hora
            horas = Decimal(str(mq.horas_uso_mensual))
            costo = costo_horario * horas
            cmaq_total += costo
            cmaq_lineas.append({
                "maquinaria_id": m["id"],
                "nombre": m["nombre"],
                "depreciacion_por_hora": to_money(depreciacion_hora),
                "mantenimiento_por_hora": to_money(mantenimiento_hora),
                "consumibles_por_hora": to_money(consumibles_hora),
                "costo_horario": to_money(costo_horario),
                "horas_uso_mensual": float(horas),
                "costo": to_money(costo),
            })

        # -------------------------------------------------------- Gastos varios
        gastos_varios_lineas: List[Dict[str, Any]] = []
        gastos_varios_total = Decimal("0")
        for gasto in req.gastos_varios:
            monto = Decimal(str(gasto.monto_mensual))
            gastos_varios_total += monto
            gastos_varios_lineas.append({
                "descripcion": gasto.descripcion,
                "monto_mensual": to_money(monto),
                "costo": to_money(monto),
            })

        # ------------------------------------------------------------ Consolidacion
        cod = mod_total + ciq_total + cmaq_total + gastos_varios_total
        ga_pct = Decimal(str(req.comercial.gastos_administrativos_pct))
        ir_pct = Decimal(str(req.comercial.imprevistos_riesgo_pct))
        mn_pct = Decimal(str(req.comercial.margen_neto_pct))
        descuento_pct = Decimal(str(req.comercial.descuento_pct))
        gastos_admin = cod * ga_pct / PCT
        imprevistos = cod * ir_pct / PCT
        margen = cod * mn_pct / PCT
        subtotal_oferta = cod + gastos_admin + imprevistos + margen
        descuento_comercial = subtotal_oferta * descuento_pct / PCT
        precio_final = subtotal_oferta - descuento_comercial
        cod_usuario = mod_total_usuario + ciq_total + cmaq_total + gastos_varios_total
        gastos_admin_usuario = cod_usuario * ga_pct / PCT
        imprevistos_usuario = cod_usuario * ir_pct / PCT
        margen_usuario = cod_usuario * mn_pct / PCT
        subtotal_oferta_usuario = cod_usuario + gastos_admin_usuario + imprevistos_usuario + margen_usuario
        descuento_comercial_usuario = subtotal_oferta_usuario * descuento_pct / PCT
        precio_final_usuario = subtotal_oferta_usuario - descuento_comercial_usuario
        factor_total = float(
            (Decimal("1") + ga_pct / PCT + ir_pct / PCT + mn_pct / PCT).quantize(FOURPLACES)
        )

        # -------------------------------------------------------------- Governance
        piso_inviolable = bool(req.superficies) and cod > 0 and mn_pct >= 0 and ga_pct >= 0 and ir_pct >= 0 and precio_final >= cod
        if not req.superficies:
            advertencias.append({
                "codigo": "SIN_SUPERFICIES",
                "mensaje": "No se declararon superficies: el costo operativo directo es cero.",
                "severidad": "critica",
                "campo": "superficies",
            })
        if req.proyecto.tipo_infraestructura == "hospital":
            tiene_critica = any(
                "critica" in s.superficie_id.lower() or "hospital" in s.superficie_id.lower()
                for s in req.superficies
            )
            if not tiene_critica:
                advertencias.append({
                    "codigo": "HOSPITAL_SIN_AREAS_CRITICAS",
                    "mensaje": "Se cotiza una instalacion hospitalaria sin areas criticas (UCI/quirofano) declaradas.",
                    "severidad": "advertencia",
                    "campo": "superficies",
                })
            criticas = [
                s for s in req.superficies
                if "critica" in s.superficie_id.lower() or "hospital" in s.superficie_id.lower()
            ]
            if any(s.quimico_id for s in criticas) and not any(
                s.quimico_id == "amonio_cuaternario_5ta" for s in criticas
            ):
                advertencias.append({
                    "codigo": "HOSPITAL_SIN_AMONIO_5TA",
                    "mensaje": "Riesgo tecnico: areas criticas sin amonio cuaternario de 5ta generacion declarado.",
                    "severidad": "advertencia",
                    "campo": "superficies",
                })
        if req.turno.tipo in ("nocturno", "mixto") and prop_noct <= 0:
            advertencias.append({
                "codigo": "TURNO_NOCTURNO_SIN_RECARGO",
                "mensaje": "Turno nocturno/mixto declarado con 0% de horas nocturnas: no se aplica recargo del 25%.",
                "severidad": "advertencia",
                "campo": "turno",
            })
        if ga_pct + ir_pct + mn_pct == 0:
            advertencias.append({
                "codigo": "SIN_MARGEN",
                "mensaje": "Administracion, imprevistos y margen en 0%: la oferta se emite a costo.",
                "severidad": "advertencia",
                "campo": "comercial",
            })

        # ---------------------------------------------------------------- Partidas
        partidas: List[Dict[str, Any]] = [{
            "id": "MOD-01",
            "categoria": "Nomina",
            "descripcion": (
                f"Mano de obra directa: {operarios_base} operario(s) x "
                f"${to_money(costo_operario)} x factor reemplazo {factor_reemplazo}"
            ),
            "unidad": "mes",
            "cantidad": operarios_base,
            "precio_unitario": to_money(costo_operario),
            "total": to_money(mod_total),
            "fuente": "Acuerdo Ministerial MDT-2025-195 (SBU 2026 USD 482,00)",
            "referencia_normativa": "IESS patronal 12,15% | Fondo Reserva 8,33% | Codigo del Trabajo Art. 49",
            "estado_verificacion": "verificado",
        }]

        for idx, gasto in enumerate(gastos_varios_lineas, start=1):
            partidas.append({
                "id": f"OTR-{idx:02d}",
                "categoria": "Gastos varios",
                "descripcion": gasto["descripcion"],
                "unidad": "mes",
                "cantidad": 1.0,
                "precio_unitario": gasto["monto_mensual"],
                "total": gasto["costo"],
                "fuente": "Valor mensual ingresado por el usuario",
                "referencia_normativa": None,
                "estado_verificacion": "supuesto",
            })

        for idx, linea in enumerate(ciq_lineas, start=1):
            factor = self.chemicals[linea["quimico_id"]]["factor_dilucion"]
            partidas.append({
                "id": f"CIQ-{idx:02d}",
                "categoria": "Quimicos",
                "descripcion": f"{linea['nombre']} (1:{float(factor):.0f}, merma {float(merma_pct):.0f}%)",
                "unidad": "litro",
                "cantidad": linea["litros_concentrado"],
                "precio_unitario": linea["precio_unitario_litro"],
                "total": linea["costo"],
                "fuente": "Catalogo Klintec / ficha tecnica ARCSA",
                "referencia_normativa": "ARCSA",
                "estado_verificacion": "verificado",
            })
        for idx, item in enumerate(detalle_consumibles, start=1):
            partidas.append({
                "id": f"CON-{idx:02d}",
                "categoria": "Consumibles",
                "descripcion": f"{item['nombre']} ({item['cantidad']} {item['unidad']})",
                "unidad": item["unidad"],
                "cantidad": item["cantidad"],
                "precio_unitario": item["precio_unitario"],
                "total": item["costo"],
                "fuente": "Catalogo Klintec de consumibles",
                "referencia_normativa": None,
                "estado_verificacion": "verificado",
            })
        for idx, item in enumerate(detalle_kits, start=1):
            partidas.append({
                "id": f"EPP-{idx:02d}",
                "categoria": "EPP",
                "descripcion": f"{item['nombre']} ({item['cantidad']} {item['unidad']})",
                "unidad": item["unidad"],
                "cantidad": item["cantidad"],
                "precio_unitario": item["precio_unitario"],
                "total": item["costo"],
                "fuente": "Catalogo Klintec de EPP",
                "referencia_normativa": "Seguridad y Salud Ocupacional",
                "estado_verificacion": "verificado",
            })
        for idx, linea in enumerate(cmaq_lineas, start=1):
            partidas.append({
                "id": f"CMAQ-{idx:02d}",
                "categoria": "Maquinaria",
                "descripcion": f"{linea['nombre']} ({linea['horas_uso_mensual']} h/mes)",
                "unidad": "hora",
                "cantidad": linea["horas_uso_mensual"],
                "precio_unitario": linea["costo_horario"],
                "total": linea["costo"],
                "fuente": "Depreciacion horaria (adquisicion - residual) / vida util",
                "referencia_normativa": None,
                "estado_verificacion": "verificado",
            })
        for codigo, descripcion, monto in (
            ("ADM-01", "Gastos administrativos", gastos_admin),
            ("RIE-01", "Imprevistos / riesgo", imprevistos),
            ("MAR-01", "Margen neto", margen),
        ):
            if monto > 0:
                partidas.append({
                    "id": codigo,
                    "categoria": "Comercial",
                    "descripcion": descripcion,
                    "unidad": "%",
                    "cantidad": 1.0,
                    "precio_unitario": to_money(monto),
                    "total": to_money(monto),
                    "fuente": "Parametro comercial vigente",
                    "referencia_normativa": None,
                    "estado_verificacion": "verificado",
                })
        if descuento_comercial > 0:
            partidas.append({
                "id": "DES-01",
                "categoria": "Comercial",
                "descripcion": f"Descuento comercial ({descuento_pct}%)",
                "unidad": "%",
                "cantidad": 1.0,
                "precio_unitario": to_money(-descuento_comercial),
                "total": to_money(-descuento_comercial),
                "fuente": "Descuento ingresado por el usuario",
                "referencia_normativa": None,
                "estado_verificacion": "verificado",
            })

        # -------------------------------------------------------------------- Hash
        payload = {
            "v": self.params["version_parametros"],
            "req": req.model_dump(exclude_none=True),
            "cod": float(cod.quantize(TWOPLACES)),
        }
        hash_calculo = hashlib.sha256(
            json.dumps(payload, sort_keys=True, default=str).encode()
        ).hexdigest()[:16]

        supuestos = [
            f"SBU 2026 = USD {to_money(sbu)} (MDT-2025-195).",
            f"Horas efectivas por turno = {horas_turno} h; operarios base = ceil(horas/dia / {horas_turno}).",
            f"Factor de reemplazo/ausentismo = {factor_reemplazo}.",
            "Escenario de usuario: el SBU se prorratea por horas regulares previstas hasta 40 h/semana (173,33 h/mes de referencia).",
            f"Recargo escenario usuario: {recargo_fin_semana}% en fin de semana de descanso y {recargo_suplementarias}% en horas suplementarias diurnas; valor hora = remuneracion/240.",
            (
                f"Aporte patronal IESS = {iess_patronal_pct}% + Fondo de Reserva {fondo_reserva_pct}% "
                f"+ Decimo 3ro {decimo_tercero_pct}% + Decimo 4to USD {to_money(decimo_cuarto)} "
                f"+ Vacaciones {vacaciones_pct}%."
            ),
            f"Recargo nocturno = {recargo_noct_pct}% aplicado sobre {float(prop_noct) * 100:.0f}% de horas nocturnas.",
            f"Dosificacion quimica con merma de {merma_pct}% sobre concentrado puro.",
            "Depreciacion de maquinaria por hora efectiva = (adquisicion - residual) / vida util en horas.",
            "Rendimientos de superficie basados en ISSA Cleaning Times 8va edicion (Metric LATAM).",
        ]

        fuentes = [
            {"tipo": "normativa", "referencia": "Acuerdo Ministerial MDT-2025-195 (SBU 2026 USD 482,00)", "version": "2026"},
            {"tipo": "normativa", "referencia": "IESS - Tasas de aportacion (12,15% patronal, 8,33% fondo de reserva)", "version": "2026"},
            {"tipo": "estandar", "referencia": "ISSA Cleaning Times 8th Edition Metric LATAM", "version": "v8"},
            {"tipo": "parametro", "referencia": "Klintec Parametros Vigentes", "version": self.params["version_parametros"]},
        ]

        return {
            "version_parametros": self.params["version_parametros"],
            "hash_calculo": hash_calculo,
            "mod": {
                "horas_requeridas_dia": float(horas_dia.quantize(TWOPLACES)),
                "horas_requeridas_mes": float(horas_mes.quantize(TWOPLACES)),
                "operarios_base": operarios_base,
                "costo_mensual_por_operario": {
                    "sbu": to_money(sbu),
                    "bonificacion_especialidad": to_money(bonus),
                    "recargo_nocturno": to_money(recargo_nocturno),
                    "remuneracion_base": to_money(remuneracion_base),
                    "iess_patronal": to_money(iess_patronal),
                    "fondo_reserva": to_money(fondo_reserva),
                    "decimo_tercero": to_money(decimo_tercero),
                    "decimo_cuarto": to_money(decimo_cuarto),
                    "vacaciones": to_money(vacaciones),
                    "total": to_money(costo_operario),
                },
                "factor_reemplazo_ausentismo": float(factor_reemplazo),
                "total": to_money(mod_total),
                "escenario_usuario": {
                    "horas_laborables_mes_por_operario": float(horas_laborables_usuario.quantize(TWOPLACES)),
                    "horas_fin_semana_mes_por_operario": float(horas_fin_semana_usuario.quantize(TWOPLACES)),
                    "horas_extra_mes_por_operario": float(horas_extra_usuario.quantize(TWOPLACES)),
                    "horas_disponibles_mes_por_operario": float(horas_disponibles_usuario.quantize(TWOPLACES)),
                    "recargo_fin_semana_por_operario": to_money(prima_fin_semana),
                    "recargo_horas_extra_por_operario": to_money(prima_horas_extra),
                    "operarios_requeridos": operarios_usuario,
                    "costo_mensual_por_operario": costo_mensual_usuario,
                    "total": to_money(mod_total_usuario),
                },
            },
            "ciq": {
                "lineas": ciq_lineas,
                "subtotal_quimicos": to_money(subtotal_quimicos),
                "subtotal_consumibles": to_money(subtotal_consumibles),
                "subtotal_kits_epp": to_money(subtotal_kits_epp),
                "total": to_money(ciq_total),
            },
            "cmaq": {
                "lineas": cmaq_lineas,
                "total": to_money(cmaq_total),
            },
            "gastos_varios": {
                "lineas": gastos_varios_lineas,
                "total": to_money(gastos_varios_total),
            },
            "consolidacion": {
                "costo_operativo_directo": to_money(cod),
                "gastos_administrativos": to_money(gastos_admin),
                "imprevistos_riesgo": to_money(imprevistos),
                "margen_neto": to_money(margen),
                "factor_total": factor_total,
                "subtotal_oferta": to_money(subtotal_oferta),
                "descuento_pct": float(descuento_pct),
                "descuento_comercial": to_money(descuento_comercial),
                "precio_final": to_money(precio_final),
                "piso_inviolable_respetado": piso_inviolable,
                "costo_operativo_directo_usuario": to_money(cod_usuario),
                "gastos_administrativos_usuario": to_money(gastos_admin_usuario),
                "imprevistos_riesgo_usuario": to_money(imprevistos_usuario),
                "margen_neto_usuario": to_money(margen_usuario),
                "subtotal_oferta_usuario": to_money(subtotal_oferta_usuario),
                "descuento_comercial_usuario": to_money(descuento_comercial_usuario),
                "precio_final_usuario": to_money(precio_final_usuario),
            },
            "partidas": partidas,
            "supuestos": supuestos,
            "advertencias": advertencias,
            "fuentes": fuentes,
        }


_engine = CalculationEngine()


def get_engine() -> CalculationEngine:
    return _engine
