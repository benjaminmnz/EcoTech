from datetime import date
from getpass import getpass

from dominio.empleado import Empleado
from dominio.cuenta_usuario import CuentaUsuario
from dominio.departamento import Departamento
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo

import psycopg

from repositorio.conexion import obtener_conexion
from dominio.excepciones import ConexionBaseDatosError

from repositorio.departamento_repo import DepartamentoRepositorio
from dominio.excepciones import ErrorPersistencia
from repositorio.empleado_repo import EmpleadoRepositorio
from repositorio.cuenta_usuario_repo import CuentaUsuarioRepositorio
from repositorio.proyecto_repo import ProyectoRepositorio

def iniciar_sesion():
    for numero_intento in range(3):
        usuario = input("Usuario: ").strip()
        contrasena_ingresada = getpass("Contraseña: ")

        try:
            with obtener_conexion() as conexion:
                repositorio = CuentaUsuarioRepositorio(conexion)

                cuenta_encontrada = repositorio.obtener_por_usuario(
                    usuario
                )

                empleado_id = None

                if cuenta_encontrada is not None:
                    if cuenta_encontrada.verificar_contrasena(
                        contrasena_ingresada
                    ):
                        empleado_id = repositorio.obtener_empleado_id(
                            cuenta_encontrada.get_id()
                        )

            if empleado_id is not None:
                print("Inicio de sesión correcto.")
                return cuenta_encontrada, empleado_id

            print("Usuario o contraseña incorrectos.")

        except (
            ConexionBaseDatosError,
            ErrorPersistencia,
            ValueError
        ) as error:
            print("No se pudo iniciar sesión:", error)
            return None

        except psycopg.Error:
            print("No se pudo consultar la cuenta.")
            return None

    print("Se agotaron los tres intentos.")
    return None


# 1. CREAR EL EMPLEADO

empleado = Empleado(
    nombre="Ana Pérez",
    direccion="Los Álamos 123",
    telefono="912345678",
    email="ana@example.com",
    id_empleado=1,
    fecha_inicio_contrato=date(2026, 10, 1),
    salario=800000
)

print("Nombre:", empleado.get_nombre())
print("ID:", empleado.get_id())
print("Salario inicial:", empleado.get_salario())


# 2. PROBAR LOS AUMENTOS DE SALARIO

resultado = empleado.subir_salario(50000)

print("¿Se realizó el aumento?", resultado)
print("Salario actualizado:", empleado.get_salario())

resultado = empleado.subir_salario(-10000)

print("¿Se realizó el aumento negativo?", resultado)
print("Salario después del intento:", empleado.get_salario())


# 3. ACTUALIZAR LOS DATOS DE CONTACTO

empleado.actualizar_datos_contacto(
    direccion="Los Pinos 456",
    telefono="987654321"
)

print("Nueva dirección:", empleado.direccion)
print("Nuevo teléfono:", empleado.telefono)


# 4. CREAR LA CUENTA Y ASIGNARLA AL EMPLEADO

contrasena = getpass("Crea una contraseña de prueba: ")

hash_generado = CuentaUsuario.generar_hash(contrasena)

cuenta = CuentaUsuario(
    id_cuenta=1,
    usuario="ana",
    contrasena_hash=hash_generado,
    rol_acceso="empleado"
)

empleado.asignar_cuenta(cuenta)

print("La cuenta fue asignada al empleado:", empleado.get_nombre())


# 5. PROBAR LA CONTRASEÑA Y LOS PERMISOS

intento = getpass("Ingresa nuevamente la contraseña: ")

print("¿Contraseña correcta?", cuenta.verificar_contrasena(intento))
print(
    "¿Puede acceder a registro de tiempo?",
    cuenta.autorizar("registro_tiempo")
)
print(
    "¿Puede acceder a departamentos?",
    cuenta.autorizar("departamentos")
)


# 6. CREAR EL DEPARTAMENTO Y ASIGNAR AL EMPLEADO

departamento = Departamento(
    id_departamento=1,
    nombre="Desarrollo"
)

departamento.asignar_empleado(empleado)

print("Departamento del empleado:", empleado.departamento.nombre)

for integrante in departamento.listar_empleados():
    print("Empleado del departamento:", integrante.get_nombre())


# 7. ASIGNAR AL GERENTE

departamento.asignar_gerente(empleado)

gerente = departamento.get_gerente()

print("Gerente del departamento:", gerente.get_nombre())


