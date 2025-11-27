# Desktop App (Python + MySQL)

Aplicación de escritorio (tkinter) que consume una BD.  

## Requisitos
- Python 3.8+
- MySQL Server y cliente `mysql` en PATH
- Config en `config.json` (por defecto: root / 3306 / c)

## Ejecutar
```bash
python app.py
```
## En la ventana de conexión: Probar conexión → Guardar y continuar.

Al iniciar, la app ejecuta automáticamente:

- sql/schema_seed.sql (solo si Empleado está vacío)

- sql/procedures_all.sql

- sql/triggers.sql

## Estructura
<img width="217" height="199" alt="image" src="https://github.com/user-attachments/assets/41960a0e-30fd-4a8e-a29b-7d3e4efd17aa" />

## Problemas Comunes
- mysql no encontrado → agrega el binario al PATH.
- “Duplicate entry” → el seed se omite si ya hay datos en Empleado.

## Leer "Leeme.txt" en raíz de proyecto para mayor información y Manual de Usuario del aplicativo COTEIND para comprender el uso
