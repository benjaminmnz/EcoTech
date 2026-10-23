"""Operaciones de aplicación. El SQL permanece en repositorio/."""
from dataclasses import dataclass
from dominio.cuenta_usuario import CuentaUsuario
from dominio.empleado import Empleado
from dominio.excepciones import AutorizacionError, EntidadNoEncontradaError
from repositorio.conexion import obtener_conexion
from repositorio.departamento_repo import DepartamentoRepositorio
from repositorio.empleado_repo import EmpleadoRepositorio
from repositorio.proyecto_repo import ProyectoRepositorio
from repositorio.cuenta_usuario_repo import CuentaUsuarioRepositorio
from repositorio.registro_tiempo_repo import RegistroTiempoRepositorio
from repositorio.sistema_repo import SistemaRepositorio


@dataclass(frozen=True)
class Sesion:
    cuenta_id: int
    empleado_id: int


def autenticar(usuario, contrasena):
    with obtener_conexion() as conexion:
        repo = CuentaUsuarioRepositorio(conexion)
        cuenta = repo.obtener_por_usuario(usuario)
        if cuenta is None or not cuenta.verificar_contrasena(contrasena):
            return None
        empleado_id = repo.obtener_empleado_id(cuenta.get_id())
        if empleado_id is None:
            return None
        return Sesion(cuenta.get_id(), empleado_id)


def necesita_administrador():
    with obtener_conexion() as conexion:
        return not SistemaRepositorio(conexion).hay_administrador()


def crear_administrador_inicial(empleado, nombre_departamento, usuario, contrasena):
    cuenta = CuentaUsuario(0, usuario, CuentaUsuario.generar_hash(contrasena), "administrador")
    with obtener_conexion() as conexion:
        sistema = SistemaRepositorio(conexion)
        sistema.bloquear_configuracion()
        if sistema.hay_administrador():
            raise AutorizacionError("Ya existe un administrador; inicia sesión")
        departamento = DepartamentoRepositorio(conexion).crear(nombre_departamento)
        guardado = EmpleadoRepositorio(conexion).crear(empleado, departamento.get_id())
        cuenta = CuentaUsuarioRepositorio(conexion).crear(cuenta, guardado.get_id())
        return Sesion(cuenta.get_id(), guardado.get_id())


