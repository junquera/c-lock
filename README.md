# toc-toc-ssh

A TOTP based port knocking service. Every time slot, it generates a sequence of ports that must be *knocked* (in a correct order) before the final port (it have been designed for protecting a SSH service) becames opened.

<!-- https://dashboard.moovly.com -->

## Table of Contents



## Installation

### System dependencies

This is the software with wich I have worked:

- python 3.x

- iptables >= v1.6

It has been tested in *Ubuntu 16.04* and *Debian 9*, but should work with any other system with theese systems installed.

### Software dependencies

As it is just an alpha version, it has no currently an automated installer, because until it comes debugged and improved, it shouldnt have yet integration with the system.

For install dependencies there are two options:

- **Option A**: requeriments.txt

```bash
pip3 install -r requeriments.txt
```

- **Option B**: [Pipenv](https://github.com/pypa/pipenv) (*Recommended*)

```bash
pip3 install pipenv
pipenv install -r requeriments.txt
```

## Usage

First of all, you need to get a secret for initialize the TOTP system:

```
$ python3 server.py --gen-secret
TOTP Secret: 12e76644abf4eb34cf3d163fa058332c610d80d7cbe5b069ee081fb2430126253563b03836b6e1a1
```

Then you can run `server.py` with this secret.

### Server

Must be launch as root (for managing the *iptables* rules):

```
usage: server.py [-h] [-ts SLOT] [-f FORBIDDEN [FORBIDDEN ...]] [-a ADDRESS]
                 [-s SECRET] [-p PROTECTED_PORT] [--gen-secret]
                 [--clean-firewall] [--log-level LOG_LEVEL]

Launch TOTP based port knocking protection

optional arguments:
  -h, --help            show this help message and exit
  -ts SLOT, --time-slot SLOT
                        Time slot for TOTP
  -f FORBIDDEN [FORBIDDEN ...], --forbidden FORBIDDEN [FORBIDDEN ...]
                        Ports already in use or not manageable (space
                        separated)
  -a ADDRESS, --address ADDRESS
                        Address to protect
  -s SECRET, --secret SECRET
                        Secret part of TOTP
  -p PROTECTED_PORT, --protected-port PROTECTED_PORT
                        Port which has to be protected
  --gen-secret          Generate random secret
  --clean-firewall      Clean firewall configuration (e.g., after a bad close)
  --log-level LOG_LEVEL
                        Log level
```

The most simple usage is:

```
$ sudo python3 server.py -s 12e76644abf4eb34cf3d163fa058332c610d80d7cbe5b069ee081fb2430126253563b03836b6e1a1

2018-03-25 13:27:20,831 - __main__ - DEBUG - Secret: 12e76644abf4eb34cf3d163fa058332c610d80d7cbe5b069ee081fb2430126253563b03836b6e1a1
2018-03-25 13:27:20,907 - firewall_manager - DEBUG - Starting FirewallManager
2018-03-25 13:27:20,912 - ttp - DEBUG - Next slot in 10s
2018-03-25 13:27:20,912 - port_manager - DEBUG - First port: 8289
2018-03-25 13:27:20,913 - port_manager - INFO - Opening 8289
2018-03-25 13:27:20,913 - port_manager - INFO - Opening 3913
2018-03-25 13:27:20,913 - firewall_manager - INFO - Opening first port 8289
2018-03-25 13:27:20,914 - port_manager - INFO - Opening 4852
2018-03-25 13:27:20,915 - port_manager - INFO - Opening 6218
2018-03-25 13:27:20,915 - firewall_manager - DEBUG - Adding rule 23c8aae9-31d3-4cc6-a50d-9f14bc9eccf1 -> <iptc.ip4tc.Rule object at 0x7fcacd6b6940>
```

### Client

```
usage: client.py [-h] [-ts SLOT] [-a ADDRESS] -s SECRET

Launch TOTP based port knocking protection

optional arguments:
  -h, --help            show this help message and exit
  -ts SLOT, --time-slot SLOT
                        Time slot for TOTP
  -a ADDRESS, --address ADDRESS
                        Address to knock
  -s SECRET, --secret SECRET
                        Secret part of TOTP
```

## Examples

This is how it shows when a client interacts with the server:

![Working example](img/working_example.png)

## Contributing



## Credits



## License

```
MIT License

Copyright (c) 2018 Javier Junquera Sánchez

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## README

> https://guides.github.com/features/wikis/

- [ ] Project name: Your project’s name is the first thing people will see upon scrolling down to your README, and is included upon creation of your README file.

- [x] Description: A description of your project follows. A good description is clear, short, and to the point. Describe the importance of your project, and what it does.

- [ ] Table of Contents: Optionally, include a table of contents in order to allow other people to quickly navigate especially long or detailed READMEs.

- [ ] Installation: Installation is the next section in an effective README. Tell other users how to install your project locally. Optionally, include a gif to make the process even more clear for other people.

- [ ] Usage: The next section is usage, in which you instruct other people on how to use your project after they’ve installed it. This would also be a good place to include screenshots of your project in action.

- [ ] Contributing: Larger projects often have sections on contributing to their project, in which contribution instructions are outlined. Sometimes, this is a separate file. If you have specific contribution preferences, explain them so that other developers know how to best contribute to your work. To learn more about how to help others contribute, check out the guide for setting guidelines for repository contributors.

- [ ] Credits: Include a section for credits in order to highlight and link to the authors of your project.

- [ ] License: Finally, include a section for the license of your project. For more information on choosing a license, check out GitHub’s licensing guide!

## TODO

- [ ] Write this document!

- [ ] Make it work with previous/next slots for clock issues.

- [ ] Al capturar error fatal, limpiar las reglas y dejar abierto el puerto de destino

- [ ] El valor del último puerto tiene que estar en el manejador del resto de módulos, en TocTocPorts tiene que entrar sólo como un puerto prohibido.

- [ ] Best practices in logging: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/

- [ ] See YAML or JSON config file: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/

- [ ] Cerrar todos los thread

- [ ] Cuando un puerto está ocupado: ¿Esperamos al siguiente slot o matamos el proceso?

- [ ] Intentar mejorar todos los hilos (en especial, los de sockets)

- [ ] Worker events -> Self file

- [ ] Varios puertos destino (por ejemplo, sistema web, db...)

- [ ] Hacer método de limpieza de mis reglas de IPTABLES

- [ ] Clase orquestador

- [ ] Extraer método lock de asíncronos

- [ ] Asegurar cierre (y sobre todo, limpieza de las iptables)

### URGENTE - Para versión 0.0.1 (alpha-1)

- [ ] README

- [x] Arg parser

- [x] Main en condiciones

- [x] Cerrar bien y matar threads

- [ ] Maqueta de instalador

- [ ] Correct XTABLES dir

- [ ] Test in vm

## Atrribution

- By Micthev (Own work) [GFDL (http://www.gnu.org/copyleft/fdl.html) or CC BY-SA 4.0-3.0-2.5-2.0-1.0 (https://creativecommons.org/licenses/by-sa/4.0-3.0-2.5-2.0-1.0)], via Wikimedia Commons

https://commons.wikimedia.org/wiki/File:Clock_12-00.svg
