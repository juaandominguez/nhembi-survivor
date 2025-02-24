import pygame
import random
from pygame.locals import *
from resource_manager import ResourceManager
from Escenas.scene_abs import SceneAbs
from camera import Camera
from level import Level
from enemy import Enemy
from player import Player

# Constants (deberían estar en un archivo aparte, por ejemplo constants.py)
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
COLORS = {
    "grass": (76, 154, 42)
}


class NewGameScene(SceneAbs):
    def __init__(self, screen, scene_manager):
        super().__init__(screen, scene_manager)
        self.resources = ResourceManager()
        self._paused = False
        self.running = True
        self.level = None
        self.camera = None
        self.player = None
        self.enemies = []
        self.paused = False
        self.collision_tiles = []

    def setup(self):

        self.level = Level("./levels/pasilloFIC.ldtk")
        self.camera = Camera(self.level.width, self.level.height, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.collision_tiles = self.level.get_level_collisions()
        # Inicializar jugador
        self.player = Player(
            x=0,
            y=self.level.height// 2,
            speed=PLAYER_SPEED
        )
        self.player.add_observer(self.camera)

        # Generar enemigos
        self.spawn_enemies(0)

    def cleanup(self):
        """Limpia los recursos de la escena"""
        self.enemies.clear()
        self._paused = True
        self.player = None
        self.camera = None
        self.level = None

    def handle_event(self, event):
        """Maneja eventos específicos de la escena"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_p:
                self.pause()


    def update(self):
        """Actualiza la lógica del juego"""
        keys_pressed = pygame.key.get_pressed()

        # Actualizar jugador
        if self.player:
            self.player.move(keys_pressed, self.level.width, self.level.height, self.collision_tiles)
            self.player.notify_observers()

        # Actualizar enemigos
        for enemy in self.enemies:
            enemy.update(self.player, self.collision_tiles)

    def render(self):
        """Renderiza la escena"""
        if not self.level or not self.player:
            return

        # Limpiar pantalla
        self.screen.fill(COLORS["grass"])

        # Dibujar nivel
        self.level.draw(self.screen, self.camera)

        # Dibujar jugador
        self.player.draw(self.screen, self.camera)

        # Dibujar enemigos
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)

    def spawn_enemies(self, count):
        """Genera enemigos en posiciones aleatorias"""
        if not self.level:
            return

        # Generar minotauro
        minotaur_x = random.randint(50, self.level.width - 50)
        minotaur_y = random.randint(50, self.level.height - 50)
        self.enemies.append(Enemy("minotaur", minotaur_x, minotaur_y, 0.8))

        # Generar otros enemigos
        for _ in range(count - 1):
            enemy_type = random.choice(["alien", "rat"])
            x = random.randint(50, self.level.width - 50)
            y = random.randint(50, self.level.height - 50)
            speed = 3.0 if enemy_type == "rat" else 1.5
            self.enemies.append(Enemy(enemy_type, x, y, speed))

    def handle_selection(self):
        """Maneja la lógica de selección (requerido por SceneAbs)"""
        print("Selection handled in NewGameScene")

    def pause(self):
        print("Juego pausado")
        self._paused = True
        pygame.mixer.music.pause()
        self.scene_manager.push_scene("pause")
        self.scene_manager.current_scene().capture_background(self.screen)

    def resume(self):
        print("Juego reanudado")
        self._paused = False
        pygame.mixer.music.unpause()

        # Reanudar música/temporizadores si es necesario