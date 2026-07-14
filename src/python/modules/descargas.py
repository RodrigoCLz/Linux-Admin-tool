import os
import json
import threading
import time
import datetime

DESCARGAS_DIR = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'descargas')
HISTORIAL_FILE = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'historial_descargas.json')

os.makedirs(DESCARGAS_DIR, exist_ok=True)

class Descarga:
    def __init__(self, url, destino=None, nombre=None):
        self.url = url
        self.destino = destino or DESCARGAS_DIR
        self.nombre = nombre or os.path.basename(url.split('?')[0]) or 'download'
        self.ruta = os.path.join(self.destino, self.nombre)
        self.estado = 'pendiente'
        self.progreso = 0.0
        self.velocidad = 0.0
        self.tamano_total = 0
        self.tamano_descargado = 0
        self.error = None
        self._thread = None
        self._cancel = False
        self._pause = False
        self.inicio = None
        self.fin = None

    def _run(self, callback=None):
        self.inicio = datetime.datetime.now()
        self.estado = 'descargando'
        try:
            import urllib.request
            req = urllib.request.Request(self.url, headers={
                'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64)'
            })
            with urllib.request.urlopen(req, timeout=30) as response:
                total = int(response.headers.get('Content-Length', 0))
                self.tamano_total = total
                self.tamano_descargado = 0
                chunk_size = 8192
                start_time = time.time()
                downloaded = 0

                os.makedirs(self.destino, exist_ok=True)
                with open(self.ruta + '.part', 'wb') as f:
                    while True:
                        if self._cancel:
                            self.estado = 'cancelado'
                            if os.path.exists(self.ruta + '.part'):
                                os.remove(self.ruta + '.part')
                            if callback:
                                callback(self)
                            _guardar_historial_descarga(self)
                            return

                        while self._pause:
                            if self._cancel:
                                self.estado = 'cancelado'
                                if os.path.exists(self.ruta + '.part'):
                                    os.remove(self.ruta + '.part')
                                if callback:
                                    callback(self)
                                _guardar_historial_descarga(self)
                                return
                            time.sleep(0.1)

                        chunk = response.read(chunk_size)
                        if not chunk:
                            break
                        f.write(chunk)
                        self.tamano_descargado += len(chunk)
                        downloaded += len(chunk)

                        elapsed = time.time() - start_time
                        if elapsed > 0:
                            self.velocidad = downloaded / elapsed
                        if total > 0:
                            self.progreso = (self.tamano_descargado / total) * 100

                os.rename(self.ruta + '.part', self.ruta)
                self.estado = 'completado'
                self.progreso = 100.0
        except Exception as e:
            self.estado = 'error'
            self.error = str(e)
            if os.path.exists(self.ruta + '.part'):
                os.remove(self.ruta + '.part')

        self.fin = datetime.datetime.now()
        if callback:
            callback(self)
        _guardar_historial_descarga(self)

    def iniciar(self, callback=None):
        self._thread = threading.Thread(target=self._run, args=(callback,), daemon=True)
        self._thread.start()

    def cancelar(self):
        self._cancel = True

    def pausar(self):
        self._pause = True
        self.estado = 'pausado'

    def reanudar(self):
        self._pause = False
        self.estado = 'descargando'

    def to_dict(self):
        return {
            'url': self.url,
            'nombre': self.nombre,
            'ruta': self.ruta,
            'destino': self.destino,
            'estado': self.estado,
            'tamano_total': self.tamano_total,
            'tamano_descargado': self.tamano_descargado,
            'error': self.error,
            'inicio': self.inicio.isoformat() if self.inicio else None,
            'fin': self.fin.isoformat() if self.fin else None,
        }


_descargas_activas = []

def _cargar_historial():
    try:
        if os.path.exists(HISTORIAL_FILE):
            with open(HISTORIAL_FILE, 'r') as f:
                return json.load(f)
    except (json.JSONDecodeError, IOError):
        pass
    return []

def _guardar_historial_descarga(descarga):
    hist = _cargar_historial()
    hist.append(descarga.to_dict())
    try:
        with open(HISTORIAL_FILE, 'w') as f:
            json.dump(hist[-200:], f, indent=2)
    except IOError:
        pass

def nueva_descarga(url, destino=None, nombre=None, callback=None):
    d = Descarga(url, destino, nombre)
    _descargas_activas.append(d)
    d.iniciar(callback)
    return d

def listar_descargas_activas():
    return _descargas_activas

def listar_historial():
    return _cargar_historial()

def limpiar_historial():
    try:
        with open(HISTORIAL_FILE, 'w') as f:
            json.dump([], f)
    except IOError:
        pass
    return "Historial de descargas limpiado"
