# toc-toc-ssh

A TOTP based port knocking service. Every time slot, it generates a sequence of ports that must be *knocked* (in a correct order) before the final port (it have been designed for protecting a SSH service) becames opened.

<!-- https://dashboard.moovly.com -->

![TTS Process](img/tts-process.gif)

> Yeah, I'm not very good with graphics...

## Table of Contents



## Installation

### System dependencies

This is the software with wich I have worked:

- `python 3.x`

- `iptables >= v1.6`

It has been tested in *Ubuntu 16.04* and *Debian 9*, but should work with any other system with theese systems installed.

### Software dependencies

As it is just an alpha version, it has no currently an automated installer, because until it comes debugged and improved, it shouldnt have yet integration with the system.

Because `python-cryptography` is needed for some dependencies, it must be installed before anything else: [Building cryptography on linux](https://cryptography.io/en/latest/installation/#building-cryptography-on-linux)

For install dependencies there are two options:

- **Option A**: [Pipenv](https://github.com/pypa/pipenv) (*Recommended*)

```bash
pip3 install pipenv
pipenv install -r requeriments.txt
```

- **Option B**: requeriments.txt

```bash
pip3 install -r requeriments.txt
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
usage: client.py [-h] [-ts SLOT] -a ADDRESS -s SECRET

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

By now, and until I finish a first stable version, I want to control the code. The best way of contribute to this project is apporting ideas and reviewing code. Any help is welcome!

For example, its obvious that I need help with documentation images, design, logo... :blush:
<!-- ## Credits -->

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
