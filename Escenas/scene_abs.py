from abc import ABC, abstractmethod

class SceneAbs(ABC):
    def __init__(self, screen, scene_manager):
        self.screen = screen
        self.scene_manager = scene_manager
        self.font = None

        self.title_text = None
        self.title_rect = None

        self.menu_options = []
        self.selected_option = 0
    @abstractmethod
    def setup(self):
        """Configura las escena: carga el mapa, enemigos, y objetos."""

        pass
    @abstractmethod
    def cleanup(self):
        """Limpia los recursos del nivel cuando se cambia de escena."""

        pass
    @abstractmethod
    def update(self):
        """Actualiza los elementos de la escena en cada frame."""

        pass
    @abstractmethod
    def render(self):
        """Dibuja los elementos en pantalla."""

        pass
    @abstractmethod
    def handle_event(self, event):
        """Maneja los eventos de entrada del jugador."""
        pass
    @abstractmethod
    def handle_selection(self):
        """Maneja la selección de opciones o interacciones dentro del nivel."""
        pass