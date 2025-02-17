import pygame
import random

class Enemy:
    def __init__(self, enemy_type, x, y, speed):
        """
        Crea un enemigo con un tipo específico, posición inicial y velocidad.
        """
        self.enemy_type = enemy_type
        self.speed = speed
        self.sprite_sheet = pygame.image.load(f'sprites/enemies/enemy_{enemy_type}/walk.png').convert_alpha()
        
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

    def load_frames(self, row, frame_count):
        """
        Carga los frames desde la hoja de sprites.
        """
        frame_width = self.sprite_sheet.get_width() // 8
        frame_height = self.sprite_sheet.get_height() // 4
        frames = []

        for i in range(frame_count):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(self.sprite_sheet, (0, 0), (i * frame_width, row * frame_height, frame_width, frame_height))
            frames.append(pygame.transform.scale(frame, (frame_width * 2, frame_height * 2)))

        return frames

    def move_towards(self, player):
        """
        Mueve al enemigo hacia el jugador con su velocidad configurada.
        """
        dx, dy = player.rect.centerx - self.rect.centerx, player.rect.centery - self.rect.centery
        distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)

        self.rect.x += (dx / distance) * self.speed
        self.rect.y += (dy / distance) * self.speed

        # Cambiar dirección de la animación
        if abs(dx) > abs(dy):
            self.direction = "right" if dx > 0 else "left"
        else:
            self.direction = "down" if dy > 0 else "up"

    def animate(self):
        """
        Cambia el frame del enemigo para animarlo.
        """
        now = pygame.time.get_ticks()
        if now - self.last_update > 200:  # Cambia cada 200ms
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.frames[self.direction])
            self.image = self.frames[self.direction][self.current_frame]

    def update(self, player):
        """
        Actualiza la posición y animación del enemigo.
        """
        self.move_towards(player)
        self.animate()

    def draw(self, surface, camera):
        """
        Dibuja el enemigo en pantalla ajustado a la cámara.
        """
        surface.blit(self.image, camera.apply(self))
