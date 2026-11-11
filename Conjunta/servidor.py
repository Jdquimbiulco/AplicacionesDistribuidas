"""
=============================================================================
SERVIDOR DE CHAT DISTRIBUIDO EN TIEMPO REAL
=============================================================================
Asignatura: Aplicaciones Distribuidas
Módulo: Examen Práctico - Parcial 1

Descripción:
Servidor multihilo implementado con sockets TCP y la biblioteca estándar
`threading` de Python. Permite la conexión simultánea de múltiples clientes
(Cliente 1, Cliente 2), reenvía mensajes entre ellos en tiempo real sin
esperar turnos, y permite al propio servidor participar en la conversación
enviando mensajes a todos los clientes conectados.

Características principales:
1. Concurrencia con Hilos (Threading):
   - Un hilo dedicado a aceptar nuevas conexiones sin bloquear.
   - Un hilo independiente por cada cliente para recibir sus mensajes.
   - Un hilo de consola para que el operador del servidor pueda escribir
     mensajes identificados como [SERVIDOR] y difundirlos a todos los clientes.
2. Identificación de participantes:
   - Identifica y etiqueta correctamente a [CLIENTE 1], [CLIENTE 2] y [SERVIDOR].
3. Comunicación bidireccional sin turnos:
   - Ningún participante debe esperar turnos para escribir o recibir mensajes.
4. Sincronización segura (Thread-Safe):
   - Uso de `threading.Lock()` para evitar condiciones de carrera al acceder
     a la lista de clientes conectados.
=============================================================================
"""

import os
import sys
import time
import socket
import threading

# Configuración del servidor (variables de entorno o valores por defecto)
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "5000"))

# Diccionario para almacenar los clientes conectados: {socket_cliente: "CLIENTE 1"}
clientes_conectados = {}

# Candado (Lock) para sincronizar el acceso concurrente al diccionario de clientes
candado_clientes = threading.Lock()

# Control de ejecución del servidor
servidor_activo = True


def difundir(mensaje, socket_remitente=None):
    """
    Difunde un mensaje a los clientes conectados.
    
    Parámetros:
    - mensaje: Texto a enviar (debe terminar en salto de línea \\n).
    - socket_remitente: Socket del cliente que originó el mensaje.
      Si se especifica, el mensaje se envía a TODOS LOS DEMÁS clientes.
      Si es None, se envía a ABSOLUTAMENTE TODOS los clientes (ej. mensajes del [SERVIDOR]).
    """
    with candado_clientes:
        destinatarios = list(clientes_conectados.keys())
        for sock in destinatarios:
            if sock != socket_remitente:
                try:
                    sock.sendall(mensaje.encode("utf-8"))
                except (BrokenPipeError, ConnectionResetError, OSError):
                    # Si falla el envío, el hilo del cliente gestionará la desconexión
                    pass


def asignar_identificador(nombre_solicitado=None):
    """
    Determina el identificador del cliente.
    Si el cliente solicita un nombre (ej. 'CLIENTE 1', 'CLIENTE 2' o 'SERVIDOR'), se valida su disponibilidad.
    Si no se solicita o solicita 'AUTO', se le asigna el primer identificador libre disponible.
    """
    with candado_clientes:
        nombres_en_uso = set(clientes_conectados.values())

        if nombre_solicitado and nombre_solicitado != "AUTO":
            # Normalizar nombres conocidos
            solicitud = nombre_solicitado.upper()
            if solicitud in ("SERVIDOR", "ADMIN"):
                return "SERVIDOR"
            if solicitud not in nombres_en_uso:
                return solicitud

        # Asignación automática ordenada: intentar CLIENTE 1, luego CLIENTE 2, etc.
        indice = 1
        while True:
            candidato = f"CLIENTE {indice}"
            if candidato not in nombres_en_uso:
                return candidato
            indice += 1


