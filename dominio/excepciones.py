class EcoTechError(Exception):
    pass


class SalarioInvalidoError(EcoTechError, ValueError):
    pass


class ConexionBaseDatosError(EcoTechError):
    pass


class ErrorPersistencia(EcoTechError):
    pass


class AutorizacionError(EcoTechError):
    pass


class EntidadNoEncontradaError(EcoTechError):
    pass
