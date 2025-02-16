import pygame
from abc import ABC, abstractmethod

class CinematicAbs(ABC):
    def __init__(self, screen, scene_manager):
        self.screen = screen
        self.scene_manager = scene_manager
        self.frames = []
        self.dialogues = []
        self.current_frame = 0
        self.timer = 0
        self.font = pygame.font.Font(None, 24)

        self.cinematic_active = True

    @abstractmethod
    def setup(self):
        """Carga los frames, sonidos y diálogos de la cinemática."""
        pass

    @abstractmethod
    def cleanup(self):
        """Limpia recursos al finalizar la cinemática."""
        pass

    @abstractmethod
    def update(self, delta_time):
        """Actualiza la cinemática según el tiempo transcurrido."""
        pass

    @abstractmethod
    def render(self):
        """Dibuja la cinemática en pantalla."""
        pass

    @abstractmethod
    def handle_event(self, event):
        """Maneja entrada del usuario (ej. saltar cinemática)."""
        pass
