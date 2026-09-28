# Simulador Docker CLI

Simulador interactivo de algunos comandos basicos de Docker. No necesita Docker instalado y no ejecuta contenedores reales: las imagenes y los contenedores se guardan en memoria mientras el programa esta abierto.

## Requisitos e inicio

Necesitas Python 3. Desde la carpeta del proyecto, inicia el REPL con:

```powershell
py main.py
```

En otros sistemas, puedes usar `python3 main.py` o `python main.py`, segun como este instalado Python.

Cuando aparezca `docker>`, escribe los comandos del simulador. Para salir, escribe `exit`.

## Crear y ver imagenes

La imagen `demo/compra-libros:1.0` viene precargada. Puedes verla con:

```text
docker images
```

Para registrar otra imagen de prueba en la sesion actual:

```text
docker pull nginx:latest
docker images
```

En este simulador, `docker pull` no descarga nada de Internet: agrega el nombre de imagen al diccionario en memoria. La imagen desaparece al cerrar el programa. Para precargar imagenes propias, agrega entradas al diccionario `self.images` en `DockerSimulator.__init__` dentro de `main.py`, usando `name` y, opcionalmente, `description`.

## Crear y administrar contenedores

Ejemplo con la imagen de compra de libros que ya viene incluida:

```text
docker run -d --name compra-libros -p 8080:80 demo/compra-libros:1.0
docker ps
docker logs compra-libros
docker stop compra-libros
docker ps -a
docker rm compra-libros
```

`docker run` requiere una imagen registrada. Acepta `-d`, `--name`, `-p` y `-v`; los puertos y volumenes se guardan como datos, pero no se publican ni se montan en el sistema. `-d` se acepta como opcion, aunque no cambia el comportamiento del simulador.

Cada contenedor recibe un ID hexadecimal de 6 caracteres y comienza con estado `Up`. `docker stop` cambia su estado a `Exited`. Solo se puede eliminar con `docker rm` despues de detenerlo. Puedes identificarlo por ID o por nombre.

## Comandos disponibles

| Comando | Funcion |
| --- | --- |
| `docker help` | Muestra la ayuda del REPL. |
| `docker pull <imagen>` | Registra una imagen de prueba en memoria. |
| `docker images` | Lista las imagenes registradas. |
| `docker run [opciones] <imagen>` | Crea un contenedor en estado `Up`. |
| `docker ps` | Lista contenedores activos. |
| `docker ps -a` | Lista todos los contenedores, incluidos los detenidos. |
| `docker stop <id|nombre>` | Cambia un contenedor activo a estado `Exited`. |
| `docker rm <id|nombre>` | Elimina un contenedor detenido. |
| `docker logs <id|nombre>` | Muestra un resumen simulado, no logs reales. |
| `exit` | Cierra el simulador. |

Los datos no se guardan entre ejecuciones. El simulador no construye imagenes con Dockerfiles ni ejecuta `docker build`.
