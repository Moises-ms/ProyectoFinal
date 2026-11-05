# historial_calculos.py
# Administra Cola de trabajos, Pila para deshacer e Historial con Lista Doblemente Enlazada.

# ==========================================
# 1. COLA (Queue - Trabajos Pendientes)
# ==========================================
def crear_cola_cotizaciones():
    return {"elementos": []}

def encolar_cotizacion(cola, cliente, descripcion_trabajo):
    solicitud = {
        "cliente": cliente,
        "descripcion": descripcion_trabajo
    }
    cola["elementos"].append(solicitud)
    print(f"\n[✓] Solicitud de trabajo agregada a la COLA de espera (Posición #{len(cola['elementos'])}).")

def procesar_cotizacion(cola):
    if not cola["elementos"]:
        print("\n[!] No hay solicitudes de trabajo pendientes en la cola.")
        return None
    solicitud = cola["elementos"].pop(0)
    print(f"\n[✓] Procesando solicitud de: {solicitud['cliente']['nombre']}")
    print(f"    Requerimiento: {solicitud['descripcion']}")
    print(f"    (Quedan {len(cola['elementos'])} solicitudes pendientes en la cola)")
    return solicitud

# ==========================================
# 2. PILA (Stack - Deshacer Ítems)
# ==========================================
def crear_pila_deshacer():
    return {"elementos": []}

def apilar_operacion(pila, accion, datos):
    pila["elementos"].append({
        "accion": accion,
        "datos": datos
    })

def deshacer_operacion(presupuesto, pila, funcion_eliminar_item):
    if not pila["elementos"]:
        print("\n[!] No hay acciones recientes en la pila para deshacer en esta cotización.")
        return False

    ultima_op = pila["elementos"].pop()
    if ultima_op["accion"] == "AGREGAR_ITEM":
        concepto = ultima_op["datos"]["concepto"]
        print(f"\n[↩] Deshaciendo: Eliminando el ítem agregando anteriormente ('{concepto}')...")
        funcion_eliminar_item(presupuesto, concepto)
        return True
    return False

# ==========================================
# 3. LISTA DOBLEMENTE ENLAZADA (Historial)
# ==========================================
def crear_nodo_historial(presupuesto):
    return {
        "presupuesto": presupuesto,
        "anterior": None,
        "siguiente": None
    }

def crear_historial():
    return {
        "cabeza": None,
        "cola": None
    }

def agregar_historial(historial, presupuesto):
    nuevo_nodo = crear_nodo_historial(presupuesto)
    if historial["cabeza"] is None:
        historial["cabeza"] = nuevo_nodo
        historial["cola"] = nuevo_nodo
    else:
        nuevo_nodo["anterior"] = historial["cola"]
        historial["cola"]["siguiente"] = nuevo_nodo
        historial["cola"] = nuevo_nodo
    print(f"\n[✓] Cotización N° {presupuesto['id']} registrada en el historial general.")

def recorrer_historial_adelante(historial):
    actual = historial["cabeza"]
    if actual is None:
        print("\n[!] No se ha guardado ninguna cotización en el historial aún.")
        return False

    print("\n=========================================================================")
    print("      HISTORIAL DE COTIZACIONES (RECORRIDO HACIA ADELANTE: PRIMERAS PRIMERO)")
    print("=========================================================================")
    while actual is not None:
        p = actual["presupuesto"]
        cli = p["cliente"]["nombre"] if isinstance(p["cliente"], dict) else p["cliente"]
        print(f"Cotización ID: {p['id']:<5} | Cliente: {cli:<22} | Total: ${p['total']:.2f}")
        actual = actual["siguiente"]
    print("=========================================================================\n")
    return True

def recorrer_historial_atras(historial):
    actual = historial["cola"]
    if actual is None:
        print("\n[!] No se ha guardado ninguna cotización en el historial aún.")
        return False

    print("\n=========================================================================")
    print("      HISTORIAL DE COTIZACIONES (RECORRIDO HACIA ATRÁS: RECIENTES PRIMERO)")
    print("=========================================================================")
    while actual is not None:
        p = actual["presupuesto"]
        cli = p["cliente"]["nombre"] if isinstance(p["cliente"], dict) else p["cliente"]
        print(f"Cotización ID: {p['id']:<5} | Cliente: {cli:<22} | Total: ${p['total']:.2f}")
        actual = actual["anterior"]
    print("=========================================================================\n")
    return True

# ==========================================
# 4. FUNCIONES DE CÁLCULO
# ==========================================
def aplicar_descuento_a_presupuesto(presupuesto, porcentaje_descuento):
    subtotal = presupuesto["subtotal"]
    if subtotal == 0:
        print("\n[!] Agregue ítems a la cotización antes de aplicar un descuento.")
        return
    monto_desc = subtotal * (porcentaje_descuento / 100.0)
    presupuesto["descuento"] = monto_desc
    presupuesto["total"] = max(0.0, subtotal - monto_desc + presupuesto["impuesto"])
    print(f"\n[✓] Descuento del {porcentaje_descuento}% (-${monto_desc:.2f}) aplicado.")

def aplicar_impuesto_a_presupuesto(presupuesto, porcentaje_impuesto):
    subtotal_con_desc = max(0.0, presupuesto["subtotal"] - presupuesto["descuento"])
    if subtotal_con_desc == 0 and presupuesto["subtotal"] == 0:
        print("\n[!] Agregue ítems a la cotización antes de calcular impuestos.")
        return
    monto_imp = subtotal_con_desc * (porcentaje_impuesto / 100.0)
    presupuesto["impuesto"] = monto_imp
    presupuesto["total"] = subtotal_con_desc + monto_imp
    print(f"\n[✓] Impuesto/IVA del {porcentaje_impuesto}% (+${monto_imp:.2f}) aplicado.")