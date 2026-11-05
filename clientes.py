# clientes.py
# Administra la lista de clientes mediante diccionarios de Python.

def registrar_cliente(lista_clientes, id_cliente, nombre, telefono, direccion, correo, rubro):
    """Crea un cliente como diccionario y lo añade a la lista general."""
    cliente = {
        "id": id_cliente,
        "nombre": nombre,
        "telefono": telefono,
        "direccion": direccion,
        "correo": correo,
        "rubro": rubro
    }
    lista_clientes.append(cliente)
    print(f"\n[✓] Cliente '{nombre}' ({rubro}) registrado con éxito con ID {id_cliente}.")
    return cliente

def buscar_cliente(lista_clientes, criterio):
    """Busca un cliente por ID o por nombre."""
    resultados = []
    criterio_str = str(criterio).lower().strip()
    for c in lista_clientes:
        if criterio_str in str(c["id"]).lower() or criterio_str in c["nombre"].lower():
            resultados.append(c)
    return resultados

def modificar_cliente(lista_clientes, id_cliente, campo, nuevo_valor):
    """Modifica un campo específico del cliente."""
    for c in lista_clientes:
        if c["id"] == id_cliente:
            if campo in c:
                c[campo] = nuevo_valor
                print(f"[✓] Campo '{campo}' actualizado a '{nuevo_valor}' para el cliente ID {id_cliente}.")
                return True
            else:
                print(f"[X] El campo '{campo}' no existe en la ficha de cliente.")
                return False
    print(f"[X] Cliente ID {id_cliente} no encontrado.")
    return False

def eliminar_cliente(lista_clientes, id_cliente):
    """Elimina un cliente por su ID."""
    for c in lista_clientes:
        if c["id"] == id_cliente:
            lista_clientes.remove(c)
            print(f"[✓] Cliente ID {id_cliente} eliminado del sistema.")
            return True
    print(f"[X] Cliente ID {id_cliente} no encontrado.")
    return False

def mostrar_clientes(lista_clientes):
    """Muestra la lista de clientes registrados o un mensaje si está vacía."""
    if not lista_clientes:
        print("\n[!] No se han registrado clientes aún en el sistema.")
        return False
    
    print("\n=========================================================================")
    print(f"{'ID':<6} | {'Nombre':<22} | {'Rubro/Servicio':<16} | {'Teléfono':<12} | {'Correo':<18}")
    print("=========================================================================")
    for c in lista_clientes:
        print(f"{c['id']:<6} | {c['nombre']:<22} | {c['rubro']:<16} | {c['telefono']:<12} | {c['correo']:<18}")
    print("=========================================================================\n")
    return True