class RegistroTiempo:
    """Horas trabajadas por un empleado en una fecha."""

    def __init__(self, id_registro, fecha, horas_trabajadas, descripcion_tarea):
        self._id = id_registro
        self.fecha = fecha
        self._horas_trabajadas = horas_trabajadas
        self.descripcion_tarea = descripcion_tarea

    def get_id(self):
        """Devuelve el id."""
        return self._id

    def registrar(self, horas):
        """Registra las horas trabajadas, si son válidas."""
        if not self._validar_horas(horas):
            raise ValueError("Las horas deben estar entre 0 y 24")
        self._horas_trabajadas = horas

    def _validar_horas(self, horas):
        """Devuelve True si las horas son un valor razonable."""
        return 0 < horas <= 24