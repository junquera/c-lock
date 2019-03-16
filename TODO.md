# TODO

- [ ] toc-toc-ssh -> c-lock

- [ ] https://codecov.io/

- [ ] Travis badge

- [ ] Snyk o pyup

- [ ] En TocTocPorts sólo queremos los puertos actuales

- [ ] ¿Centralizar eventos?

- [x] Ajustar a RFC-6238

- [ ] Colas para poder comunicarse con comandos (por ejemplo, para dejar abierto un puerto) (`feature/queue`, refered in `feature/snif`)

  - [ ] Que todo guarde relación con los eventos de ProcWorker

- [ ] Añadir compatibilidad con tokens de Google Authenticator

  - [x] Not use secret to allow pin generation in ttp.gen_ports

  - [x] Ver tamaño de clave de Authenticator para generarla igual

  - [ ] Tratar de generar bidi por consola

  - [x] Toc by pin

  Cambiado hotp después de recibir valor `totp` por random con semilla

- [ ] Al capturar error fatal, limpiar las reglas y dejar abierto el puerto de destino

- [ ] Refactor

  - [ ] Organización del proyecto: https://python-packaging.readthedocs.io/en/latest/command-line-scripts.html

  - [ ] Limpiar tests: https://docs.pytest.org/en/latest/contents.html

  - [ ] Buenas prácticas empaquetado: https://blog.ionelmc.ro/2014/05/25/python-packaging/#the-structure

  - [ ] Configurar bien travis (y gitlab ci): https://docs.travis-ci.com/user/tutorial/


- [ ] Best practices in logging: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/

- [ ] See YAML or JSON config file: https://fangpenlin.com/posts/2012/08/26/good-logging-practice-in-python/

- [ ] Cerrar todos los thread

- [ ] Intentar mejorar todos los hilos (en especial, los de sockets)

- [ ] Worker events -> Self file

- [x] Varios puertos destino (por ejemplo, sistema web, db...)

- [ ] Clase orquestador

- [ ] Extraer método lock de asíncronos

- [ ] Hacer como servicio

- [ ] Asegurar cierre (y sobre todo, limpieza de las iptables). Se puede hacer un proceso que compruebe que está corriendo.

- [ ] Cómo evitar segmentation fault.

- [ ] Time with NTP

- [ ] Project reestructure

### Para versión 0.0.2 (alpha-2)

- [ ] Select interface in firewall_manager

- [ ] Intentar mejorar el sistema de threads

- [ ] YAML config

- [ ] Lista de puertos destino

- [ ] Configuración de tiempo de apertura para puertos destino.

- [ ] Maqueta de instalador (Makefile, config...)

<!-- ## Atrribution

- By Micthev (Own work) [GFDL (http://www.gnu.org/copyleft/fdl.html) or CC BY-SA 4.0-3.0-2.5-2.0-1.0 (https://creativecommons.org/licenses/by-sa/4.0-3.0-2.5-2.0-1.0)], via Wikimedia Commons

https://commons.wikimedia.org/wiki/File:Clock_12-00.svg -->
