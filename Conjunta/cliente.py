"""
=============================================================================
CLIENTE DE CHAT DISTRIBUIDO EN TIEMPO REAL
=============================================================================
Asignatura: Aplicaciones Distribuidas
Módulo: Examen Práctico - Parcial 1

Descripción:
Cliente de chat en tiempo real implementado con sockets TCP y la biblioteca
estándar `threading` de Python. Se conecta al servidor en ejecución (dentro
de Docker o en la máquina anfitriona) y permite el intercambio de mensajes
bidireccional y simultáneo con el servidor y con otros clientes sin esperar turnos.

Características principales:
1. Concurrencia con Hilos (Threading):
   - Hilo de recepción (`recibir_mensajes`): Escucha continuamente los mensajes
     provenientes del servidor (mensajes de [SERVIDOR] y de otros clientes como [CLIENTE 2]).
   - Hilo principal de envío (`enviar_mensajes`): Lee la entrada de texto del usuario
     desde la terminal y la envía al servidor inmediatamente.
2. Identificación del participante:
   - Puede recibir el número/nombre por argumento de consola:
     Ejemplo: `python cliente.py 1`        => Se conecta como [CLIENTE 1]
              `python cliente.py 2`        => Se conecta como [CLIENTE 2]
              `python cliente.py servidor` => Se conecta como [SERVIDOR] (consola de servidor)
   - Si no se pasa argumento, despliega un menú interactivo:
     Opción 0: SERVIDOR
     Opción 1: CLIENTE 1
     Opción 2: CLIENTE 2
3. Comunicación fluida y sin turnos:
   - La recepción y el envío no se bloquean mutuamente.
   - Utiliza secuencias de escape ANSI para redibujar el prompt limpiamente
     cuando llega un mensaje mientras el usuario está escribiendo.
=============================================================================
"""

import os
import sys
import socket
import threading

# Configuración del servidor de destino
SERVER_HOST = os.getenv("SERVER_HOST", "localhost")
SERVER_PORT = int(os.getenv("SERVER_PORT", "5000"))

# Control del estado del cliente
cliente_activo = True
mi_identificador = "CLIENTE"


def recibir_mensajes(canal_lectura, mi_nombre):
    """
    Hilo de recepción: Escucha mensajes del servidor en tiempo real.
    Imprime los mensajes entrantes sin bloquear la escritura del usuario.
    """
    global cliente_activo

    while cliente_activo:
        try:
            linea = canal_lectura.readline()
            if not linea:
                # El servidor cerró la conexión
                if cliente_activo:
                    print("\n[INFO] Conexión cerrada por el servidor.", flush=True)
                cliente_activo = False
                break

            mensaje = linea.rstrip("\r\n")
            if not mensaje:
                continue

            # Si la terminal es interactiva, limpiar la línea actual y restaurar el prompt
            if sys.stdout.isatty():
                sys.stdout.write(f"\r\033[K{mensaje}\n[{mi_nombre}]: ")
                sys.stdout.flush()
            else:
                print(mensaje, flush=True)

        except (ConnectionResetError, BrokenPipeError, OSError):
            if cliente_activo:
                print("\n[INFO] Se perdió la conexión con el servidor.", flush=True)
            cliente_activo = False
            break
        except Exception as e:
            if cliente_activo:
                print(f"\n[ERROR] Error recibiendo mensaje: {e}", flush=True)
            cliente_activo = False
            break


def enviar_mensajes(sock, canal_lectura, mi_nombre):
    """
    Hilo de envío: Lee lo que el usuario escribe en la terminal
    y lo envía al servidor por el socket TCP.
    """
    global cliente_activo

    while cliente_activo:
        try:
            # Solicitar mensaje al usuario con el prefijo de su identificador
            texto = input(f"[{mi_nombre}]: ")

            texto_limpio = texto.strip()
            if not texto_limpio:
                continue

            # Si el usuario desea salir del chat
            if texto_limpio.lower() == "salir":
                sock.sendall("SALIR\n".encode("utf-8"))
                print("[*] Saliendo del chat...", flush=True)
                cliente_activo = False
                break

            # Enviar mensaje al servidor
            sock.sendall((texto_limpio + "\n").encode("utf-8"))

        except (EOFError, KeyboardInterrupt):
            print("\n[*] Saliendo del chat...", flush=True)
            cliente_activo = False
            try:
                sock.sendall("SALIR\n".encode("utf-8"))
            except Exception:
                pass
            break
        except Exception as e:
            if cliente_activo:
                print(f"\n[ERROR] Error al enviar mensaje: {e}", flush=True)
            cliente_activo = False
            break


