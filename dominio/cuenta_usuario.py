from werkzeug.security import generate_password_hash, check_password_hash


class CuentaUsuario:
    def __init__(
        self,
        id_cuenta: int,
        usuario: str,
        contrasena_hash: str,
        rol_acceso: str
    ):
        if not usuario.strip():
            raise ValueError("El usuario no puede estar vacío")

        if not contrasena_hash:
            raise ValueError("El hash de la contraseña no puede estar vacío")

        if rol_acceso not in ("administrador", "empleado"):
            raise ValueError("El rol debe ser administrador o empleado")

        self.__id = id_cuenta
        self.usuario = usuario
        self.__contrasena_hash = contrasena_hash
        self._rol_acceso = rol_acceso

    def get_id(self) -> int:
        return self.__id

    @staticmethod
    def generar_hash(contrasena: str) -> str:
        if not contrasena:
            raise ValueError("La contraseña no puede estar vacía")

        return generate_password_hash(
            contrasena,
            method="pbkdf2:sha256:600000"
        )

    def verificar_contrasena(self, contrasena: str) -> bool:
        return check_password_hash(
            self.__contrasena_hash,
            contrasena
        )

    def autorizar(self, modulo: str) -> bool:
        permisos = {
            "administrador": (
                "empleados",
                "departamentos",
                "proyectos",
                "registro_tiempo",
                "informes"
            ),
            "empleado": (
                "registro_tiempo",
            )
        }

        return modulo in permisos[self._rol_acceso]

    def get_contrasena_hash(self) -> str:
        return self.__contrasena_hash

    def get_rol_acceso(self) -> str:
        return self._rol_acceso