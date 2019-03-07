# Sniff

En lugar de escuchar con un socket, detectamos conexiones. Así evitamos "pisar puertos" y tenemos un sistema mucho más limpio.

El nuevo sistema tiene dos posibilidades:

- FT/SNIFF/O1: Estar al final de la lista de `iptables` y rechazar todas las conexiones (que no hayan sido aceptadas antes manualmente), hasta que alguien complete toda la secuencia, que podrá acceder a todo. También añadir puertos que se considere deber gestionar el sistema, pero dejándolos abiertos.

- FT/SNIFF/O2: Estar al principio y filtrar todas las peticiones a *n* puertos definidos al inicio del sistema.

- FT/SNIFF/03: Probar con NFQUEUE

Tengo que tirar de scapy en lugar del sniffer *artesanal* porque con el firewall el sniffer manual no recibe los paquetes (es un socket escuchando).

## TODO

- [x] Cambiar port manager

- [x] Set behaviour for multiple protected ports (in ttp)

- [ ] Cambiar reglas del firewall

  - [ ] Hacer que al arrancar, cierre los puertos a proteger en su propia chain

  - [ ] Hacer que al arrancar, abra los puertos especificados como abiertos

- [ ] Test
