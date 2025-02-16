import json
import pygame

class Level:
    def __init__(self, level_file, level_tileset):
        """ Carga el nivel desde un archivo LDtk y usa un tileset """
        self.tileset_image = pygame.image.load(level_tileset).convert_alpha()
        self.tile_size = 16  # Tamaño de los tiles en píxeles
        self.level_data = self.load_level(level_file)  # Cargar datos del nivel desde LDtk

    def load_level(self, level_file):
        """ Carga los datos del nivel desde un archivo LDtk (JSON) """
        with open(level_file, 'r', encoding='utf-8') as f:
            project = json.load(f)  # Cargar archivo como JSON

        level_data = []

        # Obtener el primer nivel (o busca uno específico por nombre)
        level = project["levels"][0]

        # Buscar la capa de tiles
        for layer in level["layerInstances"]:
            if layer["__type"] == "Tiles":  # Verifica si la capa es de tipo "Tiles"
                for tile in layer["gridTiles"]:
                    tile_x = tile["px"][0]  # Posición en píxeles (x)
                    tile_y = tile["px"][1]  # Posición en píxeles (y)
                    tile_src_x = tile["src"][0]  # Posición en el tileset (x)
                    tile_src_y = tile["src"][1]  # Posición en el tileset (y)
                    tile_id = tile["t"]  # ID del tile dentro del tileset

                    level_data.append((tile_x, tile_y, tile_src_x, tile_src_y, tile_id))

        self.width = level["pxWid"]
        self.height = level["pxHei"]
        
        return level_data

    def draw(self, screen, camera):
        """ Dibuja el nivel en la pantalla basado en Tile Layer """
        for x, y, src_x, src_y, tile_id in self.level_data:
            tile_rect = pygame.Rect(src_x, src_y, self.tile_size, self.tile_size)
            screen.blit(self.tileset_image, camera.apply_rect(pygame.Rect(x, y, self.tile_size, self.tile_size)), tile_rect)
