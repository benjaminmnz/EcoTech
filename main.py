from dominio.persona import Persona


persona = Persona(
    nombre="Ana Pérez",
    direccion="Los Álamos 123",
    telefono="912345678",
    email="ana@example.com"
)

print(persona.get_nombre())