# Aplicaciones Distribuidas

Ejemplos prácticos sobre ejecución secuencial, concurrencia y manejo de hilos en Python utilizando Docker.

---

## Estructura del Proyecto

* **`01_Secuencial.py`**: Demuestra una ejecución secuencial (una tarea a la vez).
* **`02_Concurrencia.py`**: Demuestra ejecución concurrente usando hilos (`threading`).
* **`03_Hilos.py`**: Demuestra condiciones de carrera (*race conditions*) y solución con `Lock`.

---

## Cómo ejecutar con Docker

El comando siempre es el mismo, **solo cambias el nombre del archivo al final**:

```bash
# Ejemplo 1: Secuencial
docker compose run --rm python-app python 01_Secuencial.py

# Ejemplo 2: Concurrencia
docker compose run --rm python-app python 02_Concurrencia.py

# Ejemplo 3: Hilos y Lock
docker compose run --rm python-app python 03_Hilos.py
```

> **Nota:** También puedes correr el script por defecto simplemente ejecutando:
> ```bash
> docker compose up
> ```
