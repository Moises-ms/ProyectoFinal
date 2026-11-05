# archivos.py
# Persistencia con archivos de texto plano. SIN json, SIN csv, SIN POO.
import os  # solo para crear la carpeta datos/

CARPETA = "datos"

def _crear_carpeta():
    if not os.path.exists(CARPETA):
        os.makedirs(CARPETA)

# ==========================================
# CLIENTES
# ==========================================
def guardar_clientes(lista_clientes):
    _crear_carpeta()
    ruta = CARPETA + "/clientes.txt"
    archivo = open(ruta, "w", encoding="utf-8")
    archivo.write("#id|nombre|telefono|direccion|correo|rubro\n")
    for c in lista_clientes:
        linea = "{}|{}|{}|{}|{}|{}\n".format(
            c["id"], c["nombre"], c["telefono"],
            c["direccion"], c["correo"], c["rubro"]
        )
        archivo.write(linea)
    archivo.close()
    print("[✓] Clientes guardados en datos/clientes.txt")

def cargar_clientes():
    _crear_carpeta()
    ruta = CARPETA + "/clientes.txt"
    lista = []
    if not os.path.exists(ruta):
        return lista
    archivo = open(ruta, "r", encoding="utf-8")
    for linea in archivo:
        linea = linea.strip()
        if linea == "" or linea.startswith("#"):
            continue
        partes = linea.split("|")
        if len(partes) < 6:
            continue
        lista.append({
            "id": int(partes[0]),
            "nombre": partes[1],
            "telefono": partes[2],
            "direccion": partes[3],
            "correo": partes[4],
            "rubro": partes[5]
        })
    archivo.close()
    return lista

# ==========================================
# PRESUPUESTOS (guardado y carga)
# ==========================================
def guardar_presupuesto(presupuesto):
    _crear_carpeta()
    ruta = CARPETA + "/presupuesto_{}.txt".format(presupuesto["id"])
    archivo = open(ruta, "w", encoding="utf-8")

    nombre_cli = presupuesto["cliente"]["nombre"] if isinstance(presupuesto["cliente"], dict) else presupuesto["cliente"]
    rubro_cli = presupuesto["cliente"].get("rubro", "General") if isinstance(presupuesto["cliente"], dict) else "General"

    archivo.write("===PRESUPUESTO===\n")
    archivo.write("id={}\n".format(presupuesto["id"]))
    archivo.write("cliente={}\n".format(nombre_cli))
    archivo.write("rubro={}\n".format(rubro_cli))
    archivo.write("subtotal={}\n".format(presupuesto["subtotal"]))
    archivo.write("descuento={}\n".format(presupuesto["descuento"]))
    archivo.write("impuesto={}\n".format(presupuesto["impuesto"]))
    archivo.write("total={}\n".format(presupuesto["total"]))
    archivo.write("---ITEMS---\n")

    actual = presupuesto["cabeza"]
    while actual is not None:
        archivo.write("{}|{}|{}|{}|{}\n".format(
            actual["concepto"], actual["tipo"],
            actual["cantidad"], actual["precio_unitario"],
            actual["subtotal_item"]
        ))
        actual = actual["siguiente"]
    archivo.write("===FIN===\n")
    archivo.close()
    print("[✓] Presupuesto N° {} guardado en disco.".format(presupuesto["id"]))

def cargar_presupuesto(ruta, modulo_presupuestos):
    """Reconstruye un presupuesto llamando al módulo presupuestos."""
    archivo = open(ruta, "r", encoding="utf-8")
    lineas = archivo.readlines()
    archivo.close()

    datos = {}
    i = 1
    while i < len(lineas) and not lineas[i].startswith("---"):
        linea = lineas[i].strip()
        if "=" in linea:
            clave, valor = linea.split("=", 1)
            datos[clave] = valor
        i += 1

    cliente = {"nombre": datos.get("cliente", "?"), "rubro": datos.get("rubro", "General")}
    p = modulo_presupuestos.crear_presupuesto(int(datos["id"]), cliente)
    p["subtotal"] = float(datos["subtotal"])
    p["descuento"] = float(datos["descuento"])
    p["impuesto"] = float(datos["impuesto"])
    p["total"] = float(datos["total"])

    i += 1  # saltar ---ITEMS---
    while i < len(lineas) and not lineas[i].startswith("==="):
        linea = lineas[i].strip()
        if linea:
            partes = linea.split("|")
            if len(partes) >= 5:
                nuevo = modulo_presupuestos.crear_nodo_item(
                    partes[0], partes[1], float(partes[2]), float(partes[3])
                )
                if p["cabeza"] is None:
                    p["cabeza"] = nuevo
                else:
                    actual = p["cabeza"]
                    while actual["siguiente"] is not None:
                        actual = actual["siguiente"]
                    actual["siguiente"] = nuevo
        i += 1
    return p

def cargar_todos_presupuestos(modulo_presupuestos):
    _crear_carpeta()
    lista = []
    for nombre in os.listdir(CARPETA):
        if nombre.startswith("presupuesto_") and nombre.endswith(".txt"):
            lista.append(cargar_presupuesto(CARPETA + "/" + nombre, modulo_presupuestos))
    # Ordenar por id
    lista_ordenada = []
    for p in lista:
        insertado = False
        for j in range(len(lista_ordenada)):
            if p["id"] < lista_ordenada[j]["id"]:
                lista_ordenada.insert(j, p)
                insertado = True
                break
        if not insertado:
            lista_ordenada.append(p)
    return lista_ordenada

# ==========================================
# EXPORTAR A CSV
# ==========================================
def exportar_presupuesto_csv(presupuesto):
    _crear_carpeta()
    ruta = CARPETA + "/exportacion_{}.csv".format(presupuesto["id"])
    archivo = open(ruta, "w", encoding="utf-8")
    archivo.write("Tipo,Concepto,Cantidad,PrecioUnitario,Subtotal\n")
    actual = presupuesto["cabeza"]
    while actual is not None:
        archivo.write("{},{},{},{},{}\n".format(
            actual["tipo"], actual["concepto"],
            actual["cantidad"], actual["precio_unitario"],
            actual["subtotal_item"]
        ))
        actual = actual["siguiente"]
    archivo.write("SUBTOTAL,,,,{}\n".format(presupuesto["subtotal"]))
    archivo.write("DESCUENTO,,,,{}\n".format(presupuesto["descuento"]))
    archivo.write("IMPUESTO,,,,{}\n".format(presupuesto["impuesto"]))
    archivo.write("TOTAL,,,,{}\n".format(presupuesto["total"]))
    archivo.close()
    print("[✓] Exportado a {}".format(ruta))
    return ruta

# ==========================================
# LEER CATÁLOGO CSV
# ==========================================
def leer_catalogo_csv():
    ruta = CARPETA + "/catalogo.csv"
    items = []
    if not os.path.exists(ruta):
        return items
    archivo = open(ruta, "r", encoding="utf-8")
    primera = True
    for linea in archivo:
        linea = linea.strip()
        if not linea:
            continue
        if primera:
            primera = False
            continue
        partes = linea.split(",")
        if len(partes) >= 4:
            items.append({
                "tipo": partes[0],
                "concepto": partes[1],
                "cantidad": float(partes[2]),
                "precio_unitario": float(partes[3])
            })
    archivo.close()
    return items