# EcoTech — Evaluación Sumativa 2

Aplicación de consola en Python basada en el UML de ES1. Administra empleados,
departamentos, proyectos, cuentas y horas con persistencia PostgreSQL en Supabase.
Los informes PDF y Excel conservan la jerarquía aportada por el compañero del equipo.

## Ejecutar en Windows

Requisitos: Python 3.11 o posterior (verificado con 3.14), Git y un proyecto Supabase.
Desde la carpeta EcoTech:

~~~powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
~~~

Si .venv o .env ya existen, conservarlos; no volver a copiarlos sobre la configuración local.
Completar .env con los valores EXACTOS de Connect > Direct > Session pooler:

~~~dotenv
DB_HOST=
DB_PORT=5432
DB_NAME=postgres
DB_USER=
DB_PASSWORD=
DB_SSLMODE=require
~~~

La contraseña es la de PostgreSQL, no una API key ni la clave de inicio de sesión de
Supabase. Puede escribirse entre comillas en .env. No se imprime ni se versiona.
SSL require exige cifrado; no equivale a validar completamente el certificado del
servidor. Si se configura verify-full, deben prepararse los certificados correspondientes.

### Base nueva

Ejecutar una sola vez datos/schema.sql en el SQL Editor, o desde Python:

~~~powershell
python main.py --inicializar
~~~

La opción comprueba si las tablas ya existen y no borra datos. Si encuentra una
instalación parcial, informa el problema; no elimina tablas para repararla.
El esquema es ecotech. Las seis tablas tienen RLS habilitado. La consola se conecta
mediante el usuario PostgreSQL del proyecto (normalmente postgres a través del pooler),
que puede operar como propietario; no utiliza anon/authenticated ni Data API.
No se deben exponer estas credenciales en una aplicación web o cliente público.
El control de roles de la consola no se convierte automáticamente en políticas RLS.

### Iniciar

~~~powershell
python main.py
~~~

Si no hay administrador, la aplicación pide los datos para registrar el primero.
Se eligen usuario y contraseña: no hay claves predeterminadas ni credenciales de
demostración. Si ya existe un administrador, se solicita iniciar sesión.
Las cuentas de empleado creadas durante las pruebas anteriores siguen existiendo.
No se promovieron automáticamente a administrador.

El programa ya no ejecuta los antiguos bloques de prueba al iniciarse ni crea filas
de demostración en cada ejecución. El main.py anterior se conserva en el historial
Git y la rama respaldo/avance-local-20261023.

## Funcionalidades por rol

| Función | Administrador | Empleado |
|---|---|---|
| CRUD de departamentos y empleados | Sí | No |
| Designar o quitar gerente | Sí | No |
| CRUD de proyectos y asignaciones | Sí | Solo consulta de sus proyectos |
| Registrar, consultar, corregir y eliminar horas | Todos los empleados | Solo sus propias horas |
| Informes con salarios | Sí | No |
| Cambiar su contraseña | Sí | Sí |

El servicio vuelve a consultar la cuenta antes de las operaciones; ocultar opciones
en el menú no es el único control. No se puede borrar al empleado de la propia sesión.
El acceso incorrecto muestra un mensaje y devuelve al menú.
Los tres intentos de login limitan una ejecución de consola; no son un bloqueo
persistente contra intentos desde otro proceso.

## Estructura y responsabilidades

~~~text
EcoTech/
  dominio/
    persona.py, empleado.py, departamento.py, proyecto.py
    cuenta_usuario.py, registro_tiempo.py
    informe.py, informe_pdf.py, informe_excel.py
    excepciones.py, validaciones.py, __init__.py
  repositorio/
    conexion.py, departamento_repo.py, empleado_repo.py
    cuenta_usuario_repo.py, proyecto_repo.py, registro_tiempo_repo.py
    sistema_repo.py, __init__.py
  datos/schema.sql
  servicios.py
  main.py
  verificaciones.py
  .env.example
  .gitignore
  requirements.txt
  README.md
