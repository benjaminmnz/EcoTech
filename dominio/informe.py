from abc import ABC, abstractmethod
from datetime import date
from pathlib import Path


class Informe(ABC):
    def __init__(self, id_informe, empleados, proyectos, registros, ruta_archivo):
        self.__id = id_informe
        self.fecha_generacion = date.today()
        self._empleados = list(empleados)
        self._proyectos = list(proyectos)
        self._registros = list(registros)
        self.ruta_archivo = Path(ruta_archivo)

    def get_id(self):
        return self.__id

    def _preparar_destino(self, extension):
        if self.ruta_archivo.suffix.lower() != extension:
            raise ValueError("La ruta debe terminar en " + extension)

        if self.ruta_archivo.exists():
            raise FileExistsError("Ya existe el archivo: " + str(self.ruta_archivo))

        self.ruta_archivo.parent.mkdir(parents=True, exist_ok=True)

    def _obtener_secciones(self):
        filas_empleados = []
        for empleado in self._empleados:
            departamento = "Sin asignar"
            if empleado.departamento is not None:
                departamento = empleado.departamento.nombre

            filas_empleados.append([
                empleado.get_id(),
                empleado.get_nombre(),
                departamento,
                empleado.get_salario()
            ])

        filas_proyectos = []
        for proyecto in self._proyectos:
            filas_proyectos.append([
                proyecto.get_id(),
                proyecto.nombre,
                proyecto.fecha_inicio.isoformat(),
                proyecto.calcular_horas_totales()
            ])

        filas_registros = []
        for registro in self._registros:
            nombre_empleado = "Sin asignar"
            if registro.empleado is not None:
                nombre_empleado = registro.empleado.get_nombre()

            filas_registros.append([
                registro.get_id(),
                registro.fecha.isoformat(),
                nombre_empleado,
                registro.proyecto.nombre if registro.proyecto is not None else "Sin asignar",
                registro.get_horas_trabajadas(),
                registro.descripcion_tarea
            ])

        return [
            ("Empleados", ["ID", "Nombre", "Departamento", "Salario"], filas_empleados),
            ("Proyectos", ["ID", "Nombre", "Fecha de inicio", "Horas totales"], filas_proyectos),
            ("Registros", ["ID", "Fecha", "Empleado", "Proyecto", "Horas", "Tarea"], filas_registros)
        ]

    @abstractmethod
    def generar(self):
        pass
