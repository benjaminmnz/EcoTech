from datetime import date


class RegistroTiempo:
    def __init__(
        self,
        id_registro: int,
        fecha: date,
        horas_trabajadas: float,
        descripcion_tarea: str
    ):
        self.__id = id_registro
        self.fecha = fecha
        self.descripcion_tarea = descripcion_tarea

        self.registrar(horas_trabajadas)

        self.empleado = None

        self.proyecto = None

    def get_id(self) -> int:
        return self.__id

    def get_horas_trabajadas(self) -> float:
        return self.__horas_trabajadas

    def registrar(self, horas: float):
        if not self.__validar_horas(horas):
            raise ValueError("Las horas deben ser un número mayor que 0 y menor o igual que 24")

        self.__horas_trabajadas = horas

    def __validar_horas(self, horas: float) -> bool:
        if isinstance(horas, bool):
            return False

        if not isinstance(horas, (int, float)):
            return False

        return 0 < horas <= 24