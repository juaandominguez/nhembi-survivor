import json
import pygame

class Level:
    def __init__(self, level_file):
        """ Carga el nivel desde un archivo LDtk y usa un tileset """
        self.level_tileset = "./levels/suelos_paredes.png"
        self.level_decorations = "./levels/muebles.png"
        self.tileset_image = pygame.image.load(self.level_tileset).convert_alpha()
        self.tileset_decorations = pygame.image.load(self.level_decorations).convert_alpha()
        self.tile_size = 16  # Tamaño de los tiles en píxeles
        self.level_data, self.level_decorations, self.level_collisions = self.load_level(level_file)  # Cargar datos del nivel desde LDtk
        

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

        self.width = level["pxWid"]
        self.height = level["pxHei"]
     
        return level_data_tileset, level_data_decorations, level_collisions


    def draw(self, screen, camera):
        """ Dibuja el nivel en la pantalla basado en Tile Layer """
        for x, y, src_x, src_y, tile_id in self.level_data:
            tile_rect = pygame.Rect(src_x, src_y, self.tile_size, self.tile_size)
            screen.blit(self.tileset_image, camera.apply_rect(pygame.Rect(x, y, self.tile_size, self.tile_size)), tile_rect)
        for x, y, src_x, src_y, tile_id in self.level_decorations:
            tile_rect = pygame.Rect(src_x, src_y, self.tile_size, self.tile_size)
            screen.blit(self.tileset_decorations, camera.apply_rect(pygame.Rect(x, y, self.tile_size, self.tile_size)), tile_rect)
        

    def get_level_collisions(self):
        return self.level_collisions