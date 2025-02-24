import pygame
import sys

from Escenas.scene_abs import SceneAbs

class MainMenu(SceneAbs):
    def __init__(self, screen, scene_manager):
        super().__init__(screen, scene_manager)
        self.font = pygame.font.Font(None, 36)
        self.title_text = None
        self.title_rect = None
        self.menu_options = ["Jugar", "Ajustes", "Salir"]
        self.selected_option = 0

    def setup(self):
        """Inicialización de recursos"""
        self.title_text = self.font.render("Ñembi Survivor", True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(
            center=(self.screen.get_width() // 2, 100)
        )

    def cleanup(self):
        """Limpieza de recursos (no necesario en este caso)"""
        pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            elif event.key == pygame.K_RETURN:
                self.handle_selection()
            elif event.key == pygame.K_ESCAPE:
                pygame.quit()
                sys.exit()

    def handle_selection(self):
        if self.selected_option == 0:  # Jugar
            self.scene_manager.push_scene("game")
        elif self.selected_option == 1:  # Ajustes
            self.scene_manager.push_scene("settings")
        elif self.selected_option == 2:  # Salir
            pygame.quit()
            sys.exit()

    def update(self):
        """Actualización lógica (no necesaria en menú estático)"""
        pass

    def render(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.title_text, self.title_rect)

        for i, option in enumerate(self.menu_options):
            color = (255, 0, 0) if i == self.selected_option else (150, 150, 150)
            text = self.font.render(option, True, color)
            rect = text.get_rect(center=(self.screen.get_width() // 2, 200 + i * 50))
            self.screen.blit(text, rect)

    def pause(self):
        """Pausa el menú (no necesario)"""
        pass

    def resume(self):
        """Reanuda el menú (no necesario)"""
        pass