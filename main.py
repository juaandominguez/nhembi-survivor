import pygame
import random
from pygame.locals import *

from Escenas.main_menu import MainMenu
from Escenas.scene_manager import SceneManager
from Escenas.settings_menu import SettingsScene
from Escenas.new_game_scene import NewGameScene
from Escenas.pause_menu import PauseMenu
from resource_manager import ResourceManager
from camera import Camera
from level import Level
from enemy import Enemy
from player import Player

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock()
        self.running = True

        # Inicializar SceneManager
        self.scene_manager = SceneManager(self.screen)
        self.resource_manager = ResourceManager()

        # Registrar todas las escenas
        self.scene_manager.register_scene("main_menu", MainMenu)
        self.scene_manager.register_scene("game", NewGameScene)
        self.scene_manager.register_scene("pause", PauseMenu)
        self.scene_manager.register_scene("settings", SettingsScene)


        self.scene_manager.push_scene("main_menu")

    def run(self):
        while self.running:
            # Manejar eventos globales
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.scene_manager.handle_event(event)

            self.scene_manager.update()
            self.screen.fill((0, 0, 0))
            self.scene_manager.render()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()

