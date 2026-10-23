"""Carga coherente de relaciones y configuración de la aplicación."""
from pathlib import Path
import psycopg

from dominio.excepciones import ErrorPersistencia
from repositorio.departamento_repo import DepartamentoRepositorio
from repositorio.empleado_repo import EmpleadoRepositorio
from repositorio.proyecto_repo import ProyectoRepositorio
from repositorio.cuenta_usuario_repo import CuentaUsuarioRepositorio
from repositorio.registro_tiempo_repo import RegistroTiempoRepositorio


class SistemaRepositorio:
    def __init__(self, conexion):
        self.conexion = conexion

    def hay_administrador(self):
        with self.conexion.cursor() as cursor:
            cursor.execute(
                "SELECT EXISTS (SELECT 1 FROM ecotech.cuenta_usuario WHERE rol_acceso = %s)",
                ("administrador",)
            )
            return cursor.fetchone()[0]

    def bloquear_configuracion(self):
        with self.conexion.cursor() as cursor:
            cursor.execute("SELECT pg_advisory_xact_lock(%s, %s)", (3021, 2))

    def comprobar_esquema(self):
        with self.conexion.cursor() as cursor:
            cursor.execute(
                "SELECT tablename, rowsecurity FROM pg_tables WHERE schemaname = %s",
                ("ecotech",)
            )
            tablas = dict(cursor.fetchall())
        necesarias = {"departamento", "empleado", "proyecto", "empleado_proyecto", "cuenta_usuario", "registro_tiempo"}
        if not necesarias.issubset(tablas):
            raise ErrorPersistencia("Faltan tablas: inicializa la base con datos/schema.sql")
        if not all(tablas[t] for t in necesarias):
            raise ErrorPersistencia("Activa RLS en las seis tablas del esquema")

    def inicializar(self):
        with self.conexion.cursor() as cursor:
            cursor.execute("SELECT COUNT(*) FROM pg_tables WHERE schemaname = %s", ("ecotech",))
            cantidad = cursor.fetchone()[0]
        if cantidad:
            self.comprobar_esquema()
            return False
        ruta = Path(__file__).resolve().parent.parent / "datos" / "schema.sql"
        with self.conexion.cursor() as cursor:
            cursor.execute(ruta.read_text(encoding="utf-8"))
        self.comprobar_esquema()
        return True

    def cargar_dominio(self):
        departamentos = DepartamentoRepositorio(self.conexion).listar()
        empleados = EmpleadoRepositorio(self.conexion).listar()
        proyectos = ProyectoRepositorio(self.conexion).listar()
        registros = RegistroTiempoRepositorio(self.conexion).listar()
        d_por_id = {d.get_id(): d for d in departamentos}
        e_por_id = {e.get_id(): e for e in empleados}
        p_por_id = {p.get_id(): p for p in proyectos}
        for empleado in empleados:
            departamento_id = empleado.departamento.get_id()
            empleado.departamento = None
            d_por_id[departamento_id].asignar_empleado(empleado)
        for proyecto_id, empleado_id in ProyectoRepositorio(self.conexion).listar_asignaciones():
            p_por_id[proyecto_id].asignar_empleado(e_por_id[empleado_id])
        for registro in registros:
            empleado_id = registro.empleado.get_id()
            proyecto_id = registro.proyecto.get_id()
            registro.empleado = None
            registro.proyecto = None
            e_por_id[empleado_id].agregar_registro(registro)
            p_por_id[proyecto_id].agregar_registro(registro)
        for departamento_id, gerente_id in DepartamentoRepositorio(self.conexion).listar_gerentes():
            if gerente_id is not None:
                d_por_id[departamento_id].asignar_gerente(e_por_id[gerente_id])
        for cuenta, empleado_id in CuentaUsuarioRepositorio(self.conexion).listar_con_empleado():
            e_por_id[empleado_id].asignar_cuenta(cuenta)
        return departamentos, empleados, proyectos, registros