# 8. CREAR LOS PROYECTOS Y ASIGNAR AL EMPLEADO

proyecto_solar = Proyecto(
    id_proyecto=1,
    nombre="Paneles solares",
    descripcion="Instalación de paneles solares",
    fecha_inicio=date(2026, 10, 1)
)

proyecto_reciclaje = Proyecto(
    id_proyecto=2,
    nombre="Reciclaje",
    descripcion="Mejora del proceso de reciclaje",
    fecha_inicio=date(2026, 10, 15)
)

proyecto_solar.asignar_empleado(empleado)
proyecto_reciclaje.asignar_empleado(empleado)

for proyecto in [proyecto_solar, proyecto_reciclaje]:
    print("Proyecto:", proyecto.nombre)

    for integrante in proyecto.listar_empleados():
        print("Empleado asignado:", integrante.get_nombre())


# 9. CREAR EL REGISTRO DE TIEMPO

registro = proyecto_solar.registrar_tiempo(
    empleado=empleado,
    id_registro=1,
    fecha=date(2026, 10, 22),
    horas=4.5,
    descripcion="Instalación de paneles solares"
)

print("ID del registro:", registro.get_id())
print("Horas registradas:", registro.get_horas_trabajadas())


# 10. PROBAR EL RECHAZO DE HORAS INVÁLIDAS

try:
    registro.registrar(-2)
except ValueError as error:
    print("Registro rechazado:", error)

print(
    "Horas después del intento inválido:",
    registro.get_horas_trabajadas()
)


# 11. ASOCIAR EL REGISTRO: PRIMERO AL EMPLEADO Y DESPUÉS AL PROYECTO


print("El registro pertenece a:", registro.empleado.get_nombre())
print("Proyecto del registro:", registro.proyecto.nombre)


# 12. CONSULTAR LOS REGISTROS DEL EMPLEADO Y EL TOTAL DEL PROYECTO

for entrada in empleado.listar_registros():
    print("Horas del empleado:", entrada.get_horas_trabajadas())

print("Proyecto:", proyecto_solar.nombre)
print("Horas totales:", proyecto_solar.calcular_horas_totales())

try:
    with obtener_conexion() as conexion:
        repositorio = DepartamentoRepositorio(conexion)

        # Crear.
        nuevo = repositorio.crear("Prueba CRUD")
        id_prueba = nuevo.get_id()
        print("CREAR:", id_prueba, nuevo.nombre)

        # Consultar.
        encontrado = repositorio.obtener_por_id(id_prueba)

        if encontrado is None:
            raise ValueError("No se recuperó el departamento creado")

        print("CONSULTAR:", encontrado.nombre)

        # Actualizar.
        actualizado = repositorio.actualizar(
            id_prueba,
            "Prueba actualizada"
        )
        print("ACTUALIZAR:", actualizado.nombre)

        # Listar.
        departamentos = repositorio.listar()
        print("LISTAR: cantidad =", len(departamentos))

        # Eliminar únicamente el departamento de esta prueba.
        eliminado = repositorio.eliminar(id_prueba)
        print("ELIMINAR:", eliminado)

        # Comprobar que ya no existe.
        comprobacion = repositorio.obtener_por_id(id_prueba)
        print("CONSULTA DESPUÉS DE ELIMINAR:", comprobacion)

    print("Prueba CRUD confirmada correctamente.")

except (ConexionBaseDatosError, ErrorPersistencia, ValueError) as error:
    print("Error:", error)

except psycopg.Error:
    print("No se pudo completar o confirmar la transacción.")

try:
    with obtener_conexion() as conexion:
        departamentos_repo = DepartamentoRepositorio(conexion)
        empleados_repo = EmpleadoRepositorio(conexion)

        # Crear un departamento exclusivo para esta prueba.
        departamento_prueba = departamentos_repo.crear(
            "Departamento de prueba de empleados"
        )

        # Guardar los datos del empleado.
        guardado = empleados_repo.crear(
            empleado,
            departamento_prueba.get_id()
        )

        id_prueba = guardado.get_id()

        print("CREAR EMPLEADO:", id_prueba, guardado.get_nombre())

        # Recuperar el empleado.
        encontrado = empleados_repo.obtener_por_id(id_prueba)

        if encontrado is None:
            raise ValueError("No se recuperó el empleado creado")

        print("CONSULTAR EMPLEADO:", encontrado.get_nombre())
        print("DEPARTAMENTO:", encontrado.departamento.nombre)

        # Modificar y guardar el contacto.
        encontrado.actualizar_datos_contacto(
            "Dirección de prueba 123",
            "911111111"
        )

        actualizado = empleados_repo.actualizar(
            encontrado,
            departamento_prueba.get_id()
        )

        print("ACTUALIZAR EMPLEADO:", actualizado.direccion)

        # Listar.
        empleados_bd = empleados_repo.listar()
        print("LISTAR EMPLEADOS: cantidad =", len(empleados_bd))

        # Eliminar únicamente los datos creados en esta prueba.
        eliminado = empleados_repo.eliminar(id_prueba)
        print("ELIMINAR EMPLEADO:", eliminado)

        comprobacion = empleados_repo.obtener_por_id(id_prueba)
        print("CONSULTA DESPUÉS DE ELIMINAR:", comprobacion)

        departamentos_repo.eliminar(departamento_prueba.get_id())

    print("Prueba CRUD de empleados confirmada.")

