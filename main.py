# main.py
# Controlador principal del sistema con validación de entradas y estados vacíos.

import clientes
import presupuestos
import historial_calculos

def solicitar_entero(mensaje):
    """Solicita un número entero válido."""
    while True:
        try:
            val = int(input(mensaje))
            return val
        except ValueError:
            print("\n[X] Entrada inválida. Por favor, ingrese un número entero.")

def solicitar_flotante(mensaje):
    """Solicita un número flotante no negativo."""
    while True:
        try:
            val = float(input(mensaje))
            if val < 0:
                print("\n[X] Ingrese un monto numérico positivo.")
                continue
            return val
        except ValueError:
            print("\n[X] Entrada inválida. Ingrese un valor numérico válido.")

def main():
    # Estructuras de datos principales
    lista_clientes = []
    cola_trabajos = historial_calculos.crear_cola_cotizaciones()
    historial_presupuestos = historial_calculos.crear_historial()
    
    secuencia_cliente_id = 1
    secuencia_presupuesto_id = 100

    while True:
        print("\n========================================================")
        print("    SISTEMA DE COTIZACIONES DE FREELANCERS Y TALLERES")
        print("========================================================")
        print("1. Registrar nuevo cliente")
        print("2. Ver lista de clientes registrados")
        print("3. Agregar solicitud de trabajo a la COLA de espera")
        print("4. Atender siguiente trabajo de la COLA")
        print("5. CREAR NUEVA COTIZACIÓN")
        print("6. Ver Historial de Cotizaciones (Adelante / Atrás)")
        print("7. Salir del programa")
        print("--------------------------------------------------------")
        opcion = input("\nSeleccione una opción (1-7): ").strip()

        # -----------------------------------------------------
        # 1. REGISTRAR CLIENTE
        # -----------------------------------------------------
        if opcion == "1":
            print("\n--- REGISTRO DE NUEVO CLIENTE ---")
            nombre = input("Nombre del cliente o empresa: ").strip()
            if not nombre:
                print("\n[X] El nombre del cliente no puede estar vacío.")
                continue

            rubro = input("Rubro / Especialidad (ej. Electricidad, Pintura, Software): ").strip() or "General"
            tel = input("Teléfono de contacto: ").strip() or "Sin teléfono"
            direccion = input("Dirección: ").strip() or "Sin dirección"
            correo = input("Correo electrónico: ").strip() or "Sin correo"
            print("Cliente registrado exitosamente!")

            clientes.registrar_cliente(lista_clientes, secuencia_cliente_id, nombre, tel, direccion, correo, rubro)
            secuencia_cliente_id += 1

        # -----------------------------------------------------
        # 2. VER CLIENTES REGISTRADOS
        # -----------------------------------------------------
        elif opcion == "2":
            clientes.mostrar_clientes(lista_clientes)

        # -----------------------------------------------------
        # 3. ENCOLAR TRABAJO
        # -----------------------------------------------------
        elif opcion == "3":
            if not lista_clientes:
                print("\n[!] No se han registrado clientes aún en el sistema. Registre un cliente antes de recibir solicitudes.")
                continue

            clientes.mostrar_clientes(lista_clientes)
            id_cli = solicitar_entero("Ingrese el ID del cliente que solicita la cotización: ")
            encontrados = clientes.buscar_cliente(lista_clientes, id_cli)

            if encontrados:
                cli = encontrados[0]
                desc = input(f"\nDescripción breve del trabajo solicitado para {cli['nombre']}: ").strip()
                if not desc:
                    desc = "Cotización general de servicio"
                historial_calculos.encolar_cotizacion(cola_trabajos, cli, desc)
            else:
                print(f"\n[X] No se encontró ningún cliente con el ID {id_cli}.")

        # -----------------------------------------------------
        # 4. ATENDER TRABAJO DE LA COLA
        # -----------------------------------------------------
        elif opcion == "4":
            historial_calculos.procesar_cotizacion(cola_trabajos)

        # -----------------------------------------------------
        # 5. CREAR COTIZACIÓN
        # -----------------------------------------------------
        elif opcion == "5":
            if not lista_clientes:
                print("\n[!] No se han registrado clientes aún en el sistema. Debe registrar un cliente para crear una cotización.")
                continue

            clientes.mostrar_clientes(lista_clientes)
            id_cli = solicitar_entero("Ingrese el ID del cliente para el que realizará la cotización: ")
            encontrados = clientes.buscar_cliente(lista_clientes, id_cli)

            if not encontrados:
                print(f"\n[X] No se encontró el cliente con ID {id_cli}.")
                continue

            cliente_seleccionado = encontrados[0]
            secuencia_presupuesto_id += 1
            nuevo_presupuesto = presupuestos.crear_presupuesto(secuencia_presupuesto_id, cliente_seleccionado)
            pila_undo = historial_calculos.crear_pila_deshacer()

            # Submenú dinámico de la cotización
            while True:
                presupuestos.mostrar_presupuesto(nuevo_presupuesto)
                print("\n--- OPCIONES DE EDICIÓN DE COTIZACIÓN ---")
                print("1. Agregar Ítem / Concepto (Material o Mano de obra)")
                print("2. Eliminar Ítem por nombre")
                print("3. Deshacer última adición (PILA)")
                print("4. Aplicar porcentaje de descuento")
                print("5. Aplicar porcentaje de impuesto / IVA")
                print("6. Finalizar y guardar cotización en HISTORIAL")
                print("7. Cancelar cotización actual")
                
                sub_op = input("\nSeleccione una opción (1-7): ").strip()

                if sub_op == "1":
                    tipo = input("Tipo de ítem (ej. Material / Mano de Obra / Equipo): ").strip() or "General"
                    concepto = input("Nombre o descripción del concepto: ").strip()
                    if not concepto:
                        print("\n[X] El nombre del concepto no puede estar vacío.")
                        continue
                    cant = solicitar_flotante("Cantidad: ")
                    precio = solicitar_flotante("Precio Unitario ($): ")

                    presupuestos.agregar_item(nuevo_presupuesto, concepto, tipo, cant, precio)
                    historial_calculos.apilar_operacion(pila_undo, "AGREGAR_ITEM", {"concepto": concepto})

                elif sub_op == "2":
                    if nuevo_presupuesto["cabeza"] is None:
                        print("\n[!] La cotización actual no contiene ítems para eliminar.")
                    else:
                        concepto = input("Ingrese el nombre del concepto que desea eliminar: ").strip()
                        presupuestos.eliminar_item(nuevo_presupuesto, concepto)

                elif sub_op == "3":
                    historial_calculos.deshacer_operacion(nuevo_presupuesto, pila_undo, presupuestos.eliminar_item)

                elif sub_op == "4":
                    pct = solicitar_flotante("Ingrese el % de descuento a aplicar: ")
                    historial_calculos.aplicar_descuento_a_presupuesto(nuevo_presupuesto, pct)

                elif sub_op == "5":
                    pct = solicitar_flotante("Ingrese el % de impuesto/IVA a aplicar: ")
                    historial_calculos.aplicar_impuesto_a_presupuesto(nuevo_presupuesto, pct)

                elif sub_op == "6":
                    if nuevo_presupuesto["cabeza"] is None:
                        confirmar = input("\n[!] La cotización está vacía (sin ítems). ¿Desea guardarla de todas formas? (s/n): ").strip().lower()
                        if confirmar != 's':
                            print("\nEdición de cotización continuada.")
                            continue

                    historial_calculos.agregar_historial(historial_presupuestos, nuevo_presupuesto)
                    break

                elif sub_op == "7":
                    print("\n[!] Cotización cancelada. Ningún dato fue guardado en el historial.")
                    break

                else:
                    print("\n[X] Opción de submenú no válida. Elija un número entre 1 y 7.")

        # -----------------------------------------------------
        # 6. HISTORIAL DE COTIZACIONES
        # -----------------------------------------------------
        elif opcion == "6":
            if historial_presupuestos["cabeza"] is None:
                print("\n[!] No se ha guardado ninguna cotización en el historial aún.")
                continue

            print("\n¿Cómo deseas recorrer la Lista Doblemente Enlazada del historial?")
            print("1. Recorrido Hacia Adelante (Primeras cotizaciones creadas primero)")
            print("2. Recorrido Hacia Atrás (Últimas cotizaciones creadas primero)")
            sub = input("Seleccione 1 o 2: ").strip()
            
            if sub == "1":
                historial_calculos.recorrer_historial_adelante(historial_presupuestos)
            elif sub == "2":
                historial_calculos.recorrer_historial_atras(historial_presupuestos)
            else:
                print("[X] Opción no válida.")

        # -----------------------------------------------------
        # 7. SALIR
        # -----------------------------------------------------
        elif opcion == "7":
            print("\n========================================================")
            print("     Gracias por utilizar el Cotizador.")
            print("========================================================\n")
            break

        else:
            print("\n[X] Opción no válida. Por favor, seleccione un número del 1 al 7.")

if __name__ == "__main__":
    main()