# TODO

- [ ] Make it work with previous/next time slots for clock issues.

- [ ] Al capturar error fatal, limpiar las reglas y dejar abierto el puerto de destino

- [ ] El valor del último puerto tiene que estar en el manejador del resto de módulos, en TocTocPorts tiene que entrar sólo como un puerto prohibido.

- [ ] Refactor

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

- [ ] Hacer como servicio

- [ ] Asegurar cierre (y sobre todo, limpieza de las iptables). Se puede hacer un proceso que compruebe que está corriendo.

- [ ] Servidor web con configuración, generación de bidi para secreto...

- [ ] Cómo evitar segmentation fault.

### Para versión 0.0.1 (alpha-1)

- [x] README

- [x] Arg parser

- [x] Main en condiciones

- [x] Cerrar bien y matar threads

- [x] Correct XTABLES dir

- [x] Test in vm

- [ ] Select address in port_manager y firewall_manager

- [x] Opción en server de limpiar iptables

- [ ] Crear un buen sistema para los thread

### Para versión 0.0.2 (alpha-2)

- [ ] YAML config

- [ ] Lista de puertos destino

- [ ] Configuración de tiempo de apertura para puertos destino.

- [ ] Maqueta de instalador (Makefile, config...)

<!-- ## Atrribution

- By Micthev (Own work) [GFDL (http://www.gnu.org/copyleft/fdl.html) or CC BY-SA 4.0-3.0-2.5-2.0-1.0 (https://creativecommons.org/licenses/by-sa/4.0-3.0-2.5-2.0-1.0)], via Wikimedia Commons

https://commons.wikimedia.org/wiki/File:Clock_12-00.svg -->
