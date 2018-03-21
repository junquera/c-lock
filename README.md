# toc-toc-ssh

Port knocking based in TOTP.

## README

> https://guides.github.com/features/wikis/

- [ ] Project name: Your project’s name is the first thing people will see upon scrolling down to your README, and is included upon creation of your README file.

- [ ] Description: A description of your project follows. A good description is clear, short, and to the point. Describe the importance of your project, and what it does.

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

- [ ] Main en condiciones

- [x] Cerrar bien y matar threads

- [ ] Maqueta de instalador


## Atrribution

- By Micthev (Own work) [GFDL (http://www.gnu.org/copyleft/fdl.html) or CC BY-SA 4.0-3.0-2.5-2.0-1.0 (https://creativecommons.org/licenses/by-sa/4.0-3.0-2.5-2.0-1.0)], via Wikimedia Commons

https://commons.wikimedia.org/wiki/File:Clock_12-00.svg
