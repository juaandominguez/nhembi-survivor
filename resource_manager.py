import json
import pygame, sys, os
from pygame.locals import *


# -------------------------------------------------
# Clase GestorRecursos

# En este caso se implementa como una clase vacía, solo con métodos de clase
class GestorRecursos(object):
    recursos = {}
            
    @classmethod
    def CargarImagen(cls, nombre, colorkey=None):
        # Si el nombre de archivo está entre los recursos ya cargados
        if nombre in cls.recursos:
            # Se devuelve ese recurso
            return cls.recursos[nombre]
        # Si no ha sido cargado anteriormente
        else:
            # Se carga la imagen indicando la carpeta en la que está
            fullname = os.path.join('imagenes', nombre)
            try:
                imagen = pygame.image.load(fullname)
            except pygame.error:
                raise SystemExit
            imagen = imagen.convert()
            if colorkey is not None:
                if colorkey is -1:
                    colorkey = imagen.get_at((0,0))
                imagen.set_colorkey(colorkey, RLEACCEL)
            # Se almacena
            cls.recursos[nombre] = imagen
            # Se devuelve
            return imagen

    @classmethod
    def CargarArchivoCoordenadas(cls, nombre):
        # Si el nombre de archivo está entre los recursos ya cargados
        if nombre in cls.recursos:
            # Se devuelve ese recurso
            return cls.recursos[nombre]
        # Si no ha sido cargado anteriormente
        else:
            # Se carga el recurso indicando el nombre de su carpeta
            fullname = os.path.join('imagenes', nombre)
            pfile=open(fullname,'r')
            datos=pfile.read()
            pfile.close()
            # Se almacena
            cls.recursos[nombre] = datos
            # Se devuelve
            return datos


    @classmethod
    def load_level(self, level_file):
        """ Carga los datos del nivel desde un archivo LDtk (JSON) """
        with open(level_file, 'r', encoding='utf-8') as f:
            project = json.load(f)  # Cargar archivo como JSON

        level_data_tileset = []
        level_data_decorations = []
        level_collisions = []

        # Obtener el primer nivel (o busca uno específico por nombre)
        level = project["levels"][0]

        # Buscar la capa de tiles
        for layer in level["layerInstances"]:
            if layer["__identifier"] == "Suelo_paredes" or layer["__identifier"] == "Muebles": 
                for tile in layer["gridTiles"]:
                    tile_x = tile["px"][0]  # Posición en píxeles (x)
                    tile_y = tile["px"][1]  # Posición en píxeles (y)
                    tile_src_x = tile["src"][0]  # Posición en el tileset (x)
                    tile_src_y = tile["src"][1]  # Posición en el tileset (y)
                    tile_id = tile["t"]  # ID del tile dentro del tileset

                    if layer["__identifier"] == "Suelo_paredes":
                        level_data_tileset.append((tile_x, tile_y, tile_src_x, tile_src_y, tile_id))
                    else:
                        level_data_decorations.append((tile_x, tile_y, tile_src_x, tile_src_y, tile_id))

            if layer["__identifier"] == "Collisions": # Verifica si la capa es "Collisions" (el identifador de ldtk para lo que se ve en el nivel)
                for tile in layer["gridTiles"]:
                    x = tile["px"][0]
                    y = tile["px"][1]
                    level_collisions.append(pygame.Rect(x, y, 1, 1))

        return level_data_tileset, level_data_decorations, level_collisions

