CC = gcc
CFLAGS = -Wall -Wextra -O2
SRCDIR = src/c_bins
BINDIR = bin
PYTHON = python3

C_SRCS = $(wildcard $(SRCDIR)/*.c)
C_BINS = $(patsubst $(SRCDIR)/%.c, $(BINDIR)/%, $(C_SRCS))

.PHONY: all build run clean install distclean docs help

all: build

build: $(BINDIR) $(C_BINS)

$(BINDIR):
	mkdir -p $(BINDIR)

$(BINDIR)/%: $(SRCDIR)/%.c
	$(CC) $(CFLAGS) -o $@ $<

install:
	pip install -r requirements.txt

run: build
	$(PYTHON) src/python/main.py

clean:
	rm -rf $(BINDIR)
	find . -type d -name '__pycache__' -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name '*.pyc' -delete

distclean: clean
	rm -rf *.egg-info .pytest_cache

docs:
	@echo "Documentación en docs/"
	@ls docs/

help:
	@echo "=== LINUX ADMIN TOOL ==="
	@echo "make build     - Compilar binarios C"
	@echo "make install   - Instalar dependencias Python"
	@echo "make run       - Compilar y ejecutar la herramienta"
	@echo "make clean     - Limpiar archivos compilados"
	@echo "make docs      - Ver documentación"
