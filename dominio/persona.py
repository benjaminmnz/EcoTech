class Persona:

    def __init__(self, nombre, direccion, telefono, email):
        self.nombre = nombre
        self.direccion = direccion
        self.telefono = telefono
        self.email = email

    def get_nombre(self):
        """Devuelve el nombre."""
        return self.nombre