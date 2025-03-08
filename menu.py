import pygame
import json
import sys
from abc import ABC, abstractmethod
from scene import Scene  # Se asume que tienes una clase base Scene
from director import Director as scene_manager  # Gestor de escenas
from resource_manager import ResourceManager  # Gestor de recursos
# -------------------------------
# Patrón Singleton para GameSettings
# -------------------------------
class GameSettings:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameSettings, cls).__new__(cls)
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
                # Asegurarse de que la resolución sea una tupla
                self.settings['resolution'] = tuple(self.settings['resolution'])
        except Exception:
            self.settings = self.defaults.copy()

    def save_settings(self):
        """Guarda los ajustes en un archivo JSON"""
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)

    def apply_resolution(self, screen):
        """Aplica la resolución y el modo de pantalla completa"""
        flags = pygame.FULLSCREEN if self.settings['fullscreen'] else 0
        if self.settings['resolution'] != screen.get_size():
            return pygame.display.set_mode(
                self.settings['resolution'],
                flags,
                vsync=1
            )
        return screen

# -------------------------------
# Base para componentes UI (Patrón Componente)
# -------------------------------
class UIComponent(ABC):
    def __init__(self):
        self.selected = False

    @abstractmethod
    def handle_event(self, event):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self, surface):
        pass

# -------------------------------
# Componente Slider (para volúmenes, etc.)
# -------------------------------
class Slider(UIComponent):
    def __init__(self, x, y, width, height, value, min_value=0, max_value=1, step=0.1,
                 thumb_size=15, color=(0, 255, 0), bg_color=(200, 200, 200)):
        super().__init__()
        self.rect = pygame.Rect(x, y, width, height)
        self.value = value
        self.min_value = min_value
        self.max_value = max_value
        self.step = step
        self.thumb_size = thumb_size
        self.color = color
        self.bg_color = bg_color

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.selected:
            if event.key == pygame.K_LEFT:
                self.value = max(self.min_value, self.value - self.step)
            elif event.key == pygame.K_RIGHT:
                self.value = min(self.max_value, self.value + self.step)

    def update(self):
        pass

    def render(self, surface):
        pygame.draw.rect(surface, self.bg_color, self.rect)
        ratio = (self.value - self.min_value) / (self.max_value - self.min_value)
        thumb_x = self.rect.x + int((self.rect.width - self.thumb_size) * ratio)
        thumb_rect = pygame.Rect(thumb_x, self.rect.y - 5, self.thumb_size, self.rect.height + 10)
        pygame.draw.rect(surface, self.color, thumb_rect)
        if self.selected:
            pygame.draw.rect(surface, (255, 255, 0), self.rect, 2)

# -------------------------------
# Componente Dropdown (por ejemplo, para resoluciones)
# -------------------------------
class Dropdown(UIComponent):
    def __init__(self, x, y, options, selected_index=0, font=None, text_color=(255, 255, 255)):
        super().__init__()
        self.x = x
        self.y = y
        self.options = options  # Lista de tuplas (ancho, alto)
        self.selected_index = selected_index
        self.font = font or pygame.font.Font(None, 36)
        self.text_color = text_color

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.selected:
            if event.key == pygame.K_LEFT:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_RIGHT:
                self.selected_index = (self.selected_index + 1) % len(self.options)

    def update(self):
        pass

    def render(self, surface):
        res = self.options[self.selected_index]
        option_text = self.font.render(f"{res[0]}x{res[1]}", True, self.text_color)
        surface.blit(option_text, (self.x, self.y))
        if self.selected:
            rect = option_text.get_rect(topleft=(self.x, self.y))
            pygame.draw.rect(surface, (255, 255, 0), rect, 2)

# -------------------------------
# Componente Toggle (para valores booleanos, ej. pantalla completa)
# -------------------------------
class Toggle(UIComponent):
    def __init__(self, x, y, value, font=None, text_color=(255, 255, 255)):
        super().__init__()
        self.x = x
        self.y = y
        self.value = value
        self.font = font or pygame.font.Font(None, 36)
        self.text_color = text_color

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.selected:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                self.value = not self.value

    def update(self):
        pass

    def render(self, surface):
        text = self.font.render("Sí" if self.value else "No", True, self.text_color)
        surface.blit(text, (self.x, self.y))
        if self.selected:
            rect = text.get_rect(topleft=(self.x, self.y))
            pygame.draw.rect(surface, (255, 255, 0), rect, 2)

