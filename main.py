"""Aplicación por consola de EcoTech. Ejecutar desde la carpeta del proyecto."""
import argparse
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from getpass import getpass
from pathlib import Path
from uuid import uuid4

import psycopg

from dominio.empleado import Empleado
from dominio.proyecto import Proyecto
from dominio.excepciones import EcoTechError
from repositorio.conexion import obtener_conexion
from repositorio.sistema_repo import SistemaRepositorio
from servicios import GestionEcoTech, autenticar, necesita_administrador, crear_administrador_inicial


def leer_texto(mensaje, predeterminado=None):
    while True:
        valor = input(mensaje).strip()
        if valor:
            return valor
        if predeterminado is not None:
            return predeterminado
        print("Debes ingresar un valor.")


def leer_id(mensaje, predeterminado=None, permitir_cero=False):
    while True:
        valor = input(mensaje).strip()
        if not valor and predeterminado is not None:
            return predeterminado
        try:
            numero = int(valor)
            if numero > 0 or (permitir_cero and numero == 0):
                return numero
        except ValueError:
            numero = None
        print("Ingresa un identificador entero válido.")


def leer_decimal(mensaje, predeterminado=None):
    while True:
        valor = input(mensaje).strip()
        if not valor and predeterminado is not None:
            return predeterminado
        try:
            numero = Decimal(valor.replace(",", "."))
            if numero.is_finite() and numero > 0 and numero <= Decimal("9999999999.99"):
                if numero == numero.quantize(Decimal("0.01")):
                    return numero
        except (InvalidOperation, ValueError):
            numero = None
        print("Ingresa un número positivo con hasta dos decimales, sin separadores de miles.")


def leer_fecha(mensaje, predeterminado=None):
    while True:
        valor = input(mensaje).strip()
        if not valor and predeterminado is not None:
            return predeterminado
        try:
            return date.fromisoformat(valor)
        except ValueError:
            print("Usa una fecha válida con formato AAAA-MM-DD.")


def confirmar(mensaje):
    while True:
        valor = input(mensaje + " [s/n]: ").strip().lower()
        if valor in ("s", "si", "sí"):
            return True
        if valor in ("n", "no"):
            return False
        print("Responde s o n.")


def leer_clave():
    while True:
        clave = getpass("Contraseña nueva (mínimo 8 caracteres): ")
        if len(clave) < 8 or len(clave) > 1024:
            print("La contraseña debe tener entre 8 y 1024 caracteres.")
        elif clave != getpass("Repite la contraseña: "):
            print("Las contraseñas no coinciden.")
        else:
            return clave


def leer_rol():
    while True:
        opcion = input("Rol [1] empleado / [2] administrador: ").strip()
        if opcion in ("1", "2"):
            return "empleado" if opcion == "1" else "administrador"
        print("Selecciona 1 o 2.")


def intentar(operacion):
    try:
        operacion()
    except (EcoTechError, ValueError, OSError) as error:
        print("Operación rechazada:", error)
    except psycopg.IntegrityError:
        print("La operación se deshizo: hay datos duplicados o relaciones que deben conservarse.")
    except psycopg.Error:
        print("La operación no se confirmó. Revisa la conexión e intenta nuevamente.")


def pedir_empleado(actual=None):
    aviso = " [Enter conserva el valor]" if actual else ""
    nombre = leer_texto("Nombre" + aviso + ": ", actual.nombre if actual else None)
    direccion = leer_texto("Dirección" + aviso + ": ", actual.direccion if actual else None)
    telefono = leer_texto("Teléfono" + aviso + ": ", actual.telefono if actual else None)
    email = leer_texto("Correo" + aviso + ": ", actual.email if actual else None)
    fecha = leer_fecha("Inicio de contrato AAAA-MM-DD" + aviso + ": ",
                       actual.fecha_inicio_contrato if actual else None)
    salario = leer_decimal("Salario" + aviso + ": ", actual.get_salario() if actual else None)
    return Empleado(nombre, direccion, telefono, email,
                    actual.get_id() if actual else 0, fecha, salario)


def mostrar_departamentos(gestion):
    print("\nID | Departamento | Gerente | Empleados")
    for d in gestion.departamentos():
        gerente = d.get_gerente()
        print(d.get_id(), d.nombre, gerente.get_nombre() if gerente else "Sin asignar",
              len(d.listar_empleados()), sep=" | ")


