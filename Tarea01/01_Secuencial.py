"""
EJEMPLO 1: EJECUCIÓN SECUENCIAL
Situación de la vida diaria: preparar el desayuno UNA tarea a la vez.

En una ejecución secuencial, cada tarea espera a que termine la anterior.
Tiempo total = suma de los tiempos de todas las tareas.
"""
import time

inicio = time.time()


def log(mensaje):
    """Imprime un mensaje con los segundos transcurridos desde el inicio."""
    print(f"[{time.time() - inicio:4.1f}s] {mensaje}")


def hervir_agua():
    log("Empiezo a hervir el agua...")
    time.sleep(3)  # simulamos que tarda 3 segundos
    log("Agua lista")


def tostar_pan():
    log("Empiezo a tostar el pan...")
    time.sleep(2)
    log("Pan listo")


def freir_huevo():
    log("Empiezo a freír el huevo...")
    time.sleep(2)
    log("Huevo listo")


print("=== DESAYUNO SECUENCIAL ===")
hervir_agua()   # Hasta que no termine, no pasa a la siguiente línea
tostar_pan()
freir_huevo()

print(f"\nDesayuno listo en {time.time() - inicio:.1f} segundos")