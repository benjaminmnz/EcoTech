import re
from dominio.validaciones import texto


class Persona:
    def __init__(self, nombre: str, direccion: str, telefono: str, email: str):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        self._nombre = texto(valor, "El nombre")

    @property
    def direccion(self):
        return self._direccion

    @direccion.setter
    def direccion(self, valor):
        self._direccion = texto(valor, "La dirección")

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):
        self._telefono = texto(valor, "El teléfono")

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        valor = texto(valor, "El correo")
        if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", valor):
            raise ValueError("El correo no tiene un formato válido")
        self._email = valor

    def get_nombre(self) -> str:
        return self.nombre