def mostrar_empleados(gestion):
    print("\nID | Nombre | Correo | Departamento | Salario")
    for e in gestion.empleados():
        print(e.get_id(), e.get_nombre(), e.email, e.departamento.nombre,
              format(e.get_salario(), ".2f"), sep=" | ")


def mostrar_proyectos(gestion):
    print("\nID | Proyecto | Descripción | Inicio")
    for p in gestion.proyectos():
        print(p.get_id(), p.nombre, p.descripcion, p.fecha_inicio, sep=" | ")


def mostrar_registros(gestion):
    print("\nID | Fecha | Empleado | Proyecto | Horas | Tarea")
    for r in gestion.registros():
        print(r.get_id(), r.fecha, r.empleado.get_nombre(), r.proyecto.nombre,
              r.get_horas_trabajadas(), r.descripcion_tarea, sep=" | ")


def menu_departamentos(gestion):
    while True:
        print("\nDEPARTAMENTOS: 1 Listar / 2 Crear / 3 Renombrar / 4 Eliminar / 5 Gerente / 0 Volver")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            return
        def accion():
            if opcion == "1":
                mostrar_departamentos(gestion)
            elif opcion == "2":
                nuevo = gestion.crear_departamento(leer_texto("Nombre: "))
                print("Departamento creado. ID:", nuevo.get_id())
            elif opcion == "3":
                gestion.renombrar_departamento(leer_id("ID del departamento: "), leer_texto("Nombre nuevo: "))
                print("Nombre actualizado.")
            elif opcion == "4":
                identificador = leer_id("ID del departamento: ")
                if confirmar("¿Eliminar el departamento? Debe estar sin empleados"):
                    gestion.eliminar_departamento(identificador)
                    print("Departamento eliminado.")
            elif opcion == "5":
                departamento_id = leer_id("ID del departamento: ")
                empleado_id = leer_id("ID del gerente (0 para quitarlo): ", permitir_cero=True)
                gestion.asignar_gerente(departamento_id, empleado_id or None)
                print("Gerente actualizado.")
            else:
                print("Opción inválida.")
        intentar(accion)


def menu_empleados(gestion):
    while True:
        print("\nEMPLEADOS: 1 Listar / 2 Crear / 3 Actualizar / 4 Eliminar / 5 Crear cuenta / 0 Volver")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            return
        def accion():
            if opcion == "1":
                mostrar_empleados(gestion)
            elif opcion == "2":
                mostrar_departamentos(gestion)
                departamento_id = leer_id("ID del departamento: ")
                empleado = pedir_empleado()
                usuario = clave = None
                rol = "empleado"
                if confirmar("¿Crear también su cuenta de acceso?"):
                    usuario = leer_texto("Usuario: ")
                    clave = leer_clave()
                    rol = leer_rol()
                guardado = gestion.crear_empleado(empleado, departamento_id, usuario, clave, rol)
                print("Empleado guardado. ID:", guardado.get_id())
            elif opcion == "3":
                actual = gestion.obtener_empleado(leer_id("ID del empleado: "))
                actualizado = pedir_empleado(actual)
                departamento_id = leer_id("ID del departamento [Enter conserva]: ", actual.departamento.get_id())
                gestion.actualizar_empleado(actualizado, departamento_id)
                print("Empleado actualizado. Si era gerente, quita su designación antes de trasladarlo.")
            elif opcion == "4":
                identificador = leer_id("ID del empleado: ")
                if confirmar("¿Eliminar empleado, cuenta y registros de tiempo asociados?"):
                    gestion.eliminar_empleado(identificador)
                    print("Empleado y datos dependientes eliminados.")
            elif opcion == "5":
                identificador = leer_id("ID del empleado: ")
                usuario = leer_texto("Usuario: ")
                clave = leer_clave()
                cuenta = gestion.crear_cuenta(identificador, usuario, clave, leer_rol())
                print("Cuenta creada:", cuenta.usuario)
            else:
                print("Opción inválida.")
        intentar(accion)


