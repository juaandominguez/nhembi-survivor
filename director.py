import pygame
import sys
import json
from menu import PauseMenu, MenuScene, SettingsScene, LoseScene, GameSettings, WinScene,InstructionsScene
from fase import Fase

# Initial configuration
INIT_WIDTH, INIT_HEIGHT, FPS = 800, 600, 60

class SceneFactory:
    def __init__(self, director, screen, scenes_registry):
        self.director = director
        self.screen = screen
        self.scenes_registry = scenes_registry

    def create(self, scene_identifier):
        if isinstance(scene_identifier, str):
            if scene_identifier in self.scenes_registry:
                scene_class = self.scenes_registry[scene_identifier]
                return scene_class(self.director, self.screen, scene_identifier) if scene_class == Fase else scene_class(self.director, self.screen)
            raise KeyError(f"Scene key '{scene_identifier}' not registered.")
        return Fase(self.director, self.screen, scene_identifier.config_name) if hasattr(scene_identifier, 'config_name') else scene_identifier.__class__(self.director, self.screen)

class Director:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Nhembi Survivor")

        self.scene_stack, self.scenes_registry = [], {}
        self.clock, self.running, self.exit_current_scene = pygame.time.Clock(), True, False
        self.current_phase = None
        self.saved_phase_instance = None  # Saves the current level instance

        # Game and resource configuration
        self.settings = GameSettings()
        self.screen = pygame.display.set_mode((INIT_WIDTH, INIT_HEIGHT))
        self.settings.apply_resolution(self.screen)

        # Register "static" scenes
        for key, scene in {"menu": MenuScene, "pause": PauseMenu, "settings": SettingsScene, "lose": LoseScene, "win": WinScene, "instructions": InstructionsScene}.items():
            self.register_scene(key, scene)

        self.load_levels_config()
        self.scene_factory = SceneFactory(self, self.screen, self.scenes_registry)

    def register_scene(self, scene_key, scene_class):
        self.scenes_registry[scene_key] = scene_class

    def load_levels_config(self):
        with open("levels_config.json") as f:
            for level_name in json.load(f):
                self.register_scene(level_name, Fase)

    def push_scene(self, scene_identifier):
        self.exit_current_scene = True

        # If it's a reload and there's a saved instance, use it
        if scene_identifier == self.current_phase and self.saved_phase_instance:
            new_scene = self.saved_phase_instance
        else:
            new_scene = self.scene_factory.create(scene_identifier)

        if isinstance(new_scene, Fase):
            self.current_phase = scene_identifier
            self.saved_phase_instance = new_scene

        if isinstance(new_scene, PauseMenu):
            new_scene.capture_background(self.screen.copy())

        self.scene_stack.append(new_scene)
        new_scene.on_enter()
        return new_scene

    def change_scene(self, scene_identifier):
        current_player_state = None
        if isinstance(self.scene_stack[-1], Fase):
            current_player_state = self.scene_stack[-1].jugador.save_state()
            self.saved_phase_instance = self.scene_stack[-1]

        self.pop_scene()
        new_scene = self.push_scene(scene_identifier)
        if current_player_state is not None:
            new_scene.jugador.load_state(current_player_state)

    def reload(self):
        self._apply_resolution()

    def pop_scene(self):
        self.exit_current_scene = True
        if self.scene_stack:
            scene = self.scene_stack.pop()
            if hasattr(scene, "on_exit"):
                scene.on_exit()

    def restart_scene(self):
        if self.scene_stack:
            self.exit_current_scene = True
            self.push_scene(self.scene_stack.pop())

    def restart_game(self):
        self.scene_stack.clear()
        self.saved_phase_instance = None  # 🔹 Clears the saved level state
        self.push_scene("menu")

    def game_loop(self):
        while not self.exit_current_scene:
            delta_time = self.clock.tick(FPS)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()
                    return
                if self.scene_stack:
                    self.scene_stack[-1].events(event)
            if self.scene_stack:
                self.screen.fill((0, 0, 0))
                self.scene_stack[-1].update(delta_time)
                self.scene_stack[-1].render(self.screen)
            pygame.display.flip()

    def run(self):
        while self.running and self.scene_stack:
            self.exit_current_scene = False
            self.game_loop()
        pygame.quit()
        sys.exit()

    def quit_game(self):
        self.running, self.exit_current_scene = False, True
        self.scene_stack.clear()

    def _get_scene_key(self, scene_instance):
        return next((key for key, scene_class in self.scenes_registry.items() if isinstance(scene_instance, scene_class)), None)

    def _apply_resolution(self):
        """
        Updates the display according to the current configuration and propagates the new surface to all active scenes.
        """
        # Get the new screen using the GameSettings method
        new_screen = self.settings.apply_resolution(self.screen)
        self.screen = new_screen
        # Notify each active scene of the change so they can update their layout if implemented
        for scene in self.scene_stack:
            scene.screen = new_screen
            # If the scene defines an 'on_resolution_change' method, call it
            if hasattr(scene, 'on_resolution_change'):
                scene.on_resolution_change(new_screen)





