# -*- encoding: utf-8 -*-

ANCHO_PANTALLA = 800
ALTO_PANTALLA = 600

# -------------------------------------------------
# Clase Escena con lo metodos abstractos

class Scene:

    def __init__(self, director, screen):
        self.director = director
        self.screen = screen

    def update(self, *args):
        raise NotImplementedError("You need to implement the method update.")

    def events(self, *args):
        raise NotImplementedError("You need to implement the method events.")

    def render(self, screen):
        raise NotImplementedError("You need to implement the method dibujar.")

    def on_enter(self):
        raise NotImplementedError("You need to implement the method on enter.")

    def on_exit(self):
        raise NotImplementedError("You need to implement the method on enter.")