~~~

- Dominio: clases y reglas de negocio, sin SQL. Las nueve clases del UML están presentes.
- Repositorios: SQL parametrizado, acceso a datos y mapeo de filas a objetos.
- sistema_repo.py: inicialización y reconstrucción de relaciones con objetos compartidos.
- servicios.py: autorización, operaciones atómicas y coordinación de repositorios.
- main.py: entrada de datos, mensajes y menús, sin SQL.
- verificaciones.py: evidencias reproducibles de las comprobaciones exigidas.
- reportes/: resultados generados; se crea cuando hace falta y queda fuera de Git.

El ID 0 se utiliza solamente en objetos nuevos aún no persistidos. PostgreSQL genera
el ID real y los repositorios devuelven un objeto reconstruido con ese identificador;
no se introduce un setter público de ID. Fechas como objetos date. Salarios y horas
con Decimal para evitar cálculos monetarios aproximados con float. NUMERIC mantiene
la representación decimal en la base.

## Flujo de horas y relaciones

En memoria, Proyecto.registrar_tiempo coordina validar, crear RegistroTiempo y
asociarlo con el empleado y el proyecto. Es un método auxiliar de implementación.

En el flujo persistido, el menú solicita fecha, horas y tarea; el servicio determina
qué empleado puede usar la sesión y el repositorio crea el registro con IDs reales.
La llave foránea compuesta exige que exista la asignación empleado-proyecto.
No se registran horas automáticamente al asignar un empleado.

Al recuperar datos para informes se reconstruye un grafo coherente:
departamentos, empleados, cuentas, proyectos y registros comparten las mismas
instancias relacionadas. Los proyectos suman todos sus registros mediante
calcular_horas_totales(). Leer un registro aislado no carga todo el historial del
empleado/proyecto; los informes usan la carga completa, no esa lectura parcial.

Los aumentos inválidos devuelven False, según el UML. Las validaciones rechazan
números no finitos, booleanos usados como cantidades y cantidades fuera de rango.
Las fechas imposibles y entradas incorrectas se informan sin cerrar el menú.

### Reglas de eliminación

- Departamento con empleados: bloqueado; reasignar antes.
- Empleado: elimina cuenta, asignaciones y horas por composición; si era gerente,
  su departamento queda sin gerente.
- Proyecto con registros: bloqueado para conservar su historia.
- Quitar una asignación con registros: bloqueado; resolver primero esos registros.
- Trasladar a un gerente: quitar primero su designación, luego cambiar departamento.

## Informes

El administrador puede elegir PDF, Excel o ambos. Se exportan empleados, proyectos
con horas totales y registros con empleado y proyecto. No se exportan hashes ni claves.
La lista mixta de InformePDF e InformeExcel usa el mismo generar() sin preguntar
por el tipo de objeto. Se guarda en reportes/ con fecha, hora y sufijo único.
Los textos del Excel se escriben como texto, no como fórmulas; los del PDF se
escapan antes de usarse en Paragraph.
Los informes contienen salarios y el servicio limita su exportación al administrador.

## Verificaciones de ES2

Sin acceso a la base:

~~~powershell
python main.py --verificar-local
~~~

Con Supabase:

~~~powershell
python main.py --verificar
~~~

La suite incluye siete casos locales y dos casos de integración, con múltiples
comprobaciones por caso:

- Herencia, encapsulamiento, validaciones y rechazo de NaN/infinito/bool.
- Cuenta con hash y sal aleatoria; contraseña correcta e incorrecta.
- Relaciones del dominio, copias de colecciones y coordinación del registro.
- Generación real PDF/XLSX, datos vacíos y textos parecidos a fórmulas.
- CRUD, asignaciones, gerente y restauración de objetos relacionados.
- Búsqueda con el payload ' OR '1'='1 como parámetro.
- Fallo de la segunda escritura (usuario duplicado) y rollback del empleado nuevo.
- Impedir registrar horas sin asignación y modificar horas de otro empleado.
- Menú autenticado de empleado y rechazo de opciones administrativas.
- Persistencia comprobada desde una conexión nueva.

