from werkzeug.security import generate_password_hash, check_password_hash
from dominio.validaciones import identificador, texto


class CuentaUsuario:
    def __init__(self, id_cuenta: int, usuario: str, contrasena_hash: str, rol_acceso: str):
        self.__id = identificador(id_cuenta)
        self.usuario = texto(usuario, "El usuario")
        self.__contrasena_hash = texto(contrasena_hash, "El hash")
        if rol_acceso not in ("administrador", "empleado"):
            raise ValueError("El rol debe ser administrador o empleado")
        self._rol_acceso = rol_acceso
        self.empleado = None

    def get_id(self) -> int:
        return self.__id

    def get_contrasena_hash(self) -> str:
        return self.__contrasena_hash

    def get_rol_acceso(self) -> str:
        return self._rol_acceso

    @staticmethod
    def generar_hash(contrasena: str) -> str:
        if not isinstance(contrasena, str) or not contrasena:
            raise ValueError("La contraseña no puede estar vacía")
        if len(contrasena) > 1024:
            raise ValueError("La contraseña es demasiado larga")
        return generate_password_hash(contrasena, method="pbkdf2:sha256:600000")

    def verificar_contrasena(self, contrasena: str) -> bool:
        if not isinstance(contrasena, str) or len(contrasena) > 1024:
            return False
        try:
            return check_password_hash(self.__contrasena_hash, contrasena)
        except (ValueError, TypeError):
            return False

    def autorizar(self, modulo: str) -> bool:
        permisos = {
            "administrador": ("empleados", "departamentos", "proyectos", "registro_tiempo", "informes"),
            "empleado": ("registro_tiempo",)
        }
        return modulo in permisos.get(self._rol_acceso, ())
