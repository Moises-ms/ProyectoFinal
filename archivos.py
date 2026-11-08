# archivos.py
# Persistencia en disco y generación de PDF oficial. SIN JSON, SIN CSV, SIN POO.
import os
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

CARPETA = "datos"

def _crear_carpeta():
    if not os.path.exists(CARPETA):
        os.makedirs(CARPETA)

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

def cargar_presupuesto(ruta, modulo_presupuestos):
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
    p["subtotal"] = float(datos.get("subtotal", 0.0))
    p["descuento"] = float(datos.get("descuento", 0.0))
    p["impuesto"] = float(datos.get("impuesto", 0.0))
    p["total"] = float(datos.get("total", 0.0))

    i += 1
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
    return ruta

def exportar_presupuesto_pdf(presupuesto):
    """Genera la cotización en PDF usando reportlab canvas."""
    _crear_carpeta()
    ruta_pdf = CARPETA + "/cotizacion_{}.pdf".format(presupuesto["id"])
    c = canvas.Canvas(ruta_pdf, pagesize=letter)
    ancho, alto = letter

    c.setFont("Helvetica-Bold", 18)
    c.drawString(50, alto - 50, "COTIZACIÓN N° {}".format(presupuesto["id"]))

    c.setFont("Helvetica", 11)
    cliente = presupuesto["cliente"]
    nombre_cli = cliente["nombre"] if isinstance(cliente, dict) else cliente
    rubro_cli = cliente.get("rubro", "General") if isinstance(cliente, dict) else "General"

    c.drawString(50, alto - 75, "Cliente: {}".format(nombre_cli))
    c.drawString(50, alto - 90, "Rubro / Especialidad: {}".format(rubro_cli))
    c.line(50, alto - 100, ancho - 50, alto - 100)

    y = alto - 125
    c.setFont("Helvetica-Bold", 10)
    c.drawString(50, y, "Tipo")
    c.drawString(140, y, "Concepto / Descripción")
    c.drawString(340, y, "Cant.")
    c.drawString(400, y, "P. Unit ($)")
    c.drawString(480, y, "Subtotal ($)")

    c.line(50, y - 5, ancho - 50, y - 5)
    y -= 25

    c.setFont("Helvetica", 10)
    actual = presupuesto["cabeza"]
    while actual is not None:
        c.drawString(50, y, str(actual["tipo"]))
        c.drawString(140, y, str(actual["concepto"])[:30])
        c.drawString(340, y, str(actual["cantidad"]))
        c.drawString(400, y, "${:.2f}".format(actual["precio_unitario"]))
        c.drawString(480, y, "${:.2f}".format(actual["subtotal_item"]))
        y -= 20
        actual = actual["siguiente"]
        if y < 100:
            c.showPage()
            y = alto - 50

    c.line(50, y, ancho - 50, y)
    y -= 25
    c.setFont("Helvetica-Bold", 11)
    c.drawString(360, y, "Subtotal: ${:.2f}".format(presupuesto["subtotal"]))
    y -= 18
    if presupuesto.get("descuento", 0) > 0:
        c.drawString(360, y, "Descuento: -${:.2f}".format(presupuesto["descuento"]))
        y -= 18
    if presupuesto.get("impuesto", 0) > 0:
        c.drawString(360, y, "Impuestos: +${:.2f}".format(presupuesto["impuesto"]))
        y -= 18
    c.setFont("Helvetica-Bold", 13)
    c.drawString(360, y, "TOTAL FINAL: ${:.2f}".format(presupuesto["total"]))

    c.save()
    return ruta_pdf

def leer_catalogo_csv():
    ruta = CARPETA + "/catalogo.csv"
    items = []
    if not os.path.exists(ruta):
        return items
    archivo = open(ruta, "r", encoding="utf-8")
    primera = True
    for linea in archivo:
        linea = linea.strip()
        if not linea or primera:
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