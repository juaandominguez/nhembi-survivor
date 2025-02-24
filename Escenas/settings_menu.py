import pygame
from Escenas.scene_abs import SceneAbs
import json
import os


class GameSettings:
    _instance = None

    def __new__(cls):
        if not cls._instance:
            cls._instance = super().__new__(cls)
            cls._instance.load_settings()
        return cls._instance

    def load_settings(self):
        """Carga los ajustes desde un archivo JSON"""
        self.defaults = {
            'music_volume': 0.5,
            'fx_volume': 0.5,
            'resolution': (1280, 720),
            'fullscreen': False
        }

        try:
            with open('settings.json', 'r') as f:
                self.settings = json.load(f)
                # Convertir la resolución de lista a tupla
                self.settings['resolution'] = tuple(self.settings['resolution'])
        except:
            self.settings = self.defaults.copy()

    def save_settings(self):
        """Guarda los ajustes en un archivo JSON"""
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)

    def apply_resolution(self, screen):
        """Aplica los ajustes de resolución y pantalla completa"""
        flags = pygame.FULLSCREEN if self.settings['fullscreen'] else 0
        if self.settings['resolution'] != screen.get_size():
            return pygame.display.set_mode(
                self.settings['resolution'],
                flags,
                vsync=1
            )
        return screen


class SettingsScene(SceneAbs):
    def __init__(self, screen, scene_manager):
        super().__init__(screen, scene_manager)
        self.settings = GameSettings()
        self.resolutions = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1920, 1080)
        ]
        self._setup_ui()

    def _setup_ui(self):
        """Configura los elementos de la UI"""
        self.font = pygame.font.Font(None, 36)
        self.title_text = self.font.render("Ajustes", True, (255, 255, 255))
        self.title_rect = self.title_text.get_rect(
            center=(self.screen.get_width() // 2, 50)
        )

        self.menu_options = [
            "Volumen música",
            "Volumen efectos",
            "Resolución",
            "Pantalla completa",
            "Guardar y Salir",
            "Cancelar"
        ]

        self.selected_option = 0
        self.resolution_index = self.resolutions.index(
            self.settings.settings['resolution']
        )

    def setup(self):
        """Carga los valores actuales de los ajustes"""
        self.current_settings = self.settings.settings.copy()

    def cleanup(self):
        """Limpia los recursos temporales"""
        pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_option = (self.selected_option - 1) % len(self.menu_options)
            elif event.key == pygame.K_DOWN:
                self.selected_option = (self.selected_option + 1) % len(self.menu_options)
            elif event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.adjust_setting(event.key)
            elif event.key == pygame.K_RETURN:
                self.handle_selection()
            elif event.key == pygame.K_ESCAPE:
                self.exit_settings()

    def adjust_setting(self, key):
        """Ajusta los valores de los sliders o opciones"""
        if self.selected_option == 0:  # Volumen música
            delta = -0.1 if key == pygame.K_LEFT else 0.1
            self.current_settings['music_volume'] = max(0, min(1,
                                                               self.current_settings['music_volume'] + delta
                                                               ))
            pygame.mixer.music.set_volume(self.current_settings['music_volume'])

        elif self.selected_option == 1:  # Volumen efectos
            delta = -0.1 if key == pygame.K_LEFT else 0.1
            self.current_settings['fx_volume'] = max(0, min(1,self.current_settings['fx_volume'] + delta))

        elif self.selected_option == 2:  # Resolución
            self.resolution_index = (
                (self.resolution_index - 1) % len(self.resolutions)
                if key == pygame.K_LEFT else
                (self.resolution_index + 1) % len(self.resolutions))
            self.current_settings['resolution'] = self.resolutions[self.resolution_index]

    def handle_selection(self):
        if self.selected_option == 3:  # Aplicar cambios
            self.apply_settings()
        elif self.selected_option == 4:  # Volver
            self.exit_settings()

    def apply_settings(self):
        """Aplica y guarda todos los ajustes"""
        # Actualizar volumen de efectos (ejemplo con un sonido)
        pygame.mixer.music.set_volume(self.current_settings['music_volume'])

        # Aplicar resolución y pantalla completa
        new_screen = self.settings.apply_resolution(self.screen)
        if new_screen != self.screen:
            self.screen = new_screen
            self.scene_manager.screen = new_screen
            self._setup_ui()  # Reconfigurar UI con nueva resolución

        # Guardar ajustes
        self.settings.settings = self.current_settings.copy()
        self.settings.save_settings()

    def exit_settings(self):
        """Sale del menú de ajustes"""
        if self.current_settings != self.settings.settings:
            self.apply_settings()
        self.scene_manager.pop_scene()

    def update(self):
        pass

    def render(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.title_text, self.title_rect)

        for i, option in enumerate(self.menu_options):
            color = (255, 0, 0) if i == self.selected_option else (150, 150, 150)
            y = 100 + i * 50

            # Texto de la opción
            text = self.font.render(option, True, color)
            text_rect = text.get_rect(topleft=(50, y))
            self.screen.blit(text, text_rect)

            # Contenido adicional
            if i == 0:  # Volumen música
                self.draw_slider(y, self.current_settings['music_volume'])
            elif i == 1:  # Volumen efectos
                self.draw_slider(y, self.current_settings['fx_volume'])
            elif i == 2:  # Resolución
                res_text = self.font.render(
                    f"{self.current_settings['resolution'][0]}x{self.current_settings['resolution'][1]}",
                    True, color
                )
                res_rect = res_text.get_rect(topleft=(300, y))
                self.screen.blit(res_text, res_rect)

    def draw_slider(self, y, value):
        """Dibuja un slider interactivo"""
        slider_x = 300
        slider_width = 200
        slider_height = 20
        thumb_size = 15

        # Barra del slider
        pygame.draw.rect(self.screen, (200, 200, 200),
                         (slider_x, y, slider_width, slider_height))

        # Thumb del slider
        thumb_x = slider_x + int((slider_width - thumb_size) * value)
        pygame.draw.rect(self.screen, (0, 255, 0),
                         (thumb_x, y - 5, thumb_size, slider_height + 10))

    def pause(self):
        pass

    def resume(self):
        pass