La integración usa rollback para revertir sus datos y una prueba separada confirma
la reapertura con limpieza posterior de su única fila temporal. Las secuencias de
identidad pueden avanzar incluso después de rollback: los saltos de ID son normales.
El programa no borra datos anteriores del usuario.
La conexión debe tener los permisos del propietario usados para esta consola de curso.

Las evidencias para el informe se obtienen ejecutando las verificaciones y capturando
su resultado, las consultas parametrizadas y el código de transacción. Las pruebas
automatizadas no sustituyen comprender y explicar el código.

## Transacciones

Los repositorios no confirman por su cuenta. El servicio usa una conexión compartida
dentro de with obtener_conexion(): si termina correctamente, Psycopg confirma; si
sale una excepción, revierte y cierra. Crear empleado y cuenta sucede dentro de ese
mismo bloque. El administrador inicial también se registra de forma atómica y usa
un bloqueo transaccional para evitar dos configuraciones iniciales simultáneas.
Las comprobaciones de la BD siguen aplicándose aunque se intente omitir el menú.

## Auditoría real del apoyo de IA

Herramienta usada: ChatGPT/Codex en este chat. Las versiones no registradas no se
inventan. La siguiente matriz describe decisiones reales sobre el código de este
proyecto; el equipo debe revisarla, agregar sus observaciones y registrar sus aportes.

| Fragmento / propuesta | Aspecto | Decisión | Justificación y evidencia |
|---|---|---|---|
| SQL con marcadores %s y valores separados | Seguridad | Acepto | Se conserva; la prueba con ' OR '1'='1 busca datos literales sin devolver filas ajenas. |
| Salario/horas iniciales sin validación completa y cálculo con float | Integridad | Modifico | Decimal, validación de finitud, rango y decimales; se rechazan NaN, infinito y bool. |
| Mostrar autorizar() como True/False en pruebas sin bloquear operaciones | Seguridad | Modifico | Servicios comprueban rol y propiedad antes de cada operación; una cuenta de empleado no puede modificar registros ajenos. |
| Crear registro y asociarlo por llamadas separadas en main | Consistencia | Modifico | Coordinación del dominio, transacción en persistencia y llave compuesta de asignación; prueba real de rollback. |
| Hash PBKDF2 con Werkzeug y sal automática | Contraseñas | Acepto | No se almacena texto original; la cuenta recuperada verifica la contraseña y rechaza otra. |
| Informes del compañero con listas parciales | Datos / POO | Modifico | Se preserva la jerarquía y el formato; se cargan relaciones completas y se agrega el proyecto del registro. |

No se afirma haber escrito sin asistencia los fragmentos apoyados por IA.
La autoría humana y porcentajes deben declararse con sus nombres reales en el informe,
sin atribuir todo el código generado a un integrante.

## Pendientes de la entrega académica, fuera de ejecutar la aplicación

- Completar el informe ES2 en su plantilla con capturas reales.
- Registrar nombres, aportes y coordinación reales de ambos integrantes.
- Preparar la defensa individual y repasar el flujo de registros y conexiones.
- Comprobar la configuración de Supabase desde el computador del compañero.
- Entregar el ZIP del código sin .env, .venv, .git, claves ni datos personales.

## Documentación

- Python: https://docs.python.org/3/
- Psycopg y parámetros: https://www.psycopg.org/psycopg3/docs/basic/params.html
- Transacciones: https://www.psycopg.org/psycopg3/docs/basic/transactions.html
- Supabase PostgreSQL: https://supabase.com/docs/guides/database/connecting-to-postgres
- Werkzeug: https://werkzeug.palletsprojects.com/en/stable/utils/
- ReportLab: https://docs.reportlab.com/reportlab/userguide/ch5_platypus/
- openpyxl: https://openpyxl.readthedocs.io/en/stable/tutorial.html
