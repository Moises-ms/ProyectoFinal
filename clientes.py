# clientes.py
# Administra la lista de clientes mediante diccionarios de Python.

def registrar_cliente(lista_clientes, id_cliente, nombre, telefono, direccion, correo, rubro):
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
    resultados = []
    criterio_str = str(criterio).lower().strip()
    for c in lista_clientes:
        if criterio_str in str(c["id"]).lower() or criterio_str in c["nombre"].lower():
            resultados.append(c)
    return resultados

def modificar_cliente(lista_clientes, id_cliente, campo, nuevo_valor):
    for c in lista_clientes:
        if c["id"] == id_cliente:
            if campo in c:
                c[campo] = nuevo_valor
                return True
            return False
    return False

def eliminar_cliente(lista_clientes, id_cliente):
    for c in lista_clientes:
        if c["id"] == id_cliente:
            lista_clientes.remove(c)
            return True
    return False

def mostrar_clientes(lista_clientes):
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