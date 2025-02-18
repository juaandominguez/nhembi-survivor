import pygame
import random
from pygame.locals import *

ANIMATION_INTERVAL = 200  # ms between frames


class Player:
    def __init__(self, x, y, speed):
        self.sprite_sheet = pygame.image.load('sprites/thiagic/walk.png').convert_alpha()
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
