import pygame
import sys
from fase import Fase
from menu import PauseMenu, MenuScene, SettingsScene
# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

class Director:
    def __init__(self):
        # Initialize pygame if not already initialized
        pygame.init()

        # Create the main screen
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Nhembi Survivor")

        # Scene stack
        self.scene_stack = []

        # Game clock
        self.clock = pygame.time.Clock()

        # Control flags
        self.running = True
        self.exit_current_scene = False

        self.scene_map = {
            "menu": MenuScene(self),
            "pause": PauseMenu(self),
            "newgame": Fase(self),
            "settings": SettingsScene(self)
        }

    def game_loop(self, scene):
        # Reset exit flag
        self.exit_current_scene = False

        # Clear any pending events
        pygame.event.clear()

        while not self.exit_current_scene:
            # Control frame rate
            delta_time = self.clock.tick(FPS)

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                    return
                scene.handle_events(event)

            # Update and render
            scene.update(delta_time)
            self.screen.fill((0, 0, 0))  # Clear screen
            scene.render(self.screen)
            pygame.display.flip()

    def run(self):
        while self.running and len(self.scene_stack) > 0:
            # Get current scene
            current_scene = self.scene_stack[-1]
            # Run the game loop for current scene
            self.game_loop(current_scene)

        pygame.quit()
        sys.exit()

    def quit_game(self):
        """Exit the entire game"""
        self.running = False
        self.exit_current_scene = True
        self.scene_stack.clear()

    def pop_scene(self):
        """Exit only the current scene"""
        self.exit_current_scene = True
        if self.scene_stack:
            self.scene_stack.pop()


    def change_scene(self, scene):
        """Replace current scene with a new one"""
        self.exit_current_scene = True
        if self.scene_stack:
            self.scene_stack.pop()
        self.scene_stack.append(self.scene_map[scene])

    def push_scene(self, scene):
        """Add a new scene on top of the current one"""
        self.exit_current_scene = True
        self.scene_stack.append(self.scene_map[scene])