except (ConexionBaseDatosError, ErrorPersistencia, ValueError) as error:
    print("Error:", error)

except psycopg.Error:
    print("No se pudo completar o confirmar la transacción.")

try:
    with obtener_conexion() as conexion:
        repositorio = DepartamentoRepositorio(conexion)

        control = repositorio.crear("Control de prueba SQL")

        payload = "' OR '1'='1"
        departamento_payload = repositorio.crear(payload)

        resultados = repositorio.buscar_por_nombre(payload)

        encontro_payload = False

        for resultado in resultados:
            if resultado.nombre != payload:
                raise ValueError(
                    "La búsqueda devolvió un departamento que no corresponde"
                )

            if resultado.get_id() == departamento_payload.get_id():
                encontro_payload = True

        if not encontro_payload:
            raise ValueError("No se recuperó el texto de prueba")

        # Eliminar solamente las dos filas creadas por esta prueba.
        repositorio.eliminar(departamento_payload.get_id())
        repositorio.eliminar(control.get_id())

    print("PRUEBA SQL: superada.")
    print("El payload se trató como texto.")
    print("La búsqueda no devolvió departamentos con otros nombres.")

except (ConexionBaseDatosError, ErrorPersistencia, ValueError) as error:
    print("Prueba SQL fallida:", error)

except psycopg.Error:
    print("No se pudo completar la prueba SQL.")

id_departamento_prueba = None
fallo_esperado = False

try:
    with obtener_conexion() as conexion:
        departamentos_repo = DepartamentoRepositorio(conexion)
        empleados_repo = EmpleadoRepositorio(conexion)

        # Primera escritura: crear un departamento.
        departamento_prueba = departamentos_repo.crear(
            "Departamento temporal para rollback"
        )

        id_departamento_prueba = departamento_prueba.get_id()

        # Buscar un identificador de departamento que no exista.
        id_inexistente = id_departamento_prueba + 1

        while departamentos_repo.obtener_por_id(id_inexistente) is not None:
            id_inexistente += 1

        print("Departamento insertado, todavía sin confirmar.")

        # Segunda escritura: intentar guardar un empleado
        # asociado a un departamento inexistente.
        empleados_repo.crear(
            empleado,
            id_inexistente
        )

        # Si inesperadamente funcionara, también deshacemos la prueba.
        raise ValueError(
            "No ocurrió el fallo esperado; se cancela la prueba"
        )

except ErrorPersistencia as error:
    fallo_esperado = isinstance(
        error.__cause__,
        psycopg.errors.ForeignKeyViolation
    )
    print("Operación rechazada:", error)

except (ConexionBaseDatosError, ValueError) as error:
    print("No se completó la prueba:", error)

except psycopg.Error:
    print("La prueba tuvo un problema de conexión o transacción.")


# Comprobar desde una conexión nueva que la primera escritura se deshizo.
if fallo_esperado and id_departamento_prueba is not None:
    try:
        with obtener_conexion() as conexion:
            repositorio = DepartamentoRepositorio(conexion)

            comprobacion = repositorio.obtener_por_id(
                id_departamento_prueba
            )

        if comprobacion is None:
            print("ROLLBACK: superado.")
            print("El departamento temporal no quedó guardado.")
        else:
            print("ROLLBACK: fallido. El departamento sigue guardado.")

    except (ConexionBaseDatosError, ErrorPersistencia, ValueError) as error:
        print("No se pudo verificar el rollback:", error)

    except psycopg.Error:
        print("Falló la consulta de verificación.")

