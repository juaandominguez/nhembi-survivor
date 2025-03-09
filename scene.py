# -*- encoding: utf-8 -*-

ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600

# -------------------------------------------------
# Clase Escena con lo metodos abstractos

class Scene:

    def __init__(self, director):
        self.director = director

    def update(self, *args):
        raise NotImplementedError("Tiene que implementar el metodo update.")

    def handle_events(self, *args):
        raise NotImplementedError("Tiene que implementar el metodo eventos.")

    def render(self, screen):
        raise NotImplementedError("Tiene que implementar el metodo dibujar.")
