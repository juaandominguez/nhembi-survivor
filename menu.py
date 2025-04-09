import pygame
import json
import sys
from abc import ABC, abstractmethod
from scene import Scene  # Assumes you have a base Scene class
from resource_manager import ResourceManager  # Resource manager
import logging

# -------------------------------
# Singleton Pattern for GameSettings
# -------------------------------

font = "PressStart2P-Regular.ttf"
class UIFactory:
    @staticmethod
    def create_button(x, y, text, callback, font=None, text_color=(255, 255, 255)):
        return Button(x, y, text, callback, font, text_color)

    @staticmethod
    def create_slider(x, y, width, height, value, min_value=0, max_value=1, step=0.1,
                     thumb_size=15, color=(0, 255, 0), bg_color=(200, 200, 200)):
        return Slider(x, y, width, height, value, min_value, max_value, step,
                     thumb_size, color, bg_color)

    @staticmethod
    def create_dropdown(x, y, options, selected_index=0, font=None, text_color=(255, 255, 255)):
        return Dropdown(x, y, options, selected_index, font, text_color)


class UINavigationMixin:
    def handle_ui_navigation(self, event, components):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_w:
                self._move_selection(-1, components)
            elif event.key == pygame.K_s:
                self._move_selection(1, components)
            elif event.key in (pygame.K_a, pygame.K_d):
                # Delegate left/right handling to the selected component
                if 0 <= self.selected_index < len(components):
                    components[self.selected_index].events(event)
            elif event.key == pygame.K_RETURN:
                if 0 <= self.selected_index < len(components):
                    components[self.selected_index].events(event)

    def _move_selection(self, direction, components):
        if 0 <= self.selected_index < len(components):
            components[self.selected_index].selected = False

        self.selected_index = (self.selected_index + direction) % len(components)

        if 0 <= self.selected_index < len(components):
            components[self.selected_index].selected = True

    def update_selection(self, components):
        for i, comp in enumerate(components):
            comp.selected = (i == self.selected_index)

# -------------------------------------------------
# GameSettings Class: Global game configuration
class GameSettings:
    _instance = None
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(GameSettings, cls).__new__(cls)
            cls._instance.load_settings()
        return cls._instance

    def load_settings(self):
        """Loads settings from a JSON file"""
        self.defaults = {
            'music_volume': 0.5,
            'fx_volume': 0.5,
            'resolution': (800, 600),
        }
        try:
            with open('settings.json', 'r') as f:
                self.settings = json.load(f)
                if self.settings['resolution'] != "FULL":
                    self.settings['resolution'] = tuple(self.settings['resolution'])
                else:
                    self.settings['resolution'] = str("FULL")
                pygame.mixer.music.set_volume(self.settings['music_volume'])
                ResourceManager.set_fx_volume(self.settings['fx_volume'])

        except Exception as err:
            logging.error(f"Error loading settings: {err}")
            self.settings = self.defaults.copy()

    def save_settings(self):
        """Saves settings to a JSON file"""
        try:
            with open('settings.json', 'w') as f:
                json.dump(self.settings, f)
        except Exception as err:
            logging.error(f"Error saving settings: {err}")

    def apply_resolution(self, current_screen):
        """Applies the configured resolution to the display and returns the new screen.

        This method determines whether to use fullscreen or windowed mode and returns the updated surface.
        """
        desired_resolution = self.settings['resolution']
        if desired_resolution == "FULL":
            return pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        elif current_screen.get_size() != desired_resolution:
            return pygame.display.set_mode(desired_resolution)
        return pygame.display.set_mode(current_screen.get_size())


# -------------------------------
# Base for UI components (Component Pattern)
# -------------------------------
class UIComponent(ABC):
    def __init__(self):
        self.selected = False

    @abstractmethod
    def events(self, event):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self, surface):
        pass