try:
    with obtener_conexion() as conexion:
        departamentos_repo = DepartamentoRepositorio(conexion)
        empleados_repo = EmpleadoRepositorio(conexion)
        cuentas_repo = CuentaUsuarioRepositorio(conexion)

        departamento_prueba = departamentos_repo.crear(
            "Departamento de prueba de cuentas"
        )

        empleado_guardado = empleados_repo.crear(
            empleado,
            departamento_prueba.get_id()
        )

        # Usamos el ID generado para obtener un usuario de prueba distinto.
        usuario_prueba = "prueba_" + str(empleado_guardado.get_id())

        cuenta_prueba = CuentaUsuario(
            id_cuenta=1,
            usuario=usuario_prueba,
            contrasena_hash=cuenta.get_contrasena_hash(),
            rol_acceso="empleado"
        )

        cuenta_guardada = cuentas_repo.crear(
            cuenta_prueba,
            empleado_guardado.get_id()
        )

    print("Empleado y cuenta guardados en la misma transacción.")

    # Recuperar desde una conexión nueva.
    with obtener_conexion() as conexion:
        cuentas_repo = CuentaUsuarioRepositorio(conexion)

        recuperada = cuentas_repo.obtener_por_usuario(
            cuenta_guardada.usuario
        )

        if recuperada is None:
            raise ValueError("No se recuperó la cuenta guardada")

        empleado_id = cuentas_repo.obtener_empleado_id(
            recuperada.get_id()
        )

    print("Usuario recuperado:", recuperada.usuario)
    print("Empleado asociado:", empleado_id)
    print(
        "¿Verifica la contraseña original?",
        recuperada.verificar_contrasena(contrasena)
    )

except (ConexionBaseDatosError, ErrorPersistencia, ValueError) as error:
    print("Error:", error)

except psycopg.Error:
    print("No se pudo completar la operación en la base de datos.")

print("\nPRUEBA DE INICIO DE SESIÓN")

sesion = iniciar_sesion()

if sesion is not None:
    cuenta_activa, empleado_activo_id = sesion

    print("Usuario conectado:", cuenta_activa.usuario)
    print("Rol:", cuenta_activa.get_rol_acceso())
    print("ID del empleado:", empleado_activo_id)
else:
    print("No se inició una sesión.")

try:
    with obtener_conexion() as conexion:
        departamentos_repo = DepartamentoRepositorio(conexion)
        empleados_repo = EmpleadoRepositorio(conexion)
        proyectos_repo = ProyectoRepositorio(conexion)

        departamento_prueba = departamentos_repo.crear(
            "Departamento de prueba de proyectos"
        )

        empleado_prueba = empleados_repo.crear(
            empleado,
            departamento_prueba.get_id()
        )

        proyecto_guardado = proyectos_repo.crear(proyecto_solar)

        print("PROYECTO CREADO:", proyecto_guardado.nombre)

        encontrado = proyectos_repo.obtener_por_id(
            proyecto_guardado.get_id()
        )

        if encontrado is None:
            raise ValueError("No se recuperó el proyecto")

        print("PROYECTO CONSULTADO:", encontrado.nombre)

        encontrado.nombre = "Proyecto actualizado de prueba"
        actualizado = proyectos_repo.actualizar(encontrado)

        print("PROYECTO ACTUALIZADO:", actualizado.nombre)

        proyectos_repo.asignar_empleado(
            proyecto_guardado.get_id(),
            empleado_prueba.get_id()
        )

        ids_asignados = proyectos_repo.listar_ids_empleados(
            proyecto_guardado.get_id()
        )

        if empleado_prueba.get_id() not in ids_asignados:
            raise ValueError("La asignación no se guardó")

        print("ASIGNACIÓN: correcta")
        print("PROYECTOS GUARDADOS:", len(proyectos_repo.listar()))

        # Limpiar únicamente los datos creados por esta prueba.
        proyectos_repo.quitar_empleado(
            proyecto_guardado.get_id(),
            empleado_prueba.get_id()
        )

        eliminado = proyectos_repo.eliminar(
            proyecto_guardado.get_id()
        )

        print("PROYECTO ELIMINADO:", eliminado)

        empleados_repo.eliminar(empleado_prueba.get_id())
        departamentos_repo.eliminar(departamento_prueba.get_id())

    print("Prueba de proyectos confirmada.")

except (ConexionBaseDatosError, ErrorPersistencia, ValueError) as error:
    print("Error:", error)

except psycopg.Error:
    print("No se pudo completar o confirmar la prueba.")