def resolver_nombre_solicitado():
    """
    Determina qué nombre solicitar al servidor según los argumentos CLI o entrada interactiva.
    Ejemplos soportados:
    - python cliente.py 1           -> CLIENTE 1
    - python cliente.py 2           -> CLIENTE 2
    - python cliente.py servidor    -> SERVIDOR (permite escribir como servidor desde terminal)
    - python cliente.py             -> Menú interactivo [0: SERVIDOR / 1: CLIENTE 1 / 2: CLIENTE 2]
    """
    if len(sys.argv) > 1:
        arg = sys.argv[1].strip()
        if arg in ("0", "servidor", "SERVIDOR", "admin", "ADMIN"):
            return "SERVIDOR"
        if arg in ("1", "2"):
            return f"CLIENTE {arg}"
        if arg.upper().startswith("CLIENTE"):
            return arg.upper()
        return arg

    # Entrada interactiva si no se especificaron argumentos en la terminal
    print("------------------------------------------------------------", flush=True)
    print("  SELECCIÓN DE IDENTIFICADOR", flush=True)
    print("------------------------------------------------------------", flush=True)
    print("  0 = Conectar como [SERVIDOR] (consola para enviar mensajes del servidor)", flush=True)
    print("  1 = Conectar como [CLIENTE 1]", flush=True)
    print("  2 = Conectar como [CLIENTE 2]", flush=True)
    print("  Enter directo = Asignación automática por el servidor", flush=True)
    print("------------------------------------------------------------", flush=True)
    try:
        eleccion = input("Seleccione una opción [0/1/2/Enter]: ").strip()
        if eleccion in ("0", "servidor", "SERVIDOR", "admin", "ADMIN"):
            return "SERVIDOR"
        if eleccion in ("1", "2"):
            return f"CLIENTE {eleccion}"
        if eleccion:
            return eleccion.upper() if eleccion.lower().startswith("cliente") else eleccion
        return "AUTO"
    except (EOFError, KeyboardInterrupt):
        return "AUTO"


def main():
    global cliente_activo, mi_identificador

    nombre_solicitado = resolver_nombre_solicitado()

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"[*] Conectando a {SERVER_HOST}:{SERVER_PORT}...", flush=True)
        sock.connect((SERVER_HOST, SERVER_PORT))
    except ConnectionRefusedError:
        print(f"\n[ERROR] No se pudo conectar a {SERVER_HOST}:{SERVER_PORT}.", flush=True)
        print("[!] Verifica que el contenedor del servidor esté en ejecución con:", flush=True)
        print("    docker compose up", flush=True)
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Error al conectar: {e}", flush=True)
        sys.exit(1)

    canal_lectura = sock.makefile("r", encoding="utf-8")

    try:
        # Enviar solicitud de identificación (Handshake)
        sock.sendall(f"IDENTIFICAR:{nombre_solicitado}\n".encode("utf-8"))

        # Recibir confirmación de nombre asignado
        respuesta = canal_lectura.readline()
        if not respuesta or not respuesta.startswith("ASIGNADO:"):
            print("[ERROR] El servidor no respondió la identificación adecuada.", flush=True)
            sock.close()
            sys.exit(1)

        mi_identificador = respuesta.split(":", 1)[1].strip()

        print("=" * 60, flush=True)
        print(f"          CHAT CONECTADO - PARTICIPANTE: [{mi_identificador}]", flush=True)
        print("=" * 60, flush=True)
        print(f"[*] Conectado al servidor en {SERVER_HOST}:{SERVER_PORT}", flush=True)
        print("[*] Escribe tu mensaje y presiona Enter para enviar.", flush=True)
        print("[*] Comunicación sin turnos: puedes escribir en cualquier momento.", flush=True)
        print("[*] Escribe 'salir' para desconectarte.", flush=True)
        print("=" * 60, flush=True)

        # Iniciar hilo de recepción en segundo plano
        hilo_recv = threading.Thread(
            target=recibir_mensajes,
            args=(canal_lectura, mi_identificador),
            daemon=True
        )
        hilo_recv.start()

        # El hilo principal se encarga de la captura y envío de mensajes
        enviar_mensajes(sock, canal_lectura, mi_identificador)

    except KeyboardInterrupt:
        print("\n[*] Desconectando...", flush=True)
    finally:
        cliente_activo = False
        try:
            sock.close()
        except Exception:
            pass
        print(f"[*] Sesión de [{mi_identificador}] finalizada.", flush=True)


if __name__ == "__main__":
    main()