# -------------------------------
# Slider Component (for volumes, etc.)
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

    def events(self, event):
        if event.type == pygame.KEYDOWN and self.selected:
            if event.key == pygame.K_a:
                self.value = max(self.min_value, self.value - self.step)
            elif event.key == pygame.K_d:
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
# Dropdown Component (e.g., for resolutions)
# -------------------------------
class Dropdown(UIComponent):
    def __init__(self, x, y, options, selected_index=0, font=None, text_color=(255, 255, 255)):
        super().__init__()
        self.x = x
        self.y = y
        self.options = options  # List of tuples (width, height)
        self.selected_index = selected_index
        self.text_color = text_color
        self.font = font
    def events(self, event):
        if event.type == pygame.KEYDOWN and self.selected:
            if event.key == pygame.K_a:
                self.selected_index = (self.selected_index - 1) % len(self.options)
            elif event.key == pygame.K_d:
                self.selected_index = (self.selected_index + 1) % len(self.options)

    def update(self):
        pass

    def render(self, surface):
        res = self.options[self.selected_index]
        if res == "FULL":
            option_text = _render_text_with_outline(self.font, "FULL", self.text_color, (0, 0, 0))
        else:
            option_text = _render_text_with_outline(self.font, f"{res[0]}x{res[1]}", self.text_color, (0, 0, 0))
        surface.blit(option_text, (self.x, self.y))
        surface.blit(option_text, (self.x, self.y))    
        if self.selected:
            rect = option_text.get_rect(topleft=(self.x, self.y))
            pygame.draw.rect(surface, (255, 255, 0), rect, 2)


# -------------------------------
# Button Component (using Command Pattern)
# -------------------------------
class Button(UIComponent):
    def __init__(self, x, y, text, callback, font=None, text_color=(255, 255, 255)):
        super().__init__()
        self.x = x
        self.y = y
        self.text = text
        self.callback = callback
        self.font = font
        self.text_color = text_color
        self.rect = None

    def events(self, event):
        if event.type == pygame.KEYDOWN and self.selected:
            if event.key == pygame.K_RETURN:
                self.callback()

    def update(self):
        pass

    def render(self, surface):
        text_surface = _render_text_with_outline(self.font, self.text, self.text_color, (0, 0, 0))
        self.rect = text_surface.get_rect(topleft=(self.x, self.y))
        surface.blit(text_surface, self.rect)
        if self.selected:
            pygame.draw.rect(surface, (255, 255, 0), self.rect, 2)

