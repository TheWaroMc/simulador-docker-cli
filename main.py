import secrets
import shlex


class DockerSimulator:
    def __init__(self):
        self.images = {
            "demo/compra-libros:1.0": {
                "name": "demo/compra-libros:1.0",
                "description": "Demo de compra de libros usados.",
            }
        }
        self.containers = {}

    def run(self):
        print("Simulador Docker CLI. Escribe 'exit' para salir.")

        while True:
            try:
                command = input("docker> ").strip()
            except (EOFError, KeyboardInterrupt):
                print()
                break

            if not command:
                continue

            try:
                if not self.execute(command):
                    break
            except ValueError as error:
                print(f"Error: {error}")

    def execute(self, command):
        try:
            arguments = shlex.split(command)
        except ValueError as error:
            raise ValueError(f"comando inválido: {error}") from error

        if arguments == ["exit"]:
            return False

        if not arguments or arguments[0] != "docker" or len(arguments) < 2:
            print("Uso: docker <help|pull|images|run|ps|stop|rm|logs> (o 'exit')")
            return True

        action = arguments[1]
        values = arguments[2:]
        handlers = {
            "help": self._help,
            "pull": self._pull,
            "images": self._images,
            "run": self._run_container,
            "ps": self._ps,
            "stop": self._stop,
            "rm": self._remove,
            "logs": self._logs,
        }
        handler = handlers.get(action)
        if handler is None:
            print(f"Comando no soportado: docker {action}")
        else:
            handler(values)
        return True

    def _help(self, arguments):
        if arguments:
            raise ValueError("uso: docker help")

        print("""Simulador Docker CLI - Ayuda

Uso:
  docker <comando> [opciones]

Comandos:
  docker pull <imagen>
      Registra una imagen en la lista local del simulador.

    docker images
            Muestra las imagenes registradas en memoria.

  docker run [-d] [--name nombre] [-p host:contenedor] [-v origen:destino] <imagen>
      Crea e inicia un contenedor usando una imagen descargada.
      -d                 Acepta el modo detached; el contenedor queda en estado Up.
      --name nombre      Asigna un nombre unico. Si se omite, se genera uno.
      -p host:contenedor Guarda la configuracion del puerto en el contenedor.
      -v origen:destino  Guarda la configuracion del volumen en el contenedor.
      Puedes indicar -p y -v mas de una vez.

  docker ps
      Muestra los contenedores activos (estado Up).

  docker ps -a
  docker ps --all
      Muestra todos los contenedores, incluidos los detenidos.

  docker stop <id|nombre>
      Detiene un contenedor activo y cambia su estado a Exited.

  docker rm <id|nombre>
      Elimina un contenedor detenido. Primero usa docker stop si sigue activo.

  docker logs <id|nombre>
      Muestra un resumen simulado del estado del contenedor; no son logs reales.

  docker help
      Muestra esta ayuda.

  exit
      Sale del simulador.

Ejemplo:
    docker run -d --name compra-libros -p 8080:80 demo/compra-libros:1.0
  docker ps
    docker logs compra-libros
    docker stop compra-libros
    docker rm compra-libros

Notas:
    - La imagen demo/compra-libros:1.0 viene precargada para probar docker run.
    - Los nombres de imagen, contenedores y sus estados solo existen en memoria.
  - El simulador no descarga imagenes ni ejecuta Docker, publica puertos o monta volumenes.
  - Para docker run, la imagen debe haberse agregado antes con docker pull.""")

    def _pull(self, arguments):
        if len(arguments) != 1:
            raise ValueError("uso: docker pull <imagen>")

        image = arguments[0].lower()
        self.images[image] = {"name": image}
        print(f"Imagen {image} descargada.")

    def _images(self, arguments):
        if arguments:
            raise ValueError("uso: docker images")

        if not self.images:
            print("No hay imagenes.")
            return

        print(f"{'IMAGE':<32} DESCRIPTION")
        for image in self.images.values():
            print(f"{image['name']:<32} {image.get('description', '-')}")

    def _run_container(self, arguments):
        name = None
        ports = []
        volumes = []
        index = 0

        while index < len(arguments) and arguments[index].startswith("-"):
            option = arguments[index]
            if option == "-d":
                index += 1
            elif option in ("--name", "-p", "-v"):
                if index + 1 >= len(arguments):
                    raise ValueError(f"falta el valor para {option}")
                value = arguments[index + 1]
                if option == "--name":
                    name = value
                elif option == "-p":
                    ports.append(value)
                else:
                    volumes.append(value)
                index += 2
            else:
                raise ValueError(f"opción no soportada: {option}")

        if len(arguments) - index != 1:
            raise ValueError("uso: docker run [-d] [--name nombre] [-p puerto] [-v volumen] <imagen>")

        image = arguments[index].lower()
        if image not in self.images:
            raise ValueError(f"la imagen '{image}' no está descargada; usa docker pull primero")

        id_hash = secrets.token_hex(3)
        while id_hash in self.containers:
            id_hash = secrets.token_hex(3)

        name = name or f"container-{id_hash}"
        if any(container["name"] == name for container in self.containers.values()):
            raise ValueError(f"ya existe un contenedor con el nombre '{name}'")

        self.containers[id_hash] = {
            "id_hash": id_hash,
            "name": name,
            "image": image,
            "status": "Up",
            "ports": ports,
            "volumes": volumes,
        }
        print(f"Contenedor {name} ({id_hash}) iniciado.")
        description = self.images[image].get("description")
        if description:
            print(f"Aplicacion: {description}")

    def _ps(self, arguments):
        if arguments not in ([], ["-a"], ["--all"]):
            raise ValueError("uso: docker ps [-a]")

        show_all = bool(arguments)
        containers = [
            container
            for container in self.containers.values()
            if show_all or container["status"] == "Up"
        ]
        if not containers:
            print("No hay contenedores.")
            return

        print(f"{'CONTAINER ID':<14} {'IMAGE':<20} {'STATUS':<8} {'NAMES'}")
        for container in containers:
            print(
                f"{container['id_hash']:<14} {container['image']:<20} "
                f"{container['status']:<8} {container['name']}"
            )

    def _find_container(self, identifier):
        for container in self.containers.values():
            if identifier in (container["id_hash"], container["name"]):
                return container
        raise ValueError(f"no se encontró el contenedor '{identifier}'")

    def _stop(self, arguments):
        if len(arguments) != 1:
            raise ValueError("uso: docker stop <id|nombre>")

        container = self._find_container(arguments[0])
        if container["status"] == "Exited":
            raise ValueError(f"el contenedor '{container['name']}' ya está detenido")
        container["status"] = "Exited"
        print(f"Contenedor {container['name']} detenido.")

    def _remove(self, arguments):
        if len(arguments) != 1:
            raise ValueError("uso: docker rm <id|nombre>")

        container = self._find_container(arguments[0])
        if container["status"] == "Up":
            raise ValueError("detén el contenedor antes de eliminarlo")
        del self.containers[container["id_hash"]]
        print(f"Contenedor {container['name']} eliminado.")

    def _logs(self, arguments):
        if len(arguments) != 1:
            raise ValueError("uso: docker logs <id|nombre>")

        container = self._find_container(arguments[0])
        print(
            f"Contenedor {container['name']} ({container['image']}): "
            f"estado {container['status']}."
        )


if __name__ == "__main__":
    DockerSimulator().run()