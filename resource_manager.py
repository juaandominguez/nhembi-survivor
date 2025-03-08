import json
import pygame, os

class ResourceManager:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance._textures = {}
            cls._instance._fonts = {}
            cls._instance._sounds = {}
        return cls._instance

    def get_texture(self, path):
        if path not in self._textures:
            self._textures[path] = pygame.image.load(path).convert_alpha()
        return self._textures[path]

    def get_font(self, name, size):
        key = (name, size)
        if key not in self._fonts:
            self._fonts[key] = pygame.font.Font(name, size)
        return self._fonts[key]

    def get_sound(self, path):
        if path not in self._sounds:
            self._sounds[path] = pygame.mixer.Sound(path)
        return self._sounds[path]
    


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
        
    # @classmethod
    # def CargarArchivoCoordenadas(cls, nombre):
    #     # Si el nombre de archivo está entre los recursos ya cargados
    #     if nombre in cls.recursos:
    #         # Se devuelve ese recurso
    #         return cls.recursos[nombre]
    #     # Si no ha sido cargado anteriormente
    #     else:
    #         # Se carga el recurso indicando el nombre de su carpeta
    #         fullname = os.path.join('sprites', nombre)
    #         pfile=open(fullname,'r')
    #         datos=pfile.read()
    #         pfile.close()
    #         # Se almacena
    #         cls.recursos[nombre] = datos
    #         # Se devuelve
    #         return datos