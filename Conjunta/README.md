# Examen Práctico: Chat en Tiempo Real con Python, Hilos, Sockets TCP y Docker

**Asignatura:** Aplicaciones Distribuidas  
**Evaluación:** Parcial 1 (Conjunta)  
**Estudiante:** Juan Quimbiulco  

---

## 1. Descripción del Proyecto

Este proyecto implementa una aplicación de chat distribuido en tiempo real que permite la comunicación simultánea y bidireccional entre **un servidor** y **dos clientes** (`CLIENTE 1` y `CLIENTE 2`), utilizando **sockets TCP** e **hilos de ejecución (`threading`)** en Python, con el servidor desplegado dentro de un contenedor **Docker**.

### Participantes:
- **Servidor:** Se ejecuta dentro de un contenedor Docker mediante `docker compose`. Recibe conexiones concurrentes, distribuye mensajes entre clientes y envía sus propios mensajes identificados como `[SERVIDOR]`.
- **Cliente 1:** Se ejecuta en una terminal independiente de VS Code, envía y recibe mensajes en tiempo real.
- **Cliente 2:** Se ejecuta en una segunda terminal independiente de VS Code, envía y recibe mensajes en tiempo real.

---

## 2. Diagrama de Arquitectura

```text
               +--------------------------------------+
               |               SERVIDOR               |
               |             Python + TCP             |
               |          Contenedor Docker           |
               |              Puerto 5000             |
               +-------------------+------------------+
                                   ^
                                   | (Sockets TCP / Hilos)
                   +---------------+---------------+
                   |                               |
                   v                               v
    +------------------------------+ +------------------------------+
    |          CLIENTE 1           | |          CLIENTE 2           |
    |       Terminal VS Code       | |       Terminal VS Code       |
    |            Python            | |            Python            |
    +------------------------------+ +------------------------------+
```

---

## 3. Estructura del Proyecto

```text
Conjunta/
├── servidor.py         # Servidor multihilo TCP (distribución de mensajes y consola de servidor)
├── cliente.py          # Cliente TCP interactivo (hilos independientes de envío y recepción)
├── docker-compose.yml  # Orquestación del contenedor del servidor (puerto 5000, tty y stdin interactivo)
├── Dockerfile          # Imagen Docker basada en python:3.11-slim
├── requirements.txt    # Documentación de dependencias (biblioteca estándar)
├── Parcial1.pdf        # Documento oficial con las especificaciones del examen
└── README.md           # Guía de instalación, ejecución y pruebas
```

---

## 4. Requisitos Previos

- **Docker** y **Docker Compose** instalados en la máquina anfitriona.
- **Python 3.8+** instalado para ejecutar los clientes en las terminales de Visual Studio Code.
- *Nota:* No se requieren librerías externas de pip; el proyecto aprovecha al 100% los módulos estándar `socket` y `threading` de Python.

---

## 5. Instrucciones de Ejecución Paso a Paso

### Paso 1: Iniciar el Servidor en Docker

Abre una terminal en Visual Studio Code, colócate en la carpeta `Conjunta/` e inicia el servidor:

```bash
docker compose up --build
```

El servidor compilará la imagen e iniciará el socket TCP en el puerto `5000`:
```text
============================================================
          SERVIDOR DE CHAT DISTRIBUIDO (TCP + HILOS)
============================================================
[*] Servidor escuchando en 0.0.0.0:5000
[*] Esperando conexiones de CLIENTE 1 y CLIENTE 2...
============================================================
```

---

### Paso 2: Conectar el Cliente 1 (Terminal 2 de VS Code)

Abre una **segunda terminal independiente** en VS Code y ejecuta:

```bash
python cliente.py 1
```

Verás la confirmación de conexión:
```text
============================================================
          CHAT CONECTADO - PARTICIPANTE: [CLIENTE 1]
============================================================
[*] Conectado al servidor en localhost:5000
[*] Escribe tu mensaje y presiona Enter para enviar.
[*] Comunicación sin turnos: puedes escribir en cualquier momento.
[*] Escribe 'salir' para desconectarte.
============================================================
[CLIENTE 1]: 
```

