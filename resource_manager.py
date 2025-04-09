import json
import pygame
import os
import logging

# Logger basic configuration
logging.basicConfig(level=logging.DEBUG, format="%(asctime)s [%(levelname)s] %(message)s")

# -------------------------------------------------
# ResourceManager Class: Centralized resource management
class ResourceManager:
    _resources = {}
    _sounds = {}
    _music = {}
    _fx_volume = 0.5

    @classmethod
    def set_fx_volume(cls, volume):
        cls._fx_volume = volume
        for sound in cls._sounds.values():
            sound.set_volume(volume)

    @classmethod
    def load_image(cls, name):
        if name in cls._resources:
            return cls._resources[name]
        fullname = os.path.join("sprites", name)
        try:
            image = pygame.image.load(fullname)
        except pygame.error as err:
            logging.error(f"Cannot load image: {fullname} - {err}")
            raise SystemExit(err)
        image = image.convert_alpha()
        cls._resources[name] = image
        return image

    @classmethod
    def load_coordinates(cls, name):
        if name in cls._resources:
            return cls._resources[name]
        fullname = os.path.join("sprites", name)
        try:
            with open(fullname, "r") as file:
                data = file.read()
        except Exception as err:
            logging.error(f"Cannot load coordinates from: {fullname} - {err}")
            raise SystemExit(err)
        cls._resources[name] = data
        return data

    @classmethod
    def load_level(cls, level_file):
        """Loads level data from an LDtk file (JSON)"""
        try:
            with open(level_file, 'r', encoding='utf-8') as f:
                project = json.load(f)
        except Exception as err:
            logging.error(f"Error loading level file: {level_file} - {err}")
            raise SystemExit(err)

        level_data_tileset = []
        level_data_decorations = []
        level_collisions = []
        level = project["levels"][0]

        for layer in level["layerInstances"]:
            identifier = layer["__identifier"]
            if identifier in ("Suelo_paredes", "Muebles"):  # Floors and walls, Furniture
                for tile in layer["gridTiles"]:
                    tile_x, tile_y = tile["px"]
                    tile_src_x, tile_src_y = tile["src"]
                    tile_id = tile["t"]
                    if identifier == "Suelo_paredes":
                        level_data_tileset.append((tile_x, tile_y, tile_src_x, tile_src_y, tile_id))
                    else:
                        level_data_decorations.append((tile_x, tile_y, tile_src_x, tile_src_y, tile_id))
            elif layer["__identifier"] == "Collisions":
                for tile in layer["gridTiles"]:
                    x, y = tile["px"]
                    level_collisions.append(pygame.Rect(x, y, 1, 1))

        return level_data_tileset, level_data_decorations, level_collisions

    @classmethod
    def load_font(cls, name, size):
        key = (name, size)
        if key in cls._resources:
            return cls._resources[key]
        if name is None:
            font = pygame.font.Font(pygame.font.get_default_font(), size)
        else:
            fullname = os.path.join("fonts", name)
            try:
                font = pygame.font.Font(fullname, size)
            except Exception as err:
                logging.error(f"Cannot load font: {fullname} - {err}")
                raise SystemExit(err)
        cls._resources[key] = font
        return font

    @classmethod
    def load_music(cls, name):
        if name in cls._music:
            return cls._music[name]
        fullname = os.path.join("music", name)
        if not os.path.exists(fullname):
            raise FileNotFoundError(f"Music file not found: {fullname}")
        cls._music[name] = fullname
        return fullname

    @classmethod
    def load_sound(cls, name):
        if name in cls._sounds:
            return cls._sounds[name]
        fullname = os.path.join("sounds", name)
        try:
            sound = pygame.mixer.Sound(fullname)
            sound.set_volume(cls._fx_volume)
        except Exception as err:
            logging.error(f"Cannot load sound: {fullname} - {err}")
            raise SystemExit(err)
        cls._sounds[name] = sound
        return sound



