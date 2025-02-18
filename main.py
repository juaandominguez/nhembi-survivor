import pygame
import random
from pygame.locals import *

from Escenas.main_menu import MainMenu
from Escenas.scene_manager import SceneManager
from Escenas.settings_menu import SettingsScene
from Escenas.new_game_scene import NewGameScene

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
        pygame.display.set_caption("Ñembi Survivor")
        self.clock = pygame.time.Clock()
        self.running = True

        self.scene_manager = SceneManager(self.screen)

        self.scene_manager.add_scene("MainMenuScene",
                                     MainMenu(self.screen, self.scene_manager))
        self.scene_manager.add_scene("SettingsScene",
                                     SettingsScene(self.screen, self.scene_manager))
        self.scene_manager.add_scene("NewGameScene",
                                     NewGameScene(self.screen, self.scene_manager))

    def run(self):
        self.scene_manager.switch_scene("MainMenuScene")
        while self.running:
            # Manejar eventos
            for event in pygame.event.get():
                if event.type == QUIT:
                    self.running = False
                self.scene_manager.handle_event(event)

            # Actualizar y renderizar
            self.scene_manager.update()
            self.scene_manager.render()

            pygame.display.flip()
            self.clock.tick(60)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()

