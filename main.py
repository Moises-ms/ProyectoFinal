# main.py
# Controlador principal del sistema y servidor Web Flask.

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
import clientes
import presupuestos
import historial_calculos
import archivos

app = Flask(__name__)

# ==========================================
# ESTADO DE DATOS EN MEMORIA
# ==========================================
lista_clientes = archivos.cargar_clientes()
historial_presupuestos = historial_calculos.crear_historial()
cola_trabajos = historial_calculos.crear_cola_cotizaciones()
cola_exportacion = historial_calculos.crear_cola_exportacion()

# Reconstruir el historial desde disco al iniciar
cargados = archivos.cargar_todos_presupuestos(presupuestos)
for p in cargados:
    historial_calculos.agregar_historial(historial_presupuestos, p)
    archivos.exportar_presupuesto_pdf(p)

secuencia_cliente_id = max([c["id"] for c in lista_clientes], default=0) + 1
secuencia_presupuesto_id = max([p["id"] for p in cargados], default=99) + 1

cotizacion_activa = None
pila_undo_activa = None


# ==========================================
# RUTAS DE LA APLICACIÓN WEB
# ==========================================

@app.route("/")
def index():
    total_clientes = len(lista_clientes)
    total_pendientes = len(cola_trabajos["elementos"])
    
    total_cotizaciones = 0
    actual = historial_presupuestos["cabeza"]
    while actual is not None:
        total_cotizaciones += 1
        actual = actual["siguiente"]

    return render_template(
        "index.html",
        total_clientes=total_clientes,
        total_pendientes=total_pendientes,
        total_cotizaciones=total_cotizaciones
    )


# ------------------------------------------
# GESTIÓN COMPLETA DE CLIENTES (CRUD)
# ------------------------------------------
@app.route("/clientes", methods=["GET", "POST"])
def gestion_clientes():
    global secuencia_cliente_id

    if request.method == "POST":
        nombre = request.form.get("nombre", "").strip()
        rubro = request.form.get("rubro", "").strip() or "General"
        telefono = request.form.get("telefono", "").strip() or "Sin teléfono"
        direccion = request.form.get("direccion", "").strip() or "Sin dirección"
        correo = request.form.get("correo", "").strip() or "Sin correo"

        if nombre:
            clientes.registrar_cliente(lista_clientes, secuencia_cliente_id, nombre, telefono, direccion, correo, rubro)
            secuencia_cliente_id += 1
            archivos.guardar_clientes(lista_clientes)
            return redirect(url_for("gestion_clientes"))

    return render_template("clientes.html", lista_clientes=lista_clientes)


@app.route("/clientes/modificar", methods=["POST"])
def modificar_cliente_ruta():
    id_cli = int(request.form.get("cliente_id"))
    campo = request.form.get("campo")
    nuevo_valor = request.form.get("nuevo_valor", "").strip()

    if nuevo_valor:
        clientes.modificar_cliente(lista_clientes, id_cli, campo, nuevo_valor)
        archivos.guardar_clientes(lista_clientes)

    return redirect(url_for("gestion_clientes"))


@app.route("/clientes/eliminar/<int:id_cli>", methods=["POST"])
def eliminar_cliente_ruta(id_cli):
    clientes.eliminar_cliente(lista_clientes, id_cli)
    archivos.guardar_clientes(lista_clientes)
    return redirect(url_for("gestion_clientes"))


# ------------------------------------------
# COLA DE ATENCIÓN DE CLIENTES
# ------------------------------------------
@app.route("/cola", methods=["GET", "POST"])
def gestion_cola():
    mensaje = None

    if request.method == "POST":
        accion = request.form.get("accion")

        if accion == "encolar":
            id_cli = int(request.form.get("cliente_id"))
            encontrados = clientes.buscar_cliente(lista_clientes, id_cli)
            if encontrados:
                desc = request.form.get("descripcion", "").strip() or "Cotización general"
                historial_calculos.encolar_cotizacion(cola_trabajos, encontrados[0], desc)
                mensaje = "Solicitud agregada a la cola de atención."

        elif accion == "procesar":
            atendido = historial_calculos.procesar_cotizacion(cola_trabajos)
            if atendido:
                mensaje = f"Se atendió la solicitud de {atendido['cliente']['nombre']}."
            else:
                mensaje = "La cola de trabajo está vacía."

    return render_template(
        "cola.html",
        cola_trabajos=cola_trabajos["elementos"],
        lista_clientes=lista_clientes,
        mensaje=mensaje
    )


