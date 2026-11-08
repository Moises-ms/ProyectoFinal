# historial_calculos.py
# Administra Cola de trabajos, Pila para deshacer e Historial con Lista Doblemente Enlazada.

def crear_cola_cotizaciones():
    return {"elementos": []}

def encolar_cotizacion(cola, cliente, descripcion_trabajo):
    solicitud = {
        "cliente": cliente,
        "descripcion": descripcion_trabajo
    }
    cola["elementos"].append(solicitud)

def procesar_cotizacion(cola):
    if not cola["elementos"]:
        return None
    return cola["elementos"].pop(0)

def crear_pila_deshacer():
    return {"elementos": []}

def apilar_operacion(pila, accion, datos):
    pila["elementos"].append({
        "accion": accion,
        "datos": datos
    })

def deshacer_operacion(presupuesto, pila, funcion_eliminar_item):
    if not pila["elementos"]:
        return False

    ultima_op = pila["elementos"].pop()
    if ultima_op["accion"] == "AGREGAR_ITEM":
        concepto = ultima_op["datos"]["concepto"]
        funcion_eliminar_item(presupuesto, concepto)
        return True
    return False

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

def recorrer_historial_adelante(historial):
    actual = historial["cabeza"]
    if actual is None:
        return False

    print("\n=== HISTORIAL (ADELANTE) ===")
    while actual is not None:
        p = actual["presupuesto"]
        cli = p["cliente"]["nombre"] if isinstance(p["cliente"], dict) else p["cliente"]
        print(f"ID: {p['id']} | Cliente: {cli} | Total: ${p['total']:.2f}")
        actual = actual["siguiente"]
    return True

def recorrer_historial_atras(historial):
    actual = historial["cola"]
    if actual is None:
        return False

    print("\n=== HISTORIAL (ATRAS) ===")
    while actual is not None:
        p = actual["presupuesto"]
        cli = p["cliente"]["nombre"] if isinstance(p["cliente"], dict) else p["cliente"]
        print(f"ID: {p['id']} | Cliente: {cli} | Total: ${p['total']:.2f}")
        actual = actual["anterior"]
    return True

def aplicar_descuento_a_presupuesto(presupuesto, porcentaje_descuento):
    subtotal = presupuesto["subtotal"]
    if subtotal == 0:
        return
    monto_desc = subtotal * (porcentaje_descuento / 100.0)
    presupuesto["descuento"] = monto_desc
    presupuesto["total"] = max(0.0, subtotal - monto_desc + presupuesto["impuesto"])

def aplicar_impuesto_a_presupuesto(presupuesto, porcentaje_impuesto):
    subtotal_con_desc = max(0.0, presupuesto["subtotal"] - presupuesto["descuento"])
    if subtotal_con_desc == 0 and presupuesto["subtotal"] == 0:
        return
    monto_imp = subtotal_con_desc * (porcentaje_impuesto / 100.0)
    presupuesto["impuesto"] = monto_imp
    presupuesto["total"] = subtotal_con_desc + monto_imp

def crear_cola_exportacion():
    return {"elementos": []}

def encolar_para_exportar(cola, presupuesto):
    cola["elementos"].append(presupuesto)

def procesar_cola_exportacion(cola, historial, archivos):
    if not cola["elementos"]:
        return False
    p = cola["elementos"].pop(0)
    agregar_historial(historial, p)
    archivos.guardar_presupuesto(p)
    archivos.exportar_presupuesto_csv(p)
    archivos.exportar_presupuesto_pdf(p)  # <--- Genera el PDF automáticamente
    return True