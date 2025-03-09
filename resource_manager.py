import json
import pygame, sys, os
from pygame.locals import *


# -------------------------------------------------
# Clase GestorRecursos

# En este caso se implementa como una clase vacía, solo con métodos de clase
class ResourceManager:
    resources = {}

    @classmethod
    def loadImage(cls, name):
        if name in cls.resources:
            return cls.resources[name]
        else:
            fullname = os.path.join("sprites", name)
            try:
                image = pygame.image.load(fullname)
            except pygame.error as message:
                print("Cannot load image:", fullname)
                raise SystemExit(message)
            image = image.convert_alpha()
            cls.resources[name] = image
            return image

    @classmethod
    def loadCoordinates(cls, name):
        if name in cls.resources:
            return cls.resources[name]
        else:
            fullname = os.path.join("sprites", name)
            with open(fullname, "r") as pfile:
                data = pfile.read()
            cls.resources[name] = data
            return data


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