def menu_proyectos(gestion):
    while True:
        print("\nPROYECTOS: 1 Listar / 2 Crear / 3 Actualizar / 4 Eliminar / 5 Asignar empleado / 6 Quitar empleado / 0 Volver")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            return
        def accion():
            if opcion == "1":
                mostrar_proyectos(gestion)
            elif opcion == "2":
                nombre = leer_texto("Nombre: ")
                descripcion = leer_texto("Descripción: ")
                fecha = leer_fecha("Inicio AAAA-MM-DD: ")
                nuevo = gestion.crear_proyecto(Proyecto(0, nombre, descripcion, fecha))
                print("Proyecto creado. ID:", nuevo.get_id())
            elif opcion == "3":
                identificador = leer_id("ID del proyecto: ")
                actual = next((p for p in gestion.proyectos() if p.get_id() == identificador), None)
                if actual is None:
                    raise ValueError("El proyecto no existe")
                nombre = leer_texto("Nombre [Enter conserva]: ", actual.nombre)
                descripcion = leer_texto("Descripción [Enter conserva]: ", actual.descripcion)
                fecha = leer_fecha("Inicio [Enter conserva]: ", actual.fecha_inicio)
                gestion.actualizar_proyecto(Proyecto(identificador, nombre, descripcion, fecha))
                print("Proyecto actualizado.")
            elif opcion == "4":
                identificador = leer_id("ID del proyecto: ")
                if confirmar("¿Eliminar proyecto? No debe conservar registros de tiempo"):
                    gestion.eliminar_proyecto(identificador)
                    print("Proyecto eliminado.")
            elif opcion in ("5", "6"):
                proyecto_id = leer_id("ID del proyecto: ")
                empleado_id = leer_id("ID del empleado: ")
                gestion.asignar_proyecto(proyecto_id, empleado_id, quitar=opcion == "6")
                print("Asignación actualizada.")
            else:
                print("Opción inválida.")
        intentar(accion)


def menu_registros(gestion):
    while True:
        print("\nHORAS: 1 Listar / 2 Registrar / 3 Corregir / 4 Eliminar / 0 Volver")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            return
        def accion():
            if opcion == "1":
                mostrar_registros(gestion)
            elif opcion == "2":
                cuenta = gestion.cuenta_actual()
                empleado_id = gestion.sesion.empleado_id
                if cuenta.get_rol_acceso() == "administrador":
                    empleado_id = leer_id("ID del empleado: ")
                mostrar_proyectos(gestion)
                proyecto_id = leer_id("ID del proyecto: ")
                fecha = leer_fecha("Fecha AAAA-MM-DD: ")
                horas = leer_decimal("Horas (mayor que 0 y máximo 24): ")
                descripcion = leer_texto("Tarea: ")
                registro = gestion.crear_registro(empleado_id, proyecto_id, fecha, horas, descripcion)
                print("Registro guardado. ID:", registro.get_id())
            elif opcion == "3":
                identificador = leer_id("ID del registro: ")
                actual = next((r for r in gestion.registros() if r.get_id() == identificador), None)
                if actual is None:
                    raise ValueError("El registro no existe o no pertenece a tu cuenta")
                fecha = leer_fecha("Fecha [Enter conserva]: ", actual.fecha)
                horas = leer_decimal("Horas [Enter conserva]: ", actual.get_horas_trabajadas())
                descripcion = leer_texto("Tarea [Enter conserva]: ", actual.descripcion_tarea)
                gestion.actualizar_registro(identificador, fecha, horas, descripcion)
                print("Registro actualizado.")
            elif opcion == "4":
                identificador = leer_id("ID del registro: ")
                if confirmar("¿Eliminar el registro?"):
                    gestion.eliminar_registro(identificador)
                    print("Registro eliminado.")
            else:
                print("Opción inválida.")
        intentar(accion)


def generar_informes(gestion):
    from dominio.informe_pdf import InformePDF
    from dominio.informe_excel import InformeExcel
    departamentos, empleados, proyectos, registros = gestion.datos_informes()
    opcion = input("Formato: 1 PDF / 2 Excel / 3 Ambos: ").strip()
    if opcion not in ("1", "2", "3"):
        raise ValueError("Selecciona 1, 2 o 3")
    carpeta = Path(__file__).resolve().parent / "reportes"
    marca = datetime.now().strftime("%Y%m%d_%H%M%S") + "_" + uuid4().hex[:8]
    informes = []
    if opcion in ("1", "3"):
        informes.append(InformePDF(1, empleados, proyectos, registros, carpeta / ("ecotech_" + marca + ".pdf")))
    if opcion in ("2", "3"):
        informes.append(InformeExcel(2, empleados, proyectos, registros, carpeta / ("ecotech_" + marca + ".xlsx")))
    # Colección mixta: cada objeto ejecuta su propio generar(), sin inspeccionar su tipo.
    for informe in informes:
        informe.generar()
        print("Informe generado:", informe.ruta_archivo)


def configurar_administrador():
    print("\nPRIMER ADMINISTRADOR")
    print("No existe una cuenta administradora. Completa el registro inicial.")
    if not confirmar("¿Crear el administrador inicial?"):
        return False
    nombre_departamento = leer_texto("Nombre del departamento inicial: ")
    empleado = pedir_empleado()
    usuario = leer_texto("Usuario administrador: ")
    clave = leer_clave()
    crear_administrador_inicial(empleado, nombre_departamento, usuario, clave)
    print("Administrador creado. Ya puedes iniciar sesión.")
    return True


def iniciar_sesion():
    for _ in range(3):
        usuario = leer_texto("Usuario: ")
        clave = getpass("Contraseña: ")
        sesion = autenticar(usuario, clave)
        if sesion is not None:
            return sesion
        print("Usuario o contraseña incorrectos.")
    print("Se agotaron los intentos de esta sesión.")
    return None


def menu_principal(gestion):
    while True:
        cuenta = gestion.cuenta_actual()
        administrador = cuenta.get_rol_acceso() == "administrador"
        print("\nEcoTech |", cuenta.usuario, "|", cuenta.get_rol_acceso())
        if administrador:
            print("1 Departamentos / 2 Empleados / 3 Proyectos / 4 Horas / 5 Informes / 6 Contraseña / 0 Salir")
        else:
            print("3 Mis proyectos / 4 Mis horas / 6 Contraseña / 0 Salir")
        opcion = input("Opción: ").strip()
        if opcion == "0":
            return
        def accion():
            if opcion == "1" and administrador:
                menu_departamentos(gestion)
            elif opcion == "2" and administrador:
                menu_empleados(gestion)
            elif opcion == "3":
                menu_proyectos(gestion) if administrador else mostrar_proyectos(gestion)
            elif opcion == "4":
                menu_registros(gestion)
            elif opcion == "5" and administrador:
                generar_informes(gestion)
            elif opcion == "6":
                actual = getpass("Contraseña actual: ")
                nueva = leer_clave()
                gestion.cambiar_contrasena(actual, nueva)
                print("Contraseña actualizada.")
            else:
                print("Opción inválida o no autorizada.")
        intentar(accion)


def main():
    parser = argparse.ArgumentParser(description="Sistema EcoTech por consola")
    grupo = parser.add_mutually_exclusive_group()
    grupo.add_argument("--inicializar", action="store_true", help="Crear el esquema en una base nueva")
    grupo.add_argument("--verificar", action="store_true", help="Pruebas locales y de BD con rollback")
    grupo.add_argument("--verificar-local", action="store_true", help="Pruebas sin conexión a BD")
    args = parser.parse_args()
    try:
        if args.verificar or args.verificar_local:
            from verificaciones import ejecutar_verificaciones
            return ejecutar_verificaciones(solo_local=args.verificar_local)
        with obtener_conexion() as conexion:
            sistema = SistemaRepositorio(conexion)
            if args.inicializar:
                creado = sistema.inicializar()
                print("Esquema creado." if creado else "El esquema ya existe y está disponible.")
                return 0
            sistema.comprobar_esquema()
        if necesita_administrador() and not configurar_administrador():
            return 0
        sesion = iniciar_sesion()
        if sesion is None:
            return 0
        menu_principal(GestionEcoTech(sesion))
        return 0
    except (EOFError, KeyboardInterrupt):
        print("\nSesión finalizada.")
        return 0
    except (EcoTechError, ValueError, OSError) as error:
        print("No se pudo continuar:", error)
        return 1
    except psycopg.Error:
        print("No se pudo completar la operación de base de datos. Revisa la conexión.")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
