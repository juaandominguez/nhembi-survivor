import pygame
import sys
from Escenas.scene_abs import SceneAbs
from resource_manager import ResourceManager


class PauseMenu(SceneAbs):
    def __init__(self, screen, scene_manager):
        super().__init__(screen, scene_manager)
        self.resources = ResourceManager()
        self.background = None
        self._setup_fonts()

        self.options = ["Continuar", "Volver al menú", "Salir"]
        self.selected = 0

    def _setup_fonts(self):
        self.title_font = self.resources.get_font(None, 48)
        self.option_font = self.resources.get_font(None, 36)

    def capture_background(self, background_surface):
        self.background = background_surface.copy()

    def setup(self):
        pass
    def cleanup(self):
        self.background = None

    def update(self):
        pass

    def render(self):
        if self.background:
            self.screen.blit(self.background, (0, 0))

        # Capa semitransparente
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        # Título
        title = self.title_font.render("PAUSA", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 200))
        self.screen.blit(title, title_rect)

        # Opciones
        for i, opt in enumerate(self.options):
            color = (255, 0, 0) if i == self.selected else (200, 200, 200)
            text = self.option_font.render(opt, True, color)
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, 300 + i * 60))
            self.screen.blit(text, text_rect)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self._handle_selection()
            elif event.key == pygame.K_ESCAPE:
                self.scene_manager.pop_scene()

    def _handle_selection(self):
        if self.selected == 0:
            self.scene_manager.pop_scene()
        elif self.selected == 1:
            self._return_to_main_menu()
        elif self.selected == 2:
            pygame.quit()
            sys.exit()

    def _return_to_main_menu(self):
        self.scene_manager.pop_scene()
        old_key = self.scene_manager.pop_scene()
        self.scene_manager.delete_scene_instance(old_key)
        while len(self.scene_manager.scene_stack) > 0:
            self.scene_manager.pop_scene()
        self.scene_manager.push_scene("main_menu")

    def pause(self):
        pass

    def resume(self):
        pass