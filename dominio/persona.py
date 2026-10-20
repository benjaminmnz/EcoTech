class Persona:
    def __init__(self, nombre: str, direccion: str, telefono: str, email: str):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email

    def get_nombre(self) -> str:
        return self.nombre