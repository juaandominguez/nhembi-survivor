from abc import ABC, abstractmethod

class SceneAbs(ABC):
    def __init__(self, screen, scene_manager):
        self.screen = screen
        self.scene_manager = scene_manager
        self.initialized = False

    @abstractmethod
    def setup(self):
        pass

    @abstractmethod
    def cleanup(self):
        pass

    def pause(self):
        pass

    def resume(self):
        pass

    @abstractmethod
    def handle_event(self, event):
        pass

    @abstractmethod
    def update(self):
        pass

    @abstractmethod
    def render(self):
        pass
