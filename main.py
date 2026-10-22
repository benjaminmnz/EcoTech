from datetime import date
from dominio.empleado import Empleado
from dominio.cuenta_usuario import CuentaUsuario
from dominio.departamento import Departamento
from dominio.proyecto import Proyecto
from dominio.registro_tiempo import RegistroTiempo

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

resultado = empleado.subir_salario(50000)

print("¿Se realizó el aumento?", resultado)
print("Salario actualizado:", empleado.get_salario())

resultado = empleado.subir_salario(-10000)

print("¿Se realizó el aumento negativo?", resultado)
print("Salario después del intento:", empleado.get_salario())

empleado.actualizar_datos_contacto(
    direccion="Los Pinos 456",
    telefono="987654321"
)

print("Nueva dirección:", empleado.direccion)
print("Nuevo teléfono:", empleado.telefono)

from getpass import getpass


contrasena = getpass("Crea una contraseña de prueba: ")

hash_generado = CuentaUsuario.generar_hash(contrasena)

cuenta = CuentaUsuario(
    id_cuenta=1,
    usuario="ana",
    contrasena_hash=hash_generado,
    rol_acceso="empleado"
)

intento = getpass("Ingresa nuevamente la contraseña: ")

print("¿Contraseña correcta?", cuenta.verificar_contrasena(intento))
print("¿Puede acceder a registro de tiempo?", cuenta.autorizar("registro_tiempo"))
print("¿Puede acceder a departamentos?", cuenta.autorizar("departamentos"))

cuenta = CuentaUsuario(
    id_cuenta=1,
    usuario="ana",
    contrasena_hash=hash_generado,
    rol_acceso="empleado"
)

empleado.asignar_cuenta(cuenta)

print("La cuenta fue asignada al empleado:", empleado.get_nombre())

departamento = Departamento(
    id_departamento=1,
    nombre="Desarrollo"
)

departamento.asignar_empleado(empleado)

print("Departamento del empleado:", empleado.departamento.nombre)

for integrante in departamento.listar_empleados():
    print("Empleado del departamento:", integrante.get_nombre())


departamento.asignar_gerente(empleado)

gerente = departamento.get_gerente()

print("Gerente del departamento:", gerente.get_nombre())

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

registro = RegistroTiempo(
    id_registro=1,
    fecha=date(2026, 10, 22),
    horas_trabajadas=4.5,
    descripcion_tarea="Instalación de paneles solares"
)

print("ID del registro:", registro.get_id())
print("Horas registradas:", registro.get_horas_trabajadas())

try:
    registro.registrar(-2)
except ValueError as error:
    print("Registro rechazado:", error)

print("Horas después del intento inválido:", registro.get_horas_trabajadas())

proyecto_solar.agregar_registro(registro)

print("Proyecto:", proyecto_solar.nombre)
print("Horas totales:", proyecto_solar.calcular_horas_totales())

empleado.agregar_registro(registro)

print("El registro pertenece a:", registro.empleado.get_nombre())

for entrada in empleado.listar_registros():
    print("Horas del empleado:", entrada.get_horas_trabajadas())

print("hola")