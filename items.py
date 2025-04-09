import pygame
from resource_manager import ResourceManager

class Item(pygame.sprite.Sprite):
    def __init__(self, pos, image, sound):
        super().__init__()
        self.resources = ResourceManager()
        self.image = self.resources.load_image(image)
        self.rect = self.image.get_rect(topleft=pos)
        self.sound = self.resources.load_sound(sound)

    def make_sound(self):
        self.sound.play()

class Coin(Item):
    def __init__(self, pos):
        super().__init__(pos, "Icono Moneda.png", "objeto.mp3")
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect(topleft=pos)

class Tortilla(Item):
    def __init__(self, pos):
        super().__init__(pos, "spanish_tortilla_sprite.png", "glup.mp3")
        self.image = pygame.transform.scale(self.image, (32, 32))
        self.rect = self.image.get_rect(topleft=pos)