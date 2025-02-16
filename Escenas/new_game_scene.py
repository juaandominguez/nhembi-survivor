import pygame
from Escenas.scene_abs import SceneAbs

class NewGameScene(SceneAbs):
    def __init__(self, screen, scene_manager):
        super().__init__(screen, scene_manager)
        self.screen = screen
        self.scene_manager = scene_manager
        self.font = pygame.font.Font(None, 36)

        self.title_text = self.font.render("Empieza el juego", True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(center=(screen.get_width() // 2, 100))

        self.game_started = False

    def setup(self):
        self.game_started = True

    def cleanup(self):
        pass

    def update(self):
        pass

    def render(self):
        self.screen.fill((0, 0, 0))

        self.screen.blit(self.title_text, self.title_rect)

        if self.game_started:
            pass
        else:
            pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.handle_selection()

    def handle_selection(self):
        print("Starting a new game")