# ------------------------------------------
# CREACIÓN Y EDICIÓN DE COTIZACIÓN
# ------------------------------------------
@app.route("/cotizar", methods=["GET", "POST"])
def iniciar_cotizacion():
    global cotizacion_activa, pila_undo_activa, secuencia_presupuesto_id

    if request.method == "POST":
        id_cli = int(request.form.get("cliente_id"))
        encontrados = clientes.buscar_cliente(lista_clientes, id_cli)

        if encontrados:
            secuencia_presupuesto_id += 1
            cotizacion_activa = presupuestos.crear_presupuesto(secuencia_presupuesto_id, encontrados[0])
            pila_undo_activa = historial_calculos.crear_pila_deshacer()
            return redirect(url_for("editar_cotizacion"))

    return render_template("cotizar.html", lista_clientes=lista_clientes)


@app.route("/cotizar/editar", methods=["GET", "POST"])
def editar_cotizacion():
    global cotizacion_activa, pila_undo_activa

    if cotizacion_activa is None:
        return redirect(url_for("iniciar_cotizacion"))

    if request.method == "POST":
        accion = request.form.get("accion")

        if accion == "agregar_item":
            tipo = request.form.get("tipo", "").strip() or "General"
            concepto = request.form.get("concepto", "").strip()
            cantidad = float(request.form.get("cantidad", 1))
            precio = float(request.form.get("precio", 0.0))

            if concepto and cantidad > 0 and precio >= 0:
                presupuestos.agregar_item(cotizacion_activa, concepto, tipo, cantidad, precio)
                historial_calculos.apilar_operacion(pila_undo_activa, "AGREGAR_ITEM", {"concepto": concepto})

        elif accion == "eliminar_item":
            concepto = request.form.get("concepto", "").strip()
            if concepto:
                presupuestos.eliminar_item(cotizacion_activa, concepto)

        elif accion == "deshacer":
            historial_calculos.deshacer_operacion(cotizacion_activa, pila_undo_activa, presupuestos.eliminar_item)

        elif accion == "descuento":
            pct = float(request.form.get("porcentaje_descuento", 0))
            historial_calculos.aplicar_descuento_a_presupuesto(cotizacion_activa, pct)

        elif accion == "impuesto":
            pct = float(request.form.get("porcentaje_impuesto", 0))
            historial_calculos.aplicar_impuesto_a_presupuesto(cotizacion_activa, pct)

        elif accion == "finalizar":
            historial_calculos.encolar_para_exportar(cola_exportacion, cotizacion_activa)
            historial_calculos.procesar_cola_exportacion(cola_exportacion, historial_presupuestos, archivos)
            cotizacion_activa = None
            pila_undo_activa = None
            return redirect(url_for("ver_historial"))

        elif accion == "cancelar":
            cotizacion_activa = None
            pila_undo_activa = None
            return redirect(url_for("index"))

    items_lista = []
    actual = cotizacion_activa["cabeza"]
    while actual is not None:
        items_lista.append(actual)
        actual = actual["siguiente"]

    return render_template(
        "editar_cotizacion.html",
        presupuesto=cotizacion_activa,
        items=items_lista
    )


# ------------------------------------------
# HISTORIAL Y DESCARGA DE PDF
# ------------------------------------------
@app.route("/historial")
def ver_historial():
    orden = request.args.get("orden", "adelante")
    cotizaciones = []

    if orden == "atras":
        actual = historial_presupuestos["cola"]
        while actual is not None:
            cotizaciones.append(actual["presupuesto"])
            actual = actual["anterior"]
    else:
        actual = historial_presupuestos["cabeza"]
        while actual is not None:
            cotizaciones.append(actual["presupuesto"])
            actual = actual["siguiente"]

    return render_template("historial.html", cotizaciones=cotizaciones, orden=orden)


@app.route("/descargar_pdf/<int:id_presupuesto>")
def descargar_pdf(id_presupuesto):
    nombre_pdf = f"cotizacion_{id_presupuesto}.pdf"
    return send_from_directory("datos", nombre_pdf)


if __name__ == "__main__":
    print("\n========================================================")
    print("  INICIANDO COTIZADOR WEB DESDE MAIN.PY")
    print("========================================================")
    print(" Servidor corriendo en: http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)