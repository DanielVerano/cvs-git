# CVS (Concurrent Version System)

## Propósito del repositorio
1º Montar un servidor cvs (se puede usar docker)

2º Investigar como crear un repositorio cvs, tras ello crearlo

3º Darle contenido ha dicho repositorio (se recomiendan hacer commits)

4º Investigar como funciona la herramienta cvs-fast-export

5º Instalarse cvs-fast-export (no vale con apt install pues la versión de los repositorios es antigua. Se recomienda descargarse el codigo del repositorio oficial y compilarlo)

6º Instalar gitlab en docker (edicio ce). Se recomienda usar docker-compose.

7º Migrar el repositorio de cvs a git

8º Automatizar el séptimo paso con un script de python. Al lanzar este script se debe crear un repositorio en el gitlab y subir el repositorio migrado. Los parámetros de este script pueden ser los que queráis.

9º Documentación del proceso.

## Requisitos
1. Dos máquinas virtuales (las distribuciones elegidas para esta práctica son):
- Ubuntu Server 22.04 (Servidor)
- Ubuntu Desktop 20.04 (Cliente)

## Pasos

## 1. Montar un Servidor CVS
1. Instalar las dependencias necesarias en el servidor:
```sh
sudo apt install cvs xinetd
```

## 2. Crear un repositorio CVS
2. Inicializar un repositorio CVS:
```sh
sudo cvs -d /usr/local/projecto1 init
```

3. Configuramos los permisos necesarios en la carpeta del repositorio:
```sh
sudo chown -R :cvs /usr/local/projecto1/
sudo chmod -R g+ws /usr/local/projecto1/
```
![cap5](/images/cap-5.PNG)

4. Editar el archivo /etc/xinetd.d/cvspserver
```sh
sudo bash -c 'cat >> /etc/xinetd.d/cvspserver << "EOF"
service cvspserver
{
    port        = 2401
    socket_type = stream
    protocol    = tcp
    wait        = no
    user        = root
    passenv     = PATH
    server      = /usr/bin/cvs
    server_args = -f --allow-root=<ruta_del_repositorio> pserver
    bind        = <ip_del_servidor>
}
EOF'
```
![cap1](/images/cap-1.PNG)

5. Reiniciamos el servicio de pserver:
```sh
sudo systemctl restart xinetd.service
```

6. Comprobamos que el servicio se está ejecutando y escuchando correctamente
```sh
netstat -ntlp | grep 2401
```
![cap2](/images/cap-2.PNG)

7. Creamos un nuevo usuario con el que nos conectaremos después al repositorio
```sh
sudo useradd <usuario>
sudo passwd <usuario>
```
![cap3](/images/cap-3.PNG)

8. Lo añadimos al grupo cvs para darle permisos de acceso:
```sh
sudo usermod -a -G cvs cvsuser
```

8. Desde la máquina cliente, realizamos los siguientes pasos:
    - Instalamos cvs
    - Creamos la variable CVSROOT necesaria para poder conectarnos al servidor
    - Nos logueamos y hacemos un checkout de los archivos actuales
```sh
sudo apt install cvs
export CVSROOT=:pserver:<usuario>@<ip_servidor>:<ruta_repositorio>
cvs login
```
![cap6](/images/cap-6.PNG)

- Para no tener que exportar la variable CVSROOT cada vez que queramos conectarnos al servidor, la exportamos permanentemente al .bashrc
```sh
echo 'export CVSROOT=:pserver:cvsuser@192.168.82.3:2401/usr/local/projecto1' >> ~/.bashrc
```

## 3. Darle contenido al repositorio
1. Importamos un nuevo módulo (directorio) que será la raíz del projecto
```sh
cvs import -m "Import inicial" <nombre_modulo> <autor> <rama>
```

2. Después de realizar el import, hacemos un cvs checkout del módulo anterior para ir registrando los cambios que hagamos
```sh
cvs checkout myapp
```

3. Para añadir nuevos archivos, usamos el comando cvs add, especificando un mensaje de manera opcional
```sh
cvs add index.html -m "archivo index.html"
```

4. Si hemos realizado modificaciones a algunos archivos, para hacer un commit de esos cambios al repositorio usamos el comando cvs commit
```sh
cvs commit
```

## 4 y 5. Instalación de la herramienta cvs-fast-export
1. Clonamos el repositorio del projecto
```sh
https://gitlab.com/esr/cvs-fast-export.git
```

2. Instalamos las dependencias necesarias antes de compilar la aplicación
```sh
sudo ./buildprep
```

3. Es posible que necesitemos otra dependencia adicional, la instalamos con este comando:
```sh
sudo apt install asciidoc-base
```

3. Compilamos la herramienta
```sh
make
```

4. Una vez compilada, la instalamos en nuestro equipo
```sh
sudo make install
```

5. Nos situamos en la raíz del projecto que queremos migrar y ejecutamos el siguiente comando:
```sh
find . | cvs-fast-export > ~/stream.fe
```

## 6. Instalación de Gitlab en Docker
1. Primero, instalamos Docker siguiendo los pasos de la [documentación oficial](https://docs.docker.com/engine/install/ubuntu/#install-using-the-repository)

2. (Opcional) Para no tener que ejecutar los comandos de docker con sudo, seguimos [estos pasos](https://docs.docker.com/engine/install/linux-postinstall/)

3. Ahora, procedemos a instalar Gitlab mediante Docker siguiendo su documentación oficial. Utilizaremos el método de [docker-compose](https://docs.gitlab.com/ee/install/docker.html#install-gitlab-using-docker-compose)

4. Ejecutamos el [docker-compose.yaml](/docker-compose.yaml) del repositorio mediante el comando
```sh
docker compose up -d
```

5. Accedemos a la página de inicio desde el navegador especificando la IP del servidor y el puerto, poniendo como usuario root y la contraseña la sacamos con este comando
```sh
docker exec -it gitlab-web-1 grep 'Password:' /etc/gitlab/initial_root_password
```
![cap-9](/images/cap-9.PNG)


## 7. Migrar el repositorio de cvs a git
1. Creamos la carpeta que será la raíz del repositorio migrado
```sh
mkdir repositorio && cd repositorio
```

2. Iniciamos un nuevo repositorio git
```sh
git init
```

3. Importamos el repositorio cvs a partir del archivo creado anteriormente (stream.fe)
```sh
git fast-import < ~/stream.fe
```
![cap-7](/images/cap-7.PNG)

4. Ya tendríamos importados todas las ramas y commits, pero el comando no extrae los propios archivos del repositorio, para ello ejecutamos el comando:
```sh
git checkout -f
```
![cap-8](/images//cap-8.PNG)

## 8. Automatización del proceso con un script de Python
1. Para que el script de Python funcione correctamente, antes necesitamos crear una clave SSH para autenticarnos con Gitlab. En esta práctica, vamos a crear una clave ED25519, siguiendo los pasos de la [documentación oficial](https://docs.gitlab.com/ee/user/ssh.html) de Gitlab
```sh
ssh-keygen -t ed25519 -C '<comentario>'
```

2. El comando anterior ha generado una clave privada y pública en el directorio /home/[usuario]/.ssh. Copiamos el contenido del archivo 'id_ed25519.pub'
```sh
cat ~/.ssh/id_ed25519.pub
```

3. Desde Gitlab, nos vamos a Preferences > SSH Keys y añadimos nuestra clave pública
![cap-11](/images//cap-10.png)

4. Por último, ejecutamos el script y comprobamos que el repositorio se ha subido a Gitlab
```sh
python3 script.py
```

![cap-12](/images//cap-11.PNG)