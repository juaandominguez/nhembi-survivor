import pygame


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