def manejar_cliente(cliente_socket, direccion):
    """
    Hilo individual para atender a un cliente conectado.
    Maneja la recepción continua de mensajes y la desconexión sin bloquear a los demás.
    """
    nombre_cliente = "DESCONOCIDO"
    canal_lectura = cliente_socket.makefile("r", encoding="utf-8")

    try:
        # 1. Fase de Handshake / Identificación
        primera_linea = canal_lectura.readline()
        if not primera_linea:
            cliente_socket.close()
            return

        primera_linea = primera_linea.strip()
        solicitud_nombre = None
        if primera_linea.startswith("IDENTIFICAR:"):
            solicitud_nombre = primera_linea.split(":", 1)[1].strip()

        # Asignar identificador único (CLIENTE 1, CLIENTE 2, SERVIDOR, etc.)
        nombre_cliente = asignar_identificador(solicitud_nombre)

        # Registrar al cliente de forma segura (Thread-Safe)
        with candado_clientes:
            clientes_conectados[cliente_socket] = nombre_cliente

        # Enviar confirmación al cliente con el nombre asignado
        cliente_socket.sendall(f"ASIGNADO:{nombre_cliente}\n".encode("utf-8"))

        print(f"[CONEXIÓN] {nombre_cliente} conectado desde {direccion}", flush=True)

        # Notificar a los otros clientes que alguien se unió
        difundir(f"*** {nombre_cliente} se ha unido al chat ***\n", socket_remitente=cliente_socket)

        # 2. Bucle principal de recepción de mensajes del cliente
        while servidor_activo:
            linea = canal_lectura.readline()
            if not linea:
                # El cliente cerró la conexión
                break

            texto = linea.strip()
            if not texto:
                continue

            # Si el cliente solicita salir voluntariamente
            if texto.upper() == "SALIR":
                break

            # Formatear el mensaje con el identificador exacto solicitado en el examen:
            # Ejemplo: [CLIENTE 1]: Hola a todos
            mensaje_formateado = f"[{nombre_cliente}]: {texto}"

            # Mostrar el mensaje en la consola del servidor
            print(mensaje_formateado, flush=True)

            # Distribuir el mensaje a los demás clientes conectados
            difundir(mensaje_formateado + "\n", socket_remitente=cliente_socket)

    except (ConnectionResetError, BrokenPipeError):
        pass
    except Exception as e:
        print(f"[ERROR] Error atendiendo a {nombre_cliente}: {e}", flush=True)
    finally:
        # 3. Desconexión limpia del cliente
        with candado_clientes:
            if cliente_socket in clientes_conectados:
                del clientes_conectados[cliente_socket]

        try:
            cliente_socket.close()
        except Exception:
            pass

        print(f"[DESCONEXIÓN] {nombre_cliente} se ha desconectado.", flush=True)
        # Notificar a los clientes restantes
        difundir(f"*** {nombre_cliente} ha salido del chat ***\n")


def consola_servidor():
    """
    Hilo para la consola del servidor.
    Permite al servidor escribir mensajes en cualquier momento y enviarlos
    a todos los clientes conectados con el formato: [SERVIDOR]: <mensaje>
    Funciona tanto en ejecución local como al interactuar con el contenedor vía:
    `docker attach chat_servidor` o `docker compose run --service-ports servidor`.
    """
    while servidor_activo:
        try:
            linea = sys.stdin.readline()
            if not linea:
                # Si no hay entrada activa (ej. antes de conectar docker attach),
                # pausar brevemente en vez de matar el hilo
                time.sleep(1)
                continue

            texto = linea.strip()
            if not texto:
                continue

            # Formatear exactamente como lo solicita el examen
            mensaje_formateado = f"[SERVIDOR]: {texto}"

            # Si la terminal es interactiva (TTY), formatear la línea
            if sys.stdout.isatty():
                sys.stdout.write(f"\033[A\r\033[K{mensaje_formateado}\n")
                sys.stdout.flush()
            else:
                print(mensaje_formateado, flush=True)

            # Enviar a TODOS los clientes conectados
            difundir(mensaje_formateado + "\n", socket_remitente=None)

        except (EOFError, KeyboardInterrupt):
            time.sleep(1)
            continue
        except Exception as e:
            if servidor_activo:
                time.sleep(1)
            continue


def iniciar_servidor():
    """
    Punto de entrada principal para iniciar el socket TCP y el bucle de conexiones.
    """
    global servidor_activo

    servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Permite reutilizar la dirección/puerto inmediatamente después de reiniciar
    servidor_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        servidor_socket.bind((HOST, PORT))
        servidor_socket.listen(5)

        print("=" * 60, flush=True)
        print("          SERVIDOR DE CHAT DISTRIBUIDO (TCP + HILOS)", flush=True)
        print("=" * 60, flush=True)
        print(f"[*] Servidor escuchando en {HOST}:{PORT}", flush=True)
        print("[*] Esperando conexiones de CLIENTE 1 y CLIENTE 2...", flush=True)
        print("[*] Escribe en esta terminal y presiona Enter para enviar como [SERVIDOR]", flush=True)
        print("=" * 60, flush=True)

        # Iniciar hilo para que el servidor pueda escribir mensajes en cualquier momento
        hilo_consola = threading.Thread(target=consola_servidor, daemon=True)
        hilo_consola.start()

        # Bucle para aceptar conexiones entrantes de clientes
        while servidor_activo:
            try:
                cliente_sock, direccion = servidor_socket.accept()
                # Iniciar un hilo dedicado para cada cliente conectado
                hilo_cliente = threading.Thread(
                    target=manejar_cliente,
                    args=(cliente_sock, direccion),
                    daemon=True
                )
                hilo_cliente.start()
            except (KeyboardInterrupt, OSError):
                break

    except Exception as e:
        print(f"[FATAL] No se pudo iniciar el servidor: {e}", flush=True)
    finally:
        servidor_activo = False
        try:
            servidor_socket.close()
        except Exception:
            pass
        print("\n[*] Servidor finalizado correctamente.", flush=True)


if __name__ == "__main__":
    iniciar_servidor()