# -------------------------------
# Settings Screen
# -------------------------------
class SettingsScene(Scene, UINavigationMixin):
    def __init__(self, director, screen):
        super().__init__(director, screen)
        self.resources = ResourceManager()
        self.director = director
        self.screen = screen
        self.tit = self.resources.load_font(font, 36)
        self.font = self.resources.load_font(font, 30)
        self.minifont = self.resources.load_font(font, 24)
        self.settings = GameSettings()

        self.background_image = self.resources.load_image("settings.jpg")

        # Adjust component positions based on screen size
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # UI components created with factory
        self.title = _render_text_with_outline(self.tit, "SETTINGS", (255, 255, 255), (0, 0, 0))
        self.title_rect = self.title.get_rect(center=(screen_width // 2, screen_height // 8))

        self.music_slider = UIFactory.create_slider(
            screen_width // 2 + 180, screen_height // 4+10, 200, 20, self.settings.settings['music_volume']
        )

        self.fx_slider = UIFactory.create_slider(
            screen_width // 2 + 180, screen_height // 4 + 50, 200, 20, self.settings.settings['fx_volume']
        )

        self.resolution_options = [(800, 600), (1280, 720), (1024, 768), "FULL"]

        initial_index = self.resolution_options.index(self.settings.settings['resolution'])

        self.resolution_dropdown = UIFactory.create_dropdown(
            screen_width // 2 + 160, screen_height // 4 + 100, self.resolution_options, initial_index, self.minifont, (255, 255, 0)
        )

        self.save_button = UIFactory.create_button(
            screen_width // 2 - 80, screen_height // 2 + 50, "SAVE", self.save_settings, self.font
        )

        self.back_button = UIFactory.create_button(
            screen_width // 2 - 80, screen_height // 2 + 100, "GO BACK", self.director.pop_scene, self.font
        )

        self.components = [
            self.music_slider,
            self.fx_slider,
            self.resolution_dropdown,
            self.save_button,
            self.back_button
        ]
        self.selected_index = 0

        self.update_selection(self.components)

    def update_selection(self, components):
        for i, comp in enumerate(self.components):
            comp.selected = (i == self.selected_index)

    def events(self, event):
        self.handle_ui_navigation(event, self.components)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.director.pop_scene()

    def update(self, delta_time):
        for comp in self.components:
            comp.update()
        pygame.mixer.music.set_volume(self.music_slider.value)
        self.resources.set_fx_volume(self.fx_slider.value)

    def render(self, screen):
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Scale background to fill the screen
        scaled_background = pygame.transform.scale(self.background_image, screen.get_size())
        screen.blit(scaled_background, (0, 0))

        screen.blit(self.title, self.title_rect)

        # Labels (based on window size)
        screen.blit(_render_text_with_outline(self.font, "Music Volume", (255, 255, 0), (0, 0, 0)), (screen_width // 2 - 280, screen_height // 4))
        screen.blit(_render_text_with_outline(self.font, "FX Volume", (255, 255, 0), (0, 0, 0)), (screen_width // 2 - 280, screen_height // 4 + 50))
        screen.blit(_render_text_with_outline(self.font, "Resolution", (255, 255, 0), (0, 0, 0)), (screen_width // 2 - 280, screen_height // 4 + 100))

        for comp in self.components:
            comp.render(screen)

    def save_settings(self):
        """Saves settings and applies resolution/fullscreen."""
        self.settings.settings.update({
            'music_volume': self.music_slider.value,
            'fx_volume': self.fx_slider.value,
            'resolution': self.resolution_dropdown.options[self.resolution_dropdown.selected_index],
        })

        # Save settings to JSON file
        self.settings.save_settings()
        self.director.pop_scene()
        self.director.reload()

    def on_enter(self):
        """Called when the menu is activated."""
        pass

    def on_exit(self):
        """Called when the menu is deactivated."""
        pass


# -------------------------------
# Pause Menu
# -------------------------------
class PauseMenu(Scene, UINavigationMixin):
    def __init__(self, director, screen):
        super().__init__(director, screen)
        self.screen = screen
        self.director = director
        self.resources = ResourceManager()
        self.background = None
        self.selected_index = 0
        self.blur_strength = 4
        self.titfont = self.resources.load_font(font, 40)
        self.font = self.resources.load_font(font, 30)
        self._create_buttons()

    def _create_buttons(self):
        button_width = 200
        start_y = self.screen.get_height() // 2 - 100  # Centering vertically
        spacing = 80

        self.buttons = [
            UIFactory.create_button(
                x=self.screen.get_width() // 2 - button_width // 1.3,
                y=start_y,
                text="Continue",
                callback=self.director.pop_scene,
                font=self.font,
                text_color=(255, 255, 0)
            ),
            UIFactory.create_button(
                x=self.screen.get_width() // 2 - button_width // 1.3,
                y=start_y + spacing,
                text="Retry",
                callback=self._restart_level,
                font=self.font,
                text_color=(255, 255, 0)
            ),
            UIFactory.create_button(
                x=self.screen.get_width() // 2 - button_width // 1.3,
                y=start_y + spacing * 2,
                text="Settings",
                callback=self._open_settings,
                font=self.font,
                text_color=(255, 255, 0)
            ),
            UIFactory.create_button(
                x=self.screen.get_width() // 2 - button_width,
                y=start_y + spacing * 3,
                text="Back to menu",
                callback=self._return_to_main_menu,
                font=self.font,
                text_color=(255, 255, 0)
            )
        ]
        self.update_selection(self.buttons)

    def on_resolution_change(self, screen):
        """Called when resolution changes and updates the UI."""
        self.screen = screen
        self._create_buttons()  # Recalculate button positions

    def capture_background(self, background_surface):
        """Captures and applies blur effect to the background"""
        scaled = pygame.transform.smoothscale(
            background_surface,
            (background_surface.get_width() // self.blur_strength,
             background_surface.get_height() // self.blur_strength)
        )
        self.background = pygame.transform.smoothscale(scaled, background_surface.get_size())
        tint = pygame.Surface(self.background.get_size())
        tint.fill((0, 0, 0))
        tint.set_alpha(150)
        self.background.blit(tint, (0, 0))

    def render(self, screen):
        if self.background:
            screen.blit(self.background, (0, 0))
        title = _render_text_with_outline(self.titfont, "PAUSE", (255, 255, 255), (0, 0, 0))
        title_rect = title.get_rect(center=(screen.get_width() // 2, 100))
        screen.blit(title, title_rect)
        for btn in self.buttons:
            btn.render(screen)


    def update(self, delta_time):
        for btn in self.buttons:
            btn.update()


    def events(self, event):
        self.handle_ui_navigation(event, self.buttons)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.director.pop_scene()

    def _open_settings(self):
        """Opens the settings menu"""
        self.director.push_scene("settings")

    def on_enter(self):
        """Called when the menu is activated."""
        pass

    def on_exit(self):
        """Called when the menu is deactivated."""
        pass

    def _return_to_main_menu(self):
        """Returns to the main menu"""
        self.director.restart_game()

    def _restart_level(self):
        """Restarts the current level"""
        self.director.pop_scene()
        self.director.restart_scene()


# -------------------------------
# Main Menu
# -------------------------------
class MenuScene(Scene, UINavigationMixin):
    def __init__(self, director, screen):
        super().__init__(director, screen)
        self.director = director
        self.screen = screen
        self.resources = ResourceManager()
        self.titfont = self.resources.load_font(font, 50)
        self.font = self.resources.load_font(font, 36)
        self.selected_index = 0
        self.background_image = self.resources.load_image("fondo_inicio.jpg")

        # Store relative values for repositioning elements
        self.title_y_ratio = 100 / screen.get_height()
        self.button_y_start_ratio = 200 / screen.get_height()
        self.button_y_spacing_ratio = 100 / screen.get_height()  # Example spacing

        # Initialize elements
        self._create_ui_elements()

        self.music = "menu.mp3"

    def _create_ui_elements(self):
        # Recalculate position and sizes based on current screen size.
        screen_width, screen_height = self.screen.get_size()
        self.title = _render_text_with_outline(self.titfont, "ÑEMBI SURVIVOR", (255, 255, 0), (0, 0, 0))
        self.title_rect = self.title.get_rect(center=(screen_width // 2, int(self.title_y_ratio * screen_height)))

        # Relative position for buttons
        btn_x = screen_width // 2 - 100  # You can make it relative too
        btn_y = int(self.button_y_start_ratio * screen_height)
        spacing = int(self.button_y_spacing_ratio * screen_height)
        self.buttons = [
            UIFactory.create_button(btn_x, btn_y, "PLAY", self.start_game, self.font),
            UIFactory.create_button(btn_x, btn_y + spacing, "SETTINGS", self.open_settings, self.font),
            UIFactory.create_button(btn_x, btn_y + spacing * 2, "HOW TO PLAY", self.open_instructions, self.font),
            UIFactory.create_button(btn_x, btn_y + spacing * 3, "EXIT", self.quit_game, self.font)
        ]
        # Update initial button selection
        self.update_selection(self.buttons)

    def update_selection(self, components):
        for i, btn in enumerate(components):
            btn.selected = (i == self.selected_index)

    def events(self, event):
        self.handle_ui_navigation(event, self.buttons)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.quit_game()

    def update(self, delta_time):
        pass

    def render(self, screen):
        scaled_background = pygame.transform.scale(self.background_image, screen.get_size())
        screen.blit(scaled_background, (0, 0))
        screen.blit(self.title, self.title_rect)
        for btn in self.buttons:
            btn.render(screen)

    def _load_music(self):
        pygame.mixer.music.stop()
        pygame.time.wait(35)
        music_path = self.resources.load_music(self.music)
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)

    def on_enter(self):
        self._load_music()

    def on_exit(self):
        pygame.mixer.music.stop()

    def start_game(self):
        self.director.push_scene("fase1")

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def open_settings(self):
        self.director.push_scene("settings")

    def open_instructions(self):
        self.director.push_scene("instructions")

    def on_resolution_change(self, screen):
        """Called when resolution changes. Recalculates the UI layout."""
        self.screen = screen
        self._create_ui_elements()  # Recalculate positions and sizes
        self.render(screen)


# -------------------------------
# Death Scene
# -------------------------------
class LoseScene(Scene,UINavigationMixin):
    def __init__(self, director,screen):
        super().__init__(director,screen)
        self.director = director
        self.screen = screen
        self.resources = ResourceManager()
        self.titfont = self.resources.load_font(font, 28)
        self.font = self.resources.load_font(font, 24)
        self.selected_index = 0

        # UI initialization
        self.title = _render_text_with_outline(self.titfont,"Accept your faith, Ñembi",(255,255,0),(0,0,0))
        self.title_rect = self.title.get_rect(center=(self.screen.get_width() // 2, 110))

        self.subtitle = _render_text_with_outline(self.font,
                                               "We will see you in July :)",
                                               (255, 255, 0), (0, 0, 0))
        self.subtitle_rect = self.subtitle.get_rect(center=(self.screen.get_width() // 2, 160))

        btn_x = self.screen.get_width() // 2 - 200
        self.buttons = [
            UIFactory.create_button(btn_x, self.screen.get_height()//2.5, "Play again", self.goto, self.titfont, (255, 255, 0)),
            UIFactory.create_button(btn_x+100, self.screen.get_height()//2, "Exit", self._return_to_main_menu, self.titfont, (255, 255, 0)),
        ]
        self.update_selection(self.buttons)
        self.blur_strength = 4
        self.music = "lose.mp3"
        self.background = self.resources.load_image("lose.jpg")

    def update_selection(self,component):
        for i, btn in enumerate(self.buttons):
            btn.selected = (i == self.selected_index)

    def events(self, event):
        self.handle_ui_navigation(event, self.buttons)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.director.quit_game()

    def update(self, delta_time):
        pass

    def _load_music(self):
        """Loads and plays menu music."""
        pygame.mixer.music.stop()
        pygame.time.wait(35)
        music_path = self.resources.load_music(self.music)
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)

    def on_enter(self):
        """Called when the menu is activated."""
        self._load_music()

    def on_exit(self):
        """Called when the menu is deactivated."""
        pygame.mixer.music.stop()

    def render(self, screen):
        if self.background:
            scaled_background = pygame.transform.scale(self.background, screen.get_size())
            screen.blit(scaled_background, (0, 0))
        screen.blit(self.title, self.title_rect)
        screen.blit(self.subtitle, self.subtitle_rect)
        for btn in self.buttons:
            btn.render(screen)


    def goto(self):
        self.director.pop_scene()
        self.director.restart_scene()

    def _return_to_main_menu(self):
        """Returns to the main menu"""
        self.director.restart_game()

# -------------------------------
# Win Scene
# -------------------------------
class WinScene(Scene,UINavigationMixin):
    def __init__(self, director,screen):
        super().__init__(director,screen)
        self.director = director
        self.screen = screen
        self.resources = ResourceManager()
        self.font = self.resources.load_font(font, 24)
        self.selected_index = 0

        # UI initialization
        self.title = _render_text_with_outline(self.font,"¡Congratulations, you save the FIC!",(255,255,0),(0,0,0))
        self.title_rect = self.title.get_rect(center=(self.screen.get_width() // 2, 110))

        btn_x = self.screen.get_width() // 2 - 120
        self.buttons = [
            UIFactory.create_button(btn_x, 230, "Play again", self._return_to_main_menu, self.font, (255, 255, 0)),
            UIFactory.create_button(btn_x + 50, 300, "Exit", self._exit, self.font, (255, 255, 0)),
        ]
        self.update_selection(self.buttons)
        self.background = self.resources.load_image("win.jpg")
        self.music = "win.mp3"
    def update_selection(self,component):
        for i, btn in enumerate(self.buttons):
            btn.selected = (i == self.selected_index)

    def events(self, event):
        self.handle_ui_navigation(event, self.buttons)
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.director.quit_game()

    def update(self, delta_time):
        pass


    def _load_music(self):
        """Loads and plays menu music."""
        pygame.mixer.music.stop()
        pygame.time.wait(35)
        music_path = self.resources.load_music(self.music)
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)

    def on_enter(self):
        """Called when the menu is activated."""
        self._load_music()

    def on_exit(self):
        """Called when the menu is deactivated."""
        pygame.mixer.music.stop()

    def render(self, screen):
        if self.background:
            scaled_background = pygame.transform.scale(self.background, screen.get_size())
            screen.blit(scaled_background, (0, 0))
        screen.blit(self.title, self.title_rect)
        for btn in self.buttons:
            btn.render(screen)

    def _exit(self):
        pygame.quit()
        sys.exit()

    def _return_to_main_menu(self):
        """Returns to the main menu"""
        while len(self.director.scene_stack) > 1:
            self.director.pop_scene()
        self.director.push_scene("menu")


class InstructionsScene(Scene):
    def __init__(self, director, screen):
        super().__init__(director, screen)
        self.resources = ResourceManager()
        self.director = director
        self.screen = screen
        self.font = self.resources.load_font("PressStart2P-Regular.ttf", 24)
        self.title_font = self.resources.load_font("PressStart2P-Regular.ttf", 36)
        self.background_image = self.resources.load_image("fondo_inicio.jpg")

        self.instructions = [
            "HOW TO PLAY",
            "",
            "WASD - Move",
            "E - Use Shield (once per level)",
            "SPACE - Attack",
            "P - Pause Menu"
        ]

    def events(self, event):
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.director.pop_scene()

    def update(self, delta_time):
        pass

    def render(self, screen):
        screen_width = self.screen.get_width()
        screen_height = self.screen.get_height()

        # Scale background to fill the screen
        scaled_background = pygame.transform.scale(self.background_image, screen.get_size())
        screen.blit(scaled_background, (0, 0))

        # Render title with outline
        title_surface = _render_text_with_outline(self.title_font, self.instructions[0], (255, 255, 255), (0, 0, 0))
        title_rect = title_surface.get_rect(center=(screen_width // 2, screen_height // 8))
        screen.blit(title_surface, title_rect)

        # Render instructions with outline
        for i, line in enumerate(self.instructions[1:], start=1):
            if line:  # Only render non-empty lines
                text_surface = _render_text_with_outline(self.font, line, (255, 255, 255), (0, 0, 0))
                text_rect = text_surface.get_rect(center=(screen_width // 2, screen_height // 8 + i * 40))
                screen.blit(text_surface, text_rect)

    def on_enter(self):
        """Called when the scene is activated."""
        pass

    def on_exit(self):
        """Called when the scene is deactivated."""
        pass

def _render_text_with_outline(font, text, text_color, outline_color, outline_width=2):
    base = font.render(text, True, text_color)
    outline = font.render(text, True, outline_color)
    w = base.get_width() + 2 * outline_width
    h = base.get_height() + 2 * outline_width
    img = pygame.Surface((w, h), pygame.SRCALPHA)
    img.blit(outline, (0, 0))
    img.blit(outline, (2 * outline_width, 0))
    img.blit(outline, (0, 2 * outline_width))
    img.blit(outline, (2 * outline_width, 2 * outline_width))
    img.blit(base, (outline_width, outline_width))
    return img