# toc-toc-ssh

Ssh port knocking based in TOTP

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

### URGENTE - Para versión 0.0.1 (alpha-1)

- [ ] README

- [ ] Arg parser

- [ ] Main en condiciones

- [x] Cerrar bien y matar threads

- [ ] Maqueta de instalador
