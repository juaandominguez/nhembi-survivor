import pygame
import os
from pygame.locals import *

# -------------------------------------------------
# Class ResourceManager

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
