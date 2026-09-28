# Simulador Docker CLI

Simulador interactivo de algunos comandos basicos de Docker. No necesita Docker instalado y no ejecuta contenedores reales: las imagenes y los contenedores se guardan en memoria mientras el programa esta abierto.

## Requisitos e inicio

Necesitas Python 3. Desde la carpeta del proyecto, inicia el REPL con:

```powershell
py main.py
```

En otros sistemas, puedes usar `python3 main.py` o `python main.py`, segun como este instalado Python.

Cuando aparezca `docker>`, escribe los comandos del simulador. Para salir, escribe `exit`.
En ese prompt puedes omitir el prefijo `docker`: se aceptan tanto `run ...` como `docker run ...`.

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

Los nombres de imagen se normalizan a minusculas. Por ejemplo, `docker pull Warito` registra `warito`, que puedes iniciar con `docker run warito`.

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

Cada contenedor recibe un ID hexadecimal de 6 caracteres y comienza con estado `Up`. `docker stop` cambia su estado a `Exited`. El comando `docker rm` normal requiere que este detenido; `docker rm -f` tambien elimina contenedores activos. Puedes identificarlo por ID o por nombre.

## Referencia de comandos

### Ayuda y salida

| Comando | Que hace |
| --- | --- |
| `docker help` | Muestra la sintaxis, las opciones y un ejemplo. No admite argumentos adicionales. |
| `exit` | Termina el REPL. Tambien puedes usar `Ctrl+C` o `Ctrl+Z` para salir. |

### Imagenes

| Comando | Que hace | Detalles |
| --- | --- | --- |
| `docker pull <imagen>` | Registra una imagen en memoria. | Acepta un nombre, por ejemplo `docker pull Warito`. El simulador lo normaliza a `warito`; no descarga desde Internet. |
| `docker images` | Lista las imagenes registradas. | Muestra el nombre y la descripcion cuando existe. No acepta opciones. |

### Contenedores

#### Crear un contenedor

```text
docker run [-d] [--name nombre] [-p host:contenedor] [-v origen:destino] <imagen>
```

Crea e inicia un contenedor a partir de una imagen registrada. Genera un ID hexadecimal de 6 caracteres y asigna el estado `Up`. Si omites `--name`, genera un nombre automaticamente.

Opciones aceptadas:

- `-d`: se acepta, pero no cambia el comportamiento del simulador.
- `--name nombre`: asigna un nombre unico al contenedor.
- `-p host:contenedor`: guarda la configuracion del puerto; no publica puertos realmente.
- `-v origen:destino`: guarda la configuracion del volumen; no monta archivos realmente.

Puedes repetir las opciones `-p` y `-v`.

#### Listar contenedores activos

```text
docker ps
```

Muestra unicamente los contenedores con estado `Up`.

#### Listar todos los contenedores

```text
docker ps -a
```

Tambien puedes usar `docker ps --all`. Ambos comandos incluyen los contenedores activos y los detenidos (`Exited`).

#### Detener un contenedor

```text
docker stop <id|nombre>
```

Cambia el estado de `Up` a `Exited`. Sustituye `<id|nombre>` por el ID o el nombre del contenedor. No se puede detener otra vez un contenedor que ya esta detenido.

#### Eliminar un contenedor

```text
docker rm [-f] <id|nombre>
```

Elimina un contenedor detenido. Si sigue activo, primero ejecuta `docker stop` o agrega `-f` para forzar la eliminacion. Por ejemplo, `docker rm -f compra-libros` elimina el contenedor por nombre aunque este activo.

#### Consultar los logs

```text
docker logs <id|nombre>
```

Muestra un resumen simulado del nombre, la imagen y el estado; no son logs reales.

Los cambios se pierden al salir del programa; el simulador no ejecuta Docker ni construye imagenes con Dockerfiles.
