# FFT Dashboard

Esta aplicaci\u00f3n muestra datos de un aceler\u00f3metro en un tablero web.

## Instalaci\u00f3n

1. Crear un entorno virtual (opcional pero recomendado).
2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Ejecuci\u00f3n con datos simulados

Para usar el generador de datos interno, defina la variable de entorno `SIMULATED_DATA` con valor `1` al lanzar la aplicaci\u00f3n (sin espacios alrededor del valor):

```bash
SIMULATED_DATA=1 python main.py
```

En Windows use:
```cmd
set SIMULATED_DATA=1 && python main.py
```

La variable se consulta en `dashboard/callbacks.py`:
```python
if os.getenv("SIMULATED_DATA", "0") == "1":
    from acquisition import simulator as data_source
else:
    from acquisition import udp_receiver as data_source
```

Si `SIMULATED_DATA` no est\u00e1 definida o es `0`, la aplicaci\u00f3n esperar\u00e1 paquetes UDP reales.

Puede verificar el valor de la variable con:
```bash
python -c "import os; print(os.getenv('SIMULATED_DATA'))"