---

### Paso 3: Conectar el Cliente 2 (Terminal 3 de VS Code)

Abre una **tercera terminal independiente** en VS Code y ejecuta:

```bash
python cliente.py 2
```

Verás la confirmación de conexión:
```text
============================================================
          CHAT CONECTADO - PARTICIPANTE: [CLIENTE 2]
============================================================
[*] Conectado al servidor en localhost:5000
[*] Escribe tu mensaje y presiona Enter para enviar.
[*] Comunicación sin turnos: puedes escribir en cualquier momento.
[*] Escribe 'salir' para desconectarte.
============================================================
[CLIENTE 2]: 
```

---

### Paso 4: Cómo Escribir Mensajes como [SERVIDOR]

Por diseño de Docker Compose v2, el comando `docker compose up` multiplexa los logs de salida y no redirige directamente las pulsaciones del teclado del anfitrión al contenedor. Para interactuar y enviar mensajes como `[SERVIDOR]` dispones de **tres alternativas 100% funcionales**:

#### Alternativa A: Desde una terminal en VS Code como [SERVIDOR] (Más fácil y recomendado)
Abre una terminal adicional en VS Code y ejecuta:
```bash
python cliente.py servidor
```
*(O ejecuta `python cliente.py` y presiona la opción `0`).*  
Esta terminal se identificará como `[SERVIDOR]`, permitiéndote escribir y enviar mensajes a todos los clientes como `[SERVIDOR]: <mensaje>`.

#### Alternativa B: Conectarse a la terminal del contenedor con `docker attach`
En cualquier terminal, ejecuta:
```bash
docker attach chat_servidor
```
Tu teclado se conectará directamente a la consola interna del contenedor. Escribe tu mensaje, presiona Enter y se difundirá como `[SERVIDOR]: <mensaje>`.

#### Alternativa C: Iniciar el servidor interactivo con `docker compose run`
En vez de `docker compose up`, puedes iniciar el servidor con:
```bash
docker compose run --rm --service-ports servidor
```
Esto asigna una TTY interactiva directa desde el inicio, permitiendo escribir en esa misma terminal.

---

## 6. Demostración y Pruebas de Funcionamiento

Para reproducir la conversación exacta descrita en la sección 2 del PDF:

1. **Desde Cliente 1 (Terminal 2):**  
   Escribe: `Hola a todos` y presiona Enter.
   - En Servidor aparece: `[CLIENTE 1]: Hola a todos`.
   - En Cliente 2 aparece: `[CLIENTE 1]: Hola a todos`.

2. **Desde Servidor (Terminal de Servidor):**  
   Escribe: `Hola cliente 1` y presiona Enter.
   - En Servidor aparece: `[SERVIDOR]: Hola cliente 1`.
   - En Cliente 1 aparece: `[SERVIDOR]: Hola cliente 1`.
   - En Cliente 2 aparece: `[SERVIDOR]: Hola cliente 1`.

3. **Desde Cliente 2 (Terminal 3):**  
   Escribe: `Buenos días` y presiona Enter.
   - Servidor y Cliente 1 reciben: `[CLIENTE 2]: Buenos días`.

4. **Desde Cliente 1 (Terminal 2):**  
   Escribe: `¿Cómo están?` y presiona Enter.
   - Servidor y Cliente 2 reciben: `[CLIENTE 1]: ¿Cómo están?`.

5. **Desde Cliente 2 (Terminal 3):**  
   Escribe: `Todo bien` y presiona Enter.
   - Servidor y Cliente 1 reciben: `[CLIENTE 2]: Todo bien`.

### Salida resultante en todas las terminales:
```text
[CLIENTE 1]: Hola a todos
[SERVIDOR]: Hola cliente 1
[CLIENTE 2]: Buenos días
[CLIENTE 1]: ¿Cómo están?
[CLIENTE 2]: Todo bien
```
