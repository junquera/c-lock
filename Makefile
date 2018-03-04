all: build_dir
	gcc *.c -Wall -lcrypto -lssl -o build/totp

build_dir:
	mkdir -p build
