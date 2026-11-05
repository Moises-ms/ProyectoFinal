# presupuestos.py
# Administra ítems de cotización usando una Lista Simplemente Enlazada basada en diccionarios.

def crear_nodo_item(concepto, tipo, cantidad, precio_unitario):
    """Crea un nodo para un ítem del presupuesto."""
    return {
        "concepto": concepto,
        "tipo": tipo,
        "cantidad": cantidad,
        "precio_unitario": precio_unitario,
        "subtotal_item": cantidad * precio_unitario,
        "siguiente": None
    }

def crear_presupuesto(id_presupuesto, cliente):
    """Inicializa la estructura del presupuesto."""
    return {
        "id": id_presupuesto,
        "cliente": cliente,
        "cabeza": None,  # Cabeza de la lista simplemente enlazada
        "subtotal": 0.0,
        "descuento": 0.0,
        "impuesto": 0.0,
        "total": 0.0
    }

def agregar_item(presupuesto, concepto, tipo, cantidad, precio_unitario):
    """Inserta un nuevo ítem al final de la lista simplemente enlazada."""
    nuevo_nodo = crear_nodo_item(concepto, tipo, cantidad, precio_unitario)
    
    if presupuesto["cabeza"] is None:
        presupuesto["cabeza"] = nuevo_nodo
    else:
        actual = presupuesto["cabeza"]
        while actual["siguiente"] is not None:
            actual = actual["siguiente"]
        actual["siguiente"] = nuevo_nodo
        
    calcular_subtotal(presupuesto)
    print(f"\n[✓] Ítem '{concepto}' agregado a la cotización.")

def eliminar_item(presupuesto, concepto):
    """Elimina un nodo de la lista enlazada por el nombre del concepto."""
    if presupuesto["cabeza"] is None:
        print("\n[!] La cotización actual no contiene ningún ítem para eliminar.")
        return False

    actual = presupuesto["cabeza"]
    previo = None

    while actual is not None:
        if actual["concepto"].lower().strip() == concepto.lower().strip():
            if previo is None:
                presupuesto["cabeza"] = actual["siguiente"]
            else:
                previo["siguiente"] = actual["siguiente"]
            
            calcular_subtotal(presupuesto)
            print(f"\n[✓] Ítem '{concepto}' eliminado de la cotización.")
            return True
        previo = actual
        actual = actual["siguiente"]

    print(f"\n[X] No se encontró el ítem '{concepto}' en la cotización.")
    return False

def calcular_subtotal(presupuesto):
    """Recorre la lista simplemente enlazada para calcular el total del presupuesto."""
    subtotal_total = 0.0
    actual = presupuesto["cabeza"]
    
    while actual is not None:
        subtotal_total += actual["subtotal_item"]
        actual = actual["siguiente"]
        
    presupuesto["subtotal"] = subtotal_total
    presupuesto["total"] = max(0.0, subtotal_total - presupuesto["descuento"] + presupuesto["impuesto"])
    return subtotal_total

def mostrar_presupuesto(presupuesto):
    """Imprime el desglose completo de la cotización actual."""
    print(f"\n=========================================================================")
    print(f"                       COTIZACIÓN / PRESUPUESTO N° {presupuesto['id']}")
    cliente = presupuesto["cliente"]
    nombre_cli = cliente["nombre"] if isinstance(cliente, dict) else cliente
    rubro_cli = cliente.get("rubro", "General") if isinstance(cliente, dict) else "General"
    print(f" CLIENTE: {nombre_cli} | RUBRO/SERVICIO: {rubro_cli}")
    print(f"=========================================================================")
    
    actual = presupuesto["cabeza"]
    if actual is None:
        print(" [ No se han agregado ítems o conceptos a esta cotización ]")
    else:
        print(f"{'Tipo':<14} | {'Concepto / Descripción':<25} | {'Cant.':<6} | {'P. Unit':<10} | {'Subtotal':<10}")
        print("-" * 75)
        while actual is not None:
            print(f"{actual['tipo']:<14} | {actual['concepto']:<25} | {actual['cantidad']:<6} | ${actual['precio_unitario']:<9.2f} | ${actual['subtotal_item']:<9.2f}")
            actual = actual["siguiente"]
            
    print(f"-------------------------------------------------------------------------")
    print(f" SUBTOTAL:   ${presupuesto['subtotal']:.2f}")
    if presupuesto["descuento"] > 0:
        print(f" DESCUENTO: -${presupuesto['descuento']:.2f}")
    if presupuesto["impuesto"] > 0:
        print(f" IMPUESTOS: +${presupuesto['impuesto']:.2f}")
    print(f" TOTAL:      ${presupuesto['total']:.2f}")
    print(f"=========================================================================\n")