# -------------------------------
# Componente Button (usando Command Pattern)
# -------------------------------
class Button(UIComponent):
    def __init__(self, x, y, text, callback, font=None, text_color=(255, 255, 255)):
        super().__init__()
        self.x = x
        self.y = y
        self.text = text
        self.callback = callback
        self.font = font or pygame.font.Font(None, 36)
        self.text_color = text_color
        self.rect = None

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and self.selected:
            if event.key == pygame.K_RETURN:
                self.callback()

    def update(self):
        pass

    def render(self, surface):
        text_surface = self.font.render(self.text, True, self.text_color)
        self.rect = text_surface.get_rect(topleft=(self.x, self.y))
        surface.blit(text_surface, self.rect)
        if self.selected:
            pygame.draw.rect(surface, (255, 255, 0), self.rect, 2)

# ================================
# Clases base para las pantallas
# ================================
class PantallaBase(ABC):
    def __init__(self, screen, font):
        self.screen = screen
        self.font = font

    @abstractmethod
    def handle_event(self, event):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self):
        pass

# -------------------------------
# Pantalla del Menú Principal
# -------------------------------
class PantallaMenu(PantallaBase):
    def __init__(self, screen, font, callback_start, callback_settings, callback_quit):
        super().__init__(screen, font)
        self.callback_start = callback_start
        self.callback_settings = callback_settings
        self.callback_quit = callback_quit

        self.title = self.font.render("Ñembi Survivor", True, (255, 255, 255))
        self.title_rect = self.title.get_rect(center=(self.screen.get_width() // 2, 100))
        btn_x = self.screen.get_width() // 2 - 50
        start_y = 200
        self.buttons = [
            Button(btn_x, start_y, "Jugar", self.callback_start, self.font),
            Button(btn_x, start_y + 50, "Ajustes", self.callback_settings, self.font),
            Button(btn_x, start_y + 100, "Salir", self.callback_quit, self.font)
        ]
        self.selected_index = 0
        for i, btn in enumerate(self.buttons):
            btn.selected = (i == self.selected_index)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.buttons[self.selected_index].selected = False
                self.selected_index = (self.selected_index - 1) % len(self.buttons)
                self.buttons[self.selected_index].selected = True
            elif event.key == pygame.K_DOWN:
                self.buttons[self.selected_index].selected = False
                self.selected_index = (self.selected_index + 1) % len(self.buttons)
                self.buttons[self.selected_index].selected = True
            elif event.key == pygame.K_ESCAPE:
                self.callback_quit()
            else:
                self.buttons[self.selected_index].handle_event(event)

    def update(self):
        for btn in self.buttons:
            btn.update()

    def render(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.title, self.title_rect)
        for btn in self.buttons:
            btn.render(self.screen)

# -------------------------------
# Pantalla de Ajustes
# -------------------------------
class PantallaAjustes(PantallaBase):
    def __init__(self, screen, font, settings_instance, callback_save, callback_cancel):
        super().__init__(screen, font)
        self.settings_instance = settings_instance
        self.callback_save = callback_save
        self.callback_cancel = callback_cancel

        self.title = self.font.render("Ajustes", True, (255, 255, 255))
        self.title_rect = self.title.get_rect(center=(self.screen.get_width() // 2, 50))
        music_volume = self.settings_instance.settings.get('music_volume', 0.5)
        fx_volume = self.settings_instance.settings.get('fx_volume', 0.5)
        fullscreen = self.settings_instance.settings.get('fullscreen', False)
        resolution = self.settings_instance.settings.get('resolution', (1280, 720))
        self.music_slider = Slider(300, 100, 200, 20, music_volume)
        self.fx_slider = Slider(300, 150, 200, 20, fx_volume)
        resolution_options = [
            (800, 600),
            (1024, 768),
            (1280, 720),
            (1920, 1080)
        ]
        try:
            initial_index = resolution_options.index(resolution)
        except ValueError:
            initial_index = 2
        self.resolution_dropdown = Dropdown(300, 200, resolution_options, selected_index=initial_index, font=self.font)
        self.fullscreen_toggle = Toggle(300, 250, fullscreen, font=self.font)
        self.save_button = Button(50, 350, "Guardar y Salir", self.callback_save, self.font)
        self.cancel_button = Button(50, 400, "Cancelar", self.callback_cancel, self.font)
        self.components = [
            self.music_slider,
            self.fx_slider,
            self.resolution_dropdown,
            self.fullscreen_toggle,
            self.save_button,
            self.cancel_button
        ]
        self.selected_index = 0
        for i, comp in enumerate(self.components):
            comp.selected = (i == self.selected_index)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.components[self.selected_index].selected = False
                self.selected_index = (self.selected_index - 1) % len(self.components)
                self.components[self.selected_index].selected = True
            elif event.key == pygame.K_DOWN:
                self.components[self.selected_index].selected = False
                self.selected_index = (self.selected_index + 1) % len(self.components)
                self.components[self.selected_index].selected = True
            else:
                self.components[self.selected_index].handle_event(event)

    def update(self):
        for comp in self.components:
            comp.update()

    def render(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.title, self.title_rect)
        # Etiquetas
        self.screen.blit(self.font.render("Volumen Música", True, (255, 255, 255)), (50, 100))
        self.screen.blit(self.font.render("Volumen Efectos", True, (255, 255, 255)), (50, 150))
        self.screen.blit(self.font.render("Resolución", True, (255, 255, 255)), (50, 200))
        self.screen.blit(self.font.render("Pantalla completa", True, (255, 255, 255)), (50, 250))
        for comp in self.components:
            comp.render(self.screen)

# -------------------------------
# Pantalla del Juego (Placeholder)
# -------------------------------
class PantallaJuego(PantallaBase):
    def __init__(self, screen, font, callback_return):
        super().__init__(screen, font)
        self.callback_return = callback_return
        self.title = self.font.render("Juego", True, (255, 255, 255))
        self.title_rect = self.title.get_rect(center=(self.screen.get_width() // 2, 100))
        btn_x = self.screen.get_width() // 2 - 50
        start_y = 200
        self.button_return = Button(btn_x, start_y, "Volver al Menú", self.callback_return, self.font)
        self.components = [self.button_return]
        self.selected_index = 0
        for i, comp in enumerate(self.components):
            comp.selected = (i == self.selected_index)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_DOWN):
                pass  # Solo hay un botón, sin navegación
            elif event.key == pygame.K_ESCAPE:
                self.callback_return()
            else:
                self.components[self.selected_index].handle_event(event)

    def update(self):
        for comp in self.components:
            comp.update()

    def render(self):
        self.screen.fill((0, 0, 0))
        self.screen.blit(self.title, self.title_rect)
        for comp in self.components:
            comp.render(self.screen)



# ================================

class PauseMenu(Scene):
    def __init__(self, screen, scene_manager):
        super().__init__(screen, scene_manager)
        self.screen = screen
        self.scene_manager = scene_manager
        self.resources = ResourceManager()
        self.background = None
        self._setup_fonts()

        self.options = ["Continuar", "Volver al menú", "Salir"]
        self.selected = 0

    def _setup_fonts(self):
        self.title_font = self.resources.get_font(None, 48)
        self.option_font = self.resources.get_font(None, 36)

    def capture_background(self, background_surface):
        """Guarda una captura del fondo para mostrarla en el menú de pausa."""
        self.background = background_surface.copy()

    def setup(self):
        pass

    def cleanup(self):
        self.background = None

    def update(self, delta_time):
        """No se requiere actualización constante en el menú de pausa."""
        pass

    def render(self):
        """Dibuja el menú de pausa sobre el fondo congelado del juego."""
        if self.background:
            self.screen.blit(self.background, (0, 0))

        # Capa semitransparente para efecto de pausa
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Negro con opacidad
        self.screen.blit(overlay, (0, 0))

        # Título "PAUSA"
        title = self.title_font.render("PAUSA", True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.screen.get_width() // 2, 200))
        self.screen.blit(title, title_rect)

        # Opciones de menú
        for i, opt in enumerate(self.options):
            color = (255, 0, 0) if i == self.selected else (200, 200, 200)
            text = self.option_font.render(opt, True, color)
            text_rect = text.get_rect(center=(self.screen.get_width() // 2, 300 + i * 60))
            self.screen.blit(text, text_rect)

    def handle_event(self, event):
        """Maneja la navegación en el menú de pausa."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected = (self.selected - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.selected = (self.selected + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                self._handle_selection()
            elif event.key == pygame.K_ESCAPE:
                self.scene_manager.pop_scene()  # Volver al juego

    def _handle_selection(self):
        """Ejecuta la acción correspondiente a la opción seleccionada."""
        if self.selected == 0:
            self.scene_manager.pop_scene()  # Continuar juego
        elif self.selected == 1:
            self._return_to_main_menu()  # Volver al menú principal
        elif self.selected == 2:
            pygame.quit()
            sys.exit()  # Salir del juego

    def _return_to_main_menu(self):
        """Vuelve al menú principal cerrando todas las escenas activas."""
        while self.scene_manager.scene_stack:
            self.scene_manager.pop_scene()
        self.scene_manager.push_scene("main_menu")  # Asegúrate de tener una escena con esta clave en tu Scene Manager

# -------------------------------
# Escena Unificada que gestiona las pantallas
# -------------------------------
class MenuScene(Scene):
    def __init__(self, screen):
        super().__init__(screen)
        self.screen = screen
        self.font = pygame.font.Font(None, 36)
        self.settings_instance = GameSettings()
        # Instanciar cada pantalla pasándole los callbacks para cambiar de estado
        self.pantalla_menu = PantallaMenu(
            screen,
            self.font,
            callback_start=self.start_game,
            callback_settings=self.open_settings,
            callback_quit=self.quit_game
        )
        self.pantalla_ajustes = PantallaAjustes(
            screen,
            self.font,
            settings_instance=self.settings_instance,
            callback_save=self.save_and_return_to_menu,
            callback_cancel=self.cancel_settings
        )
        self.pantalla_juego = PantallaJuego(
            screen,
            self.font,
            callback_return=self.return_to_menu_from_game
        )
        # La pantalla activa comienza siendo el menú
        self.active_screen = self.pantalla_menu

    def handle_event(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        self.active_screen.handle_event(event)

    def update(self, delta_time):
        self.active_screen.update()

    def render(self):
        self.active_screen.render()

    # --- Callbacks para cambiar de pantalla ---
    def start_game(self):
        self.active_screen = self.pantalla_juego

    def open_settings(self):
        self.reload_settings_components()
        self.active_screen = self.pantalla_ajustes

    def reload_settings_components(self):
        # Actualiza los componentes de ajustes con los valores actuales
        music_volume = self.settings_instance.settings.get('music_volume', 0.5)
        fx_volume = self.settings_instance.settings.get('fx_volume', 0.5)
        fullscreen = self.settings_instance.settings.get('fullscreen', False)
        resolution = self.settings_instance.settings.get('resolution', (1280, 720))
        self.pantalla_ajustes.music_slider.value = music_volume
        self.pantalla_ajustes.fx_slider.value = fx_volume
        try:
            self.pantalla_ajustes.resolution_dropdown.selected_index = self.pantalla_ajustes.resolution_dropdown.options.index(resolution)
        except ValueError:
            self.pantalla_ajustes.resolution_dropdown.selected_index = 2
        self.pantalla_ajustes.fullscreen_toggle.value = fullscreen
        self.pantalla_ajustes.selected_index = 0
        for i, comp in enumerate(self.pantalla_ajustes.components):
            comp.selected = (i == self.pantalla_ajustes.selected_index)

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def save_and_return_to_menu(self):
        # Guardar los ajustes actuales
        self.settings_instance.settings['music_volume'] = self.pantalla_ajustes.music_slider.value
        self.settings_instance.settings['fx_volume'] = self.pantalla_ajustes.fx_slider.value
        self.settings_instance.settings['resolution'] = self.pantalla_ajustes.resolution_dropdown.options[
            self.pantalla_ajustes.resolution_dropdown.selected_index]
        self.settings_instance.settings['fullscreen'] = self.pantalla_ajustes.fullscreen_toggle.value
        new_screen = self.settings_instance.apply_resolution(self.screen)
        if new_screen != self.screen:
            self.screen = new_screen
        self.settings_instance.save_settings()
        self.active_screen = self.pantalla_menu

    def cancel_settings(self):
        self.active_screen = self.pantalla_menu

    def return_to_menu_from_game(self):
        self.active_screen = self.pantalla_menu

    def pause(self):
        pass

    def resume(self):
        pass
