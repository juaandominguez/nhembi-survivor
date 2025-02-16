from Escenas.scene_abs import SceneAbs
class Level1Scene (SceneAbs):
    def __init__(self, screen, scene_manager):
        super().__init__(screen, scene_manager)
        self.screen = screen
        self.scene_manager = scene_manager
        self.level_started = True

    def setup(self):
        pass
    def cleanup(self):
        pass

    def update(self):
        pass

    def render(self):
        pass

    def handle_event(self, event):
        pass

    def handle_selection(self):
        print("Starting a new game")