class SceneManager:
    def __init__(self, screen):
        self.screen = screen
        self.scene_stack = []  # Almacena claves de escenas
        self.scenes = {}  # Registro de instancias de escenas
        self.scene_instances = {}  # Cache de instancias inicializadas

    def register_scene(self, scene_key, scene_class):
        """Registra una clase de escena con su clave"""
        self.scenes[scene_key] = scene_class

    def push_scene(self, scene_key):
        if self.scene_stack:
            current_scene = self.scene_stack[-1]
            if hasattr(current_scene, 'capture_background'):
                current_scene.capture_background()
        if scene_key not in self.scenes:
            raise ValueError(f"Escena no registrada: {scene_key}")

        # Crear instancia si no existe
        if scene_key not in self.scene_instances:
            self.scene_instances[scene_key] = self.scenes[scene_key](self.screen, self)

        # Pausar escena actual si existe
        if self.scene_stack:
            current = self.scene_stack[-1]
            self.scene_instances[current].pause()

        # Inicializar si es primera vez
        if not self.scene_instances[scene_key].initialized:
            self.scene_instances[scene_key].setup()
            self.scene_instances[scene_key].initialized = True

        self.scene_stack.append(scene_key)

    def pop_scene(self):
        """Desapila la escena actual"""
        if self.scene_stack:
            old_key = self.scene_stack.pop()
            self.scene_instances[old_key].pause()
            # Reanudar escena anterior si existe
            if self.scene_stack:
                new_current = self.scene_stack[-1]
                self.scene_instances[new_current].resume()
            return old_key
    def delete_scene_instance(self, scene_key):
        """Elimina una escena del registro"""
        if scene_key in self.scene_instances:
            del self.scene_instances[scene_key]

    def current_scene(self):
        """Obtiene la escena actual"""
        if not self.scene_stack:
            return None
        return self.scene_instances[self.scene_stack[-1]]

    def update(self):
        if scene := self.current_scene():
            scene.update()

    def render(self):
        # Renderizar todas las escenas desde la base hasta el tope
        for scene in self.scene_stack:
            self.scene_instances[scene].render()

    def handle_event(self, event):
        if scene := self.current_scene():
            scene.handle_event(event)