class GestionEcoTech:
    def __init__(self, sesion):
        if not isinstance(sesion, Sesion):
            raise AutorizacionError("Debes iniciar sesión")
        self.sesion = sesion

    def _cuenta(self, conexion):
        repo = CuentaUsuarioRepositorio(conexion)
        cuenta = repo.obtener_por_empleado(self.sesion.empleado_id)
        if cuenta is None or cuenta.get_id() != self.sesion.cuenta_id:
            raise AutorizacionError("La sesión ya no es válida")
        return cuenta

    def _operar(self, modulo, operacion):
        with obtener_conexion() as conexion:
            cuenta = self._cuenta(conexion)
            if not cuenta.autorizar(modulo):
                raise AutorizacionError("Tu cuenta no tiene permiso para esta operación")
            return operacion(conexion)

    def cuenta_actual(self):
        with obtener_conexion() as conexion:
            return self._cuenta(conexion)

    def departamentos(self):
        return self._operar("departamentos", lambda c: SistemaRepositorio(c).cargar_dominio()[0])

    def crear_departamento(self, nombre):
        return self._operar("departamentos", lambda c: DepartamentoRepositorio(c).crear(nombre))

    def renombrar_departamento(self, identificador, nombre):
        return self._operar("departamentos", lambda c: DepartamentoRepositorio(c).actualizar(identificador, nombre))

    def eliminar_departamento(self, identificador):
        resultado = self._operar("departamentos", lambda c: DepartamentoRepositorio(c).eliminar(identificador))
        if not resultado:
            raise EntidadNoEncontradaError("El departamento no existe")

    def asignar_gerente(self, departamento_id, empleado_id):
        return self._operar("departamentos", lambda c: DepartamentoRepositorio(c).asignar_gerente(departamento_id, empleado_id))

    def empleados(self):
        return self._operar("empleados", lambda c: EmpleadoRepositorio(c).listar())

    def obtener_empleado(self, identificador):
        empleado = self._operar("empleados", lambda c: EmpleadoRepositorio(c).obtener_por_id(identificador))
        if empleado is None:
            raise EntidadNoEncontradaError("El empleado no existe")
        return empleado

    def crear_empleado(self, empleado, departamento_id, usuario=None, contrasena=None, rol="empleado"):
        cuenta = None
        if usuario is not None:
            cuenta = CuentaUsuario(0, usuario, CuentaUsuario.generar_hash(contrasena), rol)
        def guardar(conexion):
            nuevo = EmpleadoRepositorio(conexion).crear(empleado, departamento_id)
            if cuenta is not None:
                guardada = CuentaUsuarioRepositorio(conexion).crear(cuenta, nuevo.get_id())
                nuevo.asignar_cuenta(guardada)
            return nuevo
        return self._operar("empleados", guardar)

    def actualizar_empleado(self, empleado, departamento_id):
        return self._operar("empleados", lambda c: EmpleadoRepositorio(c).actualizar(empleado, departamento_id))

    def eliminar_empleado(self, identificador):
        if identificador == self.sesion.empleado_id:
            raise AutorizacionError("No puedes eliminar tu propia cuenta mientras la usas")
        resultado = self._operar("empleados", lambda c: EmpleadoRepositorio(c).eliminar(identificador))
        if not resultado:
            raise EntidadNoEncontradaError("El empleado no existe")

    def crear_cuenta(self, empleado_id, usuario, contrasena, rol):
        cuenta = CuentaUsuario(0, usuario, CuentaUsuario.generar_hash(contrasena), rol)
        return self._operar("empleados", lambda c: CuentaUsuarioRepositorio(c).crear(cuenta, empleado_id))

    def proyectos(self):
        # El empleado regular solo ve proyectos a los que está asignado.
        with obtener_conexion() as conexion:
            cuenta = self._cuenta(conexion)
            repo = ProyectoRepositorio(conexion)
            if cuenta.get_rol_acceso() == "administrador":
                return SistemaRepositorio(conexion).cargar_dominio()[2]
            return repo.listar_por_empleado(self.sesion.empleado_id)

    def crear_proyecto(self, proyecto):
        return self._operar("proyectos", lambda c: ProyectoRepositorio(c).crear(proyecto))

    def actualizar_proyecto(self, proyecto):
        return self._operar("proyectos", lambda c: ProyectoRepositorio(c).actualizar(proyecto))

    def eliminar_proyecto(self, identificador):
        resultado = self._operar("proyectos", lambda c: ProyectoRepositorio(c).eliminar(identificador))
        if not resultado:
            raise EntidadNoEncontradaError("El proyecto no existe")

    def asignar_proyecto(self, proyecto_id, empleado_id, quitar=False):
        def operar(conexion):
            repo = ProyectoRepositorio(conexion)
            if quitar:
                if not repo.quitar_empleado(proyecto_id, empleado_id):
                    raise EntidadNoEncontradaError("La asignación no existe")
            else:
                repo.asignar_empleado(proyecto_id, empleado_id)
        return self._operar("proyectos", operar)

    def _empleado_permitido(self, conexion, empleado_id):
        cuenta = self._cuenta(conexion)
        if not cuenta.autorizar("registro_tiempo"):
            raise AutorizacionError("No tienes permiso para gestionar horas")
        if cuenta.get_rol_acceso() != "administrador" and empleado_id != self.sesion.empleado_id:
            raise AutorizacionError("Solo puedes gestionar tus propios registros")

    def registros(self):
        with obtener_conexion() as conexion:
            cuenta = self._cuenta(conexion)
            repo = RegistroTiempoRepositorio(conexion)
            if cuenta.get_rol_acceso() == "administrador":
                return repo.listar()
            return repo.listar_por_empleado(self.sesion.empleado_id)

    def crear_registro(self, empleado_id, proyecto_id, fecha, horas, descripcion):
        with obtener_conexion() as conexion:
            self._empleado_permitido(conexion, empleado_id)
            return RegistroTiempoRepositorio(conexion).crear(
                empleado_id, proyecto_id, fecha, horas, descripcion
            )

    def actualizar_registro(self, registro_id, fecha, horas, descripcion):
        with obtener_conexion() as conexion:
            repo = RegistroTiempoRepositorio(conexion)
            registro = repo.obtener_por_id(registro_id)
            if registro is None:
                raise EntidadNoEncontradaError("El registro no existe")
            self._empleado_permitido(conexion, registro.empleado.get_id())
            return repo.actualizar(
                registro_id, registro.empleado.get_id(), registro.proyecto.get_id(),
                fecha, horas, descripcion
            )

    def eliminar_registro(self, registro_id):
        with obtener_conexion() as conexion:
            repo = RegistroTiempoRepositorio(conexion)
            registro = repo.obtener_por_id(registro_id)
            if registro is None:
                raise EntidadNoEncontradaError("El registro no existe")
            self._empleado_permitido(conexion, registro.empleado.get_id())
            repo.eliminar(registro_id)

    def datos_informes(self):
        return self._operar("informes", lambda c: SistemaRepositorio(c).cargar_dominio())

    def cambiar_contrasena(self, actual, nueva):
        nuevo_hash = CuentaUsuario.generar_hash(nueva)
        with obtener_conexion() as conexion:
            cuenta = self._cuenta(conexion)
            if not cuenta.verificar_contrasena(actual):
                raise AutorizacionError("La contraseña actual no es correcta")
            CuentaUsuarioRepositorio(conexion).actualizar_hash(cuenta.get_id(), nuevo_hash)
