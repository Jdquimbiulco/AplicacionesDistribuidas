"""
EJEMPLO 3: HILOS Y CONDICIONES DE CARRERA
Situación de la vida diaria: queda UN SOLO asiento en el cine
y dos personas (Ana y Luis) intentan comprarlo al mismo tiempo.

Cada persona hace dos pasos:
    1. Mira si el asiento está libre
    2. Lo compra

Condición de carrera: los dos miran ANTES de que el otro compre,
ven "libre" y los dos creen que pueden comprarlo.
Resultado: el mismo asiento vendido a dos personas.
"""
import threading
import time


# ---------------------------------------------------------------
# VERSIÓN 1: SIN PROTECCIÓN
# ---------------------------------------------------------------
asiento_libre = True


def comprar_sin_proteccion(persona):
    global asiento_libre

    if asiento_libre:                      # Paso 1: mirar
        print(f"{persona}: el asiento está libre, lo voy a comprar...")
        time.sleep(1)                      # el pago tarda un poco
        asiento_libre = False              # Paso 2: comprar
        print(f"{persona}: ¡COMPRÉ el asiento!")
    else:
        print(f"{persona}: el asiento ya está ocupado")


print("=== SIN PROTECCIÓN ===")
ana = threading.Thread(target=comprar_sin_proteccion, args=("Ana",))
luis = threading.Thread(target=comprar_sin_proteccion, args=("Luis",))
ana.start()
luis.start()
ana.join()
luis.join()
print(">>> PROBLEMA: ¡el mismo asiento se vendió a DOS personas!\n")


# ---------------------------------------------------------------
# VERSIÓN 2: CON LOCK (solución)
# ---------------------------------------------------------------
asiento_libre = True
candado = threading.Lock()   # como una puerta con llave: entra uno a la vez


def comprar_con_lock(persona):
    global asiento_libre

    with candado:                          # solo UNA persona pasa a la vez
        if asiento_libre:
            print(f"{persona}: el asiento está libre, lo voy a comprar...")
            time.sleep(1)
            asiento_libre = False
            print(f"{persona}: ¡COMPRÉ el asiento!")
        else:
            print(f"{persona}: el asiento ya está ocupado")


print("=== CON LOCK ===")
ana = threading.Thread(target=comprar_con_lock, args=("Ana",))
luis = threading.Thread(target=comprar_con_lock, args=("Luis",))
ana.start()
luis.start()
ana.join()
luis.join()
print(">>> CORRECTO: el asiento se vendió a UNA sola persona")