import pygame
import random
from pygame.locals import *

from camera import Camera
from level import Level
from enemy import Enemy  # Importar la nueva clase Enemy

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
PLAYER_SPEED = 5
ANIMATION_INTERVAL = 200  # ms between frames
COLORS = {
    "grass": (76, 154, 42)
}

class Player:
    def __init__(self, x, y, speed):
        self.sprite_sheet = pygame.image.load('sprites/walk.png').convert_alpha()
        self.frames = {
            "down": self.load_frames(2, 3),
            "up": self.load_frames(0, 3),
            "left": self.load_frames(1, 3),
            "right": self.load_frames(3, 3)
        }
        self.direction = "down"
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.image = self.frames[self.direction][self.current_frame]
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = speed
        self.moving = False
        self.observers = []

    # Observer pattern functions
    def add_observer(self, observer):
        self.observers.append(observer)

    def notify_observers(self):
        for observer in self.observers:
            observer.update(self)

    def load_frames(self, row, frame_count):
        frame_width = self.sprite_sheet.get_width() // 8
        frame_height = self.sprite_sheet.get_height() // 4
        frames = []
        for i in range(frame_count):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(self.sprite_sheet, (0, 0), (i * frame_width, row * frame_height, frame_width, frame_height))
            frames.append(pygame.transform.scale(frame, (frame_width * 2, frame_height * 2)))
        return frames

    def animate(self):
        now = pygame.time.get_ticks()
        if self.moving:
            if now - self.last_update > ANIMATION_INTERVAL:
                self.last_update = now
                self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction])
        else:
            self.current_frame = 0
        self.image = self.frames[self.direction][self.current_frame]

    def move(self, keys_pressed, screen_width, screen_height):
        dx, dy = 0, 0
        self.moving = False

        if keys_pressed[K_w]:
            dy -= 1
        if keys_pressed[K_s]:
            dy += 1
        if keys_pressed[K_a]:
            dx -= 1
        if keys_pressed[K_d]:
            dx += 1

        # Normalizar la velocidad en diagonal
        if dx != 0 or dy != 0:
            self.moving = True
            length = (dx ** 2 + dy ** 2) ** 0.5  # Magnitud del vector
            dx = (dx / length) * self.speed
            dy = (dy / length) * self.speed

            # Actualizar dirección basada en movimiento
            if abs(dy) > abs(dx):
                self.direction = "down" if dy > 0 else "up"
            else:
                self.direction = "right" if dx > 0 else "left"

        # Actualizar posición con límites de pantalla
        self.rect.x = max(0, min(self.rect.x + dx, screen_width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y + dy, screen_height - self.rect.height))

        self.animate()

    def draw(self, surface, camera):
        surface.blit(self.image, camera.apply(self))


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Adventure Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.level = Level("./levels/level1.ldtk", "./levels/suelos.png")
        self.camera = Camera(self.level.width, self.level.height, SCREEN_WIDTH, SCREEN_HEIGHT)
        self.player = Player(
            x=SCREEN_WIDTH // 2,
            y=SCREEN_HEIGHT // 2,
            speed=PLAYER_SPEED
        )
        self.player.add_observer(self.camera)

        self.enemies = []
        self.spawn_enemies(10)  # Generar 10 enemigos al inicio

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False

    def spawn_enemies(self, count):
        """
        Genera enemigos en posiciones aleatorias.
        Asegura que solo haya un minotauro.
        """
        # Primero, genera el minotauro
        minotaur_x = random.randint(50, self.level.width - 50)
        minotaur_y = random.randint(50, self.level.height - 50)
        minotaur_speed = 0.8
        self.enemies.append(Enemy("minotaur", minotaur_x, minotaur_y, minotaur_speed))  # Minotauro lento

        # Luego genera los demás enemigos (alien o rat)
        for _ in range(count - 1):
            enemy_type = random.choice(["alien", "rat"])  # Elige entre alien y rat
            x = random.randint(50, self.level.width - 50)
            y = random.randint(50, self.level.height - 50)
            
            # Asignar diferentes velocidades a cada tipo de enemigo
            if enemy_type == "rat":
                speed = 3.0  # Ratas más rápidas
            else:
                speed = 1.5  # Aliens con velocidad intermedia

            self.enemies.append(Enemy(enemy_type, x, y, speed))

    def update(self):
        keys_pressed = pygame.key.get_pressed()
        self.player.move(keys_pressed, self.level.width, self.level.height)
        self.player.notify_observers()

        for enemy in self.enemies:
            enemy.update(self.player)

    def render(self):
        self.screen.fill(COLORS["grass"])
        self.level.draw(self.screen, self.camera)
        self.player.draw(self.screen, self.camera)

        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera)

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    game = Game()
    game.run()
