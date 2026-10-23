
class EcoTechError(Exception):
    pass


class SalarioInvalidoError(EcoTechError):
    pass

class ConexionBaseDatosError(EcoTechError):
    pass

class ErrorPersistencia(EcoTechError):
    pass