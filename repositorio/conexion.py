import os
from pathlib import Path

import psycopg
from dotenv import load_dotenv

from dominio.excepciones import ConexionBaseDatosError


def obtener_conexion():
    ruta_env = Path(__file__).resolve().parent.parent / ".env"

    load_dotenv(
        dotenv_path=ruta_env,
        interpolate=False
    )

    variables_obligatorias = (
        "DB_HOST",
        "DB_PORT",
        "DB_NAME",
        "DB_USER",
        "DB_PASSWORD"
    )

    for variable in variables_obligatorias:
        if not os.getenv(variable):
            raise ValueError("Falta configurar la variable: " + variable)

    modo_ssl = os.getenv("DB_SSLMODE", "require")

    if modo_ssl not in ("require", "verify-ca", "verify-full"):
        raise ValueError("La conexión debe utilizar SSL")

    try:
        conexion = psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            sslmode=modo_ssl,
            connect_timeout=10
        )
    except psycopg.Error as error:
        raise ConexionBaseDatosError(
            "No se pudo conectar con la base de datos. "
            "Revisa la configuración y la conexión a internet."
        ) from error

    return conexion