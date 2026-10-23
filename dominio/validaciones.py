from datetime import date, datetime
from decimal import Decimal, InvalidOperation


def texto(valor, campo):
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(campo + " no puede estar vacío")
    if len(valor) > 10000 or any(ord(c) < 32 and c not in "\n\r\t" for c in valor):
        raise ValueError(campo + " contiene caracteres no válidos o es demasiado largo")
    return valor.strip()


def identificador(valor):
    if isinstance(valor, bool) or not isinstance(valor, int) or valor < 0:
        raise ValueError("El identificador debe ser un entero no negativo")
    return valor


def fecha_valida(valor):
    if not isinstance(valor, date) or isinstance(valor, datetime):
        raise ValueError("La fecha debe ser un objeto date")
    return valor


def decimal_positivo(valor, campo, maximo):
    if isinstance(valor, bool):
        raise ValueError(campo + " debe ser un número")
    try:
        numero = Decimal(str(valor))
    except (InvalidOperation, ValueError) as error:
        raise ValueError(campo + " debe ser un número") from error
    if not numero.is_finite() or numero <= 0 or numero > Decimal(str(maximo)):
        raise ValueError(campo + " está fuera del rango permitido")
    if numero != numero.quantize(Decimal("0.01")):
        raise ValueError(campo + " admite como máximo dos decimales")
    return numero
