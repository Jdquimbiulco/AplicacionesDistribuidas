"""
EJEMPLO 2: CONCURRENCIA
Situación de la vida diaria: preparar el MISMO desayuno, pero haciendo
varias cosas a la vez (el agua hierve mientras se tuesta el pan y se fríe el huevo).

Cada tarea corre en su propio hilo (thread).
Tiempo total ≈ el de la tarea más larga, no la suma de todas.
"""
import threading
import time

inicio = time.time()


def log(mensaje):
    print(f"[{time.time() - inicio:4.1f}s] {mensaje}")


def hervir_agua():
    log("Empiezo a hervir el agua...")
    time.sleep(3)
    log("Agua lista")


def tostar_pan():
    log("Empiezo a tostar el pan...")
    time.sleep(2)
    log("Pan listo")


def freir_huevo():
    log("Empiezo a freír el huevo...")
    time.sleep(2)
    log("Huevo listo")


print("=== DESAYUNO CONCURRENTE ===")

# 1. Creamos un hilo por cada tarea
hilos = [
    threading.Thread(target=hervir_agua),
    threading.Thread(target=tostar_pan),
    threading.Thread(target=freir_huevo),
]

# 2. Los arrancamos todos: empiezan casi al mismo tiempo
for hilo in hilos:
    hilo.start()

# 3. Esperamos a que todos terminen
for hilo in hilos:
    hilo.join()

print(f"\nDesayuno listo en {time.time() - inicio:.1f} segundos (la tarea más larga fue hervir agua: 3s)")
