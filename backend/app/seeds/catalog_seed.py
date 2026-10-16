SURFACES = [
    {"id": "piso_vinilo", "nombre": "Piso vinílico (mantenimiento)", "rendimiento_m2_h": 350.0, "fuente": "ISSA Cleaning Times LATAM v8"},
    {"id": "piso_porcelanato", "nombre": "Porcelanato / cerámica", "rendimiento_m2_h": 400.0, "fuente": "ISSA Cleaning Times LATAM v8"},
    {"id": "bano", "nombre": "Sanitarios y baterías (general)", "rendimiento_m2_h": 150.0, "fuente": "ISSA Cleaning Times LATAM v8"},
    {"id": "muebles", "nombre": "Mobiliario y escritorios", "rendimiento_m2_h": 500.0, "fuente": "ISSA Cleaning Times LATAM v8"},
    {"id": "oficina_hospitalaria", "nombre": "Área clínica - Hospital", "rendimiento_m2_h": 120.0, "fuente": "ISSA Cleaning Times LATAM v8 (Hospital)"},
    {"id": "pasillo_industrial", "nombre": "Pasillo industrial (grasa leve)", "rendimiento_m2_h": 200.0, "fuente": "ISSA Cleaning Times LATAM v8"},
    {"id": "area_critica", "nombre": "Área crítica (UCI / Quirófano)", "rendimiento_m2_h": 90.0, "fuente": "ISSA Cleaning Times LATAM v8 (Crítico)"},
]

CHEMICALS = [
    {"id": "amonio_cuaternario_5ta", "nombre": "Amonio cuaternario 5ª generación", "factor_dilucion": 64.0, "convencion_dilucion": "partes_agua", "rendimiento_m2_por_litro": 40.0, "precio_unitario": "15.00", "unidad_precio": "litro", "ficha_tecnica_url": None},
    {"id": "desinfectante_neutro", "nombre": "Desinfectante neutro", "factor_dilucion": 100.0, "convencion_dilucion": "partes_agua", "rendimiento_m2_por_litro": 60.0, "precio_unitario": "8.50", "unidad_precio": "litro", "ficha_tecnica_url": None},
    {"id": "desengrasante_alcalino", "nombre": "Desengrasante alcalino industrial", "factor_dilucion": 20.0, "convencion_dilucion": "partes_agua", "rendimiento_m2_por_litro": 25.0, "precio_unitario": "9.80", "unidad_precio": "litro", "ficha_tecnica_url": None},
    {"id": "detergente_biodegradable", "nombre": "Detergente biodegradable", "factor_dilucion": 150.0, "convencion_dilucion": "partes_agua", "rendimiento_m2_por_litro": 80.0, "precio_unitario": "5.50", "unidad_precio": "litro", "ficha_tecnica_url": None},
    {"id": "desinfectante_clorado", "nombre": "Hipoclorito / Clorado controlado", "factor_dilucion": 50.0, "convencion_dilucion": "partes_agua", "rendimiento_m2_por_litro": 50.0, "precio_unitario": "4.20", "unidad_precio": "litro", "ficha_tecnica_url": None},
]

MACHINERY = [
    {"id": "fregadora_auto", "nombre": "Fregadora automática 20\"", "valor_adquisicion": "5200.00", "valor_residual": "520.00", "vida_util_horas": 6000, "mantenimiento_por_hora": "0.85", "consumibles_desgaste_por_hora": "0.45"},
    {"id": "fregadora_compacta", "nombre": "Fregadora compacta hospitalaria", "valor_adquisicion": "3800.00", "valor_residual": "380.00", "vida_util_horas": 5000, "mantenimiento_por_hora": "0.70", "consumibles_desgaste_por_hora": "0.35"},
    {"id": "aspiradora_hepa", "nombre": "Aspiradora industrial HEPA", "valor_adquisicion": "1850.00", "valor_residual": "185.00", "vida_util_horas": 4000, "mantenimiento_por_hora": "0.40", "consumibles_desgaste_por_hora": "0.25"},
    {"id": "hidrolavadora", "nombre": "Hidrolavadora industrial", "valor_adquisicion": "2650.00", "valor_residual": "265.00", "vida_util_horas": 5000, "mantenimiento_por_hora": "0.55", "consumibles_desgaste_por_hora": "0.30"},
    {"id": "nebulizador_ulv", "nombre": "Nebulizador ULV (desinfección)", "valor_adquisicion": "4500.00", "valor_residual": "450.00", "vida_util_horas": 4500, "mantenimiento_por_hora": "1.20", "consumibles_desgaste_por_hora": "0.40"},
]

CONSUMABLES = [
    {"id": "microfibra", "nombre": "Paños de microfibra (pack)", "categoria": "consumible", "unidad": "pack", "precio_unitario": "5.00"},
    {"id": "fundas_descarte", "nombre": "Fundas para desechos clínicos", "categoria": "consumible", "unidad": "rollo", "precio_unitario": "3.50"},
    {"id": "guantes_nitrilo", "nombre": "Guantes nitrilo", "categoria": "kit_epp", "unidad": "caja", "precio_unitario": "8.50"},
    {"id": "mascarilla_n95", "nombre": "Mascarilla N95/KN95", "categoria": "kit_epp", "unidad": "caja", "precio_unitario": "12.00"},
    {"id": "batas_quirurgicas", "nombre": "Batas quirúrgicas desechables", "categoria": "kit_epp", "unidad": "caja", "precio_unitario": "15.00"},
]