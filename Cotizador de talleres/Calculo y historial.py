import copy

# ==========================================
# INTEGRANTE 3: CÁLCULOS E HISTORIAL
# Presupuestos para Freelancers y Talleres
# ==========================================

# ------------------------------------------
# 1. FUNCIONES MATEMÁTICAS / CÁLCULOS
# ------------------------------------------

def calcular_descuento(subtotal, porcentaje_descuento):
    """Calcula el monto nominal a descontar."""
    return subtotal * (porcentaje_descuento / 100.0)

def calcular_ganancia(subtotal_neto, porcentaje_ganancia):
    """Calcula el margen de ganancia sobre el valor neto."""
    return subtotal_neto * (porcentaje_ganancia / 100.0)

def calcular_impuesto(base_imponible, porcentaje_impuesto):
    """Calcula el tributo/IVA sobre la base imponible."""
    return base_imponible * (porcentaje_impuesto / 100.0)


# ------------------------------------------
# 2. ESTRUCTURA: PILA (STACK)
# Aplicación: Deshacer últimas operaciones
# ------------------------------------------

def crear_pila():
    return []

def apilar_estado(pila, estado_actual):
    """Guarda un respaldo (snapshot) del presupuesto antes de modificarlo."""
    pila.append(copy.deepcopy(estado_actual))

def deshacer_operacion(pila, estado_actual):
    """
    Revierte el presupuesto al último estado guardado en la pila (LIFO).
    """
    if not pila:
        print("⚠️ [Pila Vacía] No hay operaciones para deshacer.")
        return estado_actual
    
    ultimo_estado = pila.pop()
    print("↺ [Deshacer] Se ha restaurado la versión previa del presupuesto.")
    return ultimo_estado


# ------------------------------------------
# 3. ESTRUCTURA: COLA (QUEUE)
# Aplicación: Procesar cotizaciones en orden de llegada
# ------------------------------------------

def crear_cola():
    return []

def encolar_solicitud(cola, cliente, items, pct_desc=0, pct_gan=20, pct_imp=16):
    """Agrega una solicitud a la cola de atención (FIFO)."""
    solicitud = {
        "cliente": cliente,
        "items": items,
        "pct_desc": pct_desc,
        "pct_gan": pct_gan,
        "pct_imp": pct_imp
    }
    cola.append(solicitud)
    print(f"📥 [Cola] Solicitud de '{cliente}' ingresada. En espera: {len(cola)}")

def procesar_cotizacion(cola, lista_historial):
    """
    Procesa la primera solicitud en la cola (FIFO), calcula montos
    y la registra en la lista doblemente enlazada de historial.
    """
    if not cola:
        print("⚠️ [Cola Vacía] No hay solicitudes pendientes de procesar.")
        return None
    
    # Extraer primer elemento (FIFO)
    solicitud = cola.pop(0)
    
    # 1. Sumar subtotal bruto desde la lista de ítems
    subtotal_bruto = 0.0
    for item in solicitud["items"]:
        subtotal_bruto += item["cantidad"] * item["precio_unitario"]
        
    # 2. Aplicar funciones de cálculo del módulo
    monto_desc = calcular_descuento(subtotal_bruto, solicitud["pct_desc"])
    subtotal_neto = subtotal_bruto - monto_desc
    
    monto_gan = calcular_ganancia(subtotal_neto, solicitud["pct_gan"])
    base_imponible = subtotal_neto + monto_gan
    
    monto_imp = calcular_impuesto(base_imponible, solicitud["pct_imp"])
    total_final = base_imponible + monto_imp
    
    # 3. Estructurar el presupuesto final
    presupuesto = {
        "cliente": solicitud["cliente"],
        "items": solicitud["items"],
        "subtotal": round(subtotal_bruto, 2),
        "descuento": round(monto_desc, 2),
        "subtotal_neto": round(subtotal_neto, 2),
        "ganancia": round(monto_gan, 2),
        "impuesto": round(monto_imp, 2),
        "total": round(total_final, 2)
    }
    
    # 4. Guardar en el historial doblemente enlazado
    agregar_historial(lista_historial, presupuesto)
    print(f"✅ [Procesado] Cotización de '{solicitud['cliente']}' completada (Total: ${presupuesto['total']}).")
    return presupuesto


# ------------------------------------------
# 4. ESTRUCTURA: LISTA DOBLEMENTE ENLAZADA
# Aplicación: Recorrer historial hacia adelante y hacia atrás
# ------------------------------------------

def crear_nodo_historial(presupuesto):
    return {
        "datos": presupuesto,
        "anterior": None,
        "siguiente": None
    }

def crear_lista_doble():
    return {
        "cabeza": None,
        "cola": None,
        "cursor": None,  # Puntero de navegación activa
        "longitud": 0
    }

def agregar_historial(lista_doble, presupuesto):
    """Inserta un presupuesto al final de la lista doblemente enlazada."""
    nuevo_nodo = crear_nodo_historial(presupuesto)
    
    if lista_doble["cabeza"] is None:
        lista_doble["cabeza"] = nuevo_nodo
        lista_doble["cola"] = nuevo_nodo
    else:
        nuevo_nodo["anterior"] = lista_doble["cola"]
        lista_doble["cola"]["siguiente"] = nuevo_nodo
        lista_doble["cola"] = nuevo_nodo
        
    lista_doble["cursor"] = nuevo_nodo
    lista_doble["longitud"] += 1

def navegar_historial_atras(lista_doble):
    """Mueve el cursor hacia la cotización anterior."""
    if lista_doble["cursor"] and lista_doble["cursor"]["anterior"]:
        lista_doble["cursor"] = lista_doble["cursor"]["anterior"]
        return lista_doble["cursor"]["datos"]
    elif lista_doble["cursor"]:
        print("📌 Inicio del historial alcanzado.")
        return lista_doble["cursor"]["datos"]
    return None

def navegar_historial_adelante(lista_doble):
    """Mueve el cursor hacia la siguiente cotización."""
    if lista_doble["cursor"] and lista_doble["cursor"]["siguiente"]:
        lista_doble["cursor"] = lista_doble["cursor"]["siguiente"]
        return lista_doble["cursor"]["datos"]
    elif lista_doble["cursor"]:
        print("📌 Final del historial alcanzado.")
        return lista_doble["cursor"]["datos"]
    return None


# ==========================================
# DEMOSTRACIÓN / PRUEBA DE INTEGRACIÓN
# ==========================================

if __name__ == "__main__":
    print("=== INICIALIZANDO ESTRUCTURAS DEL INTEGRANTE 3 ===\n")
    
    pila_deshacer = crear_pila()
    cola_solicitudes = crear_cola()
    historial = crear_lista_doble()

    # 1. ENCOLAR SOLICITUDES (Prueba de Cola)
    items_cliente1 = [
        {"descripcion": "Mano de obra - Reparación motor", "cantidad": 1, "precio_unitario": 150.0},
        {"descripcion": "Filtro de aceite", "cantidad": 2, "precio_unitario": 12.5}
    ]
    encolar_solicitud(cola_solicitudes, "Taller Mecánico El Rayo", items_cliente1, pct_desc=5, pct_gan=20, pct_imp=16)

    items_cliente2 = [
        {"descripcion": "Diseño de logotipo", "cantidad": 1, "precio_unitario": 200.0},
        {"descripcion": "Manual de marca", "cantidad": 1, "precio_unitario": 100.0}
    ]
    encolar_solicitud(cola_solicitudes, "Estudio Creativo FX", items_cliente2, pct_desc=10, pct_gan=25, pct_imp=16)

    # 2. PROCESAR COTIZACIONES (Prueba de procesar_cotizacion)
    print("\n--- Procesando Cola (FIFO) ---")
    presupuesto1 = procesar_cotizacion(cola_solicitudes, historial)
    presupuesto2 = procesar_cotizacion(cola_solicitudes, historial)

    # 3. NAVEGAR EN EL HISTORIAL (Prueba de Lista Doblemente Enlazada)
    print("\n--- Navegación por el Historial (Lista Doble) ---")
    print(f"Registro actual (último): {historial['cursor']['datos']['cliente']}")
    
    atras = navegar_historial_atras(historial)
    print(f"Navegando hacia atrás -> Cliente: {atras['cliente']}")
    
    adelante = navegar_historial_adelante(historial)
    print(f"Navegando hacia adelante -> Cliente: {adelante['cliente']}")

    # 4. PROBAR EDICIÓN Y DESHACER (Prueba de Pila y deshacer_operacion)
    print("\n--- Prueba de Deshacer (Pila LIFO) ---")
    presupuesto_trabajo = copy.deepcopy(presupuesto1)
    
    # Respaldar estado original en la Pila
    apilar_estado(pila_deshacer, presupuesto_trabajo)
    
    # Modificación accidental/errónea
    presupuesto_trabajo["total"] = 9999.99
    print(f"Total tras modificación: ${presupuesto_trabajo['total']}")
    
    # Deshacer cambio
    presupuesto_trabajo = deshacer_operacion(pila_deshacer, presupuesto_trabajo)
    print(f"Total restaurado con éxito: ${presupuesto_trabajo['total']}")