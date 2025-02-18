import pygame
import random
from pygame.locals import *

ANIMATION_INTERVAL = 200  # ms between frames
ATTACK_COOLDOWN = 400    # Tiempo entre ataques en ms
ATTACK_ANIMATION_SPEED = 25  # Velocidad de la animación de ataque


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
        self.rect = self.image.get_rect()
        self.speed = speed
        self.moving = False
        self.observers = []

        # Ataque
        self.attack_sheet = pygame.image.load('sprites/thiagic/slash.png').convert_alpha()
        self.attack_frames = {
            "up": self.load_attack_frames(0),
            "left": self.load_attack_frames(1),
            "down": self.load_attack_frames(2),
            "right": self.load_attack_frames(3)
        }
        self.attacking = False
        self.attack_frame = 0
        self.last_attack_time = 0
        self.attack_direction = "down"
        self.attack_rect = pygame.Rect(0, 0, 0, 0)

    def load_attack_frames(self, row):
        """Carga 6 frames de ataque para una dirección específica"""
        frame_width = self.attack_sheet.get_width() // 6
        frame_height = self.attack_sheet.get_height() // 4
        frames = []
        
        for i in range(6):
            frame = pygame.Surface((frame_width, frame_height), pygame.SRCALPHA)
            frame.blit(self.attack_sheet, (0, 0), 
                      (i * frame_width, row * frame_height, frame_width, frame_height))
            scaled_frame = pygame.transform.scale(frame, (frame_width * 2, frame_height * 2))
            frames.append(scaled_frame)
        return frames

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
    
    def start_attack(self):
        """Inicia el ataque si no está en cooldown"""
        if not self.attacking and pygame.time.get_ticks() - self.last_attack_time > ATTACK_COOLDOWN:
            self.attacking = True
            self.attack_frame = 0
            self.last_attack_time = pygame.time.get_ticks()
            self.attack_direction = self.direction
            self.update_attack_hitbox()

    def update_attack_hitbox(self):
        """Actualiza el área de daño según la dirección sin mover al personaje"""
        offset = 10  # Distancia extra del área de ataque

        # Crear una copia del rectángulo original del personaje
        self.attack_rect = self.rect.copy()

        if self.attack_direction == "up":
            self.attack_rect.height += offset  # Aumentar la altura hacia arriba
            self.attack_rect.top -= offset  # Desplazar hacia arriba
        elif self.attack_direction == "down":
            self.attack_rect.height += offset  # Aumentar la altura hacia abajo
        elif self.attack_direction == "left":
            self.attack_rect.width += offset  # Aumentar el ancho hacia la izquierda
            self.attack_rect.left -= offset  # Desplazar hacia la izquierda
        else:  # right
            self.attack_rect.width += offset  # Aumentar el ancho hacia la derecha


    def handle_attack(self):
        """Maneja la progresión de la animación de ataque"""
        if self.attacking:
            if pygame.time.get_ticks() - self.last_update > ATTACK_ANIMATION_SPEED:
                self.last_update = pygame.time.get_ticks()
                self.attack_frame += 1
                
                if self.attack_frame >= len(self.attack_frames[self.attack_direction]):
                    self.attacking = False
                else:
                    self.update_attack_hitbox()

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

        if keys_pressed[K_SPACE]:
            self.start_attack()

        self.handle_attack()  # Actualizar animación de ataque

        self.animate()

    def draw(self, surface, camera):
        """Dibuja el personaje, su ataque y sus hitboxes."""
        if self.attacking:
            # Dibujar ataque (código existente)
            attack_pos = camera.apply_rect(self.attack_rect)
            surface.blit(self.attack_frames[self.attack_direction][self.attack_frame], attack_pos)
            
            # Dibujar hitbox de ataque (rojo)
            attack_hitbox_surface = pygame.Surface((self.attack_rect.width, self.attack_rect.height), pygame.SRCALPHA)
            attack_hitbox_surface.fill((255, 0, 0, 100))
            surface.blit(attack_hitbox_surface, attack_pos)
        else:
            # Dibujar personaje
            surface.blit(self.image, camera.apply(self))

        # --- CORRECCIÓN: Hitbox del personaje ajustado a la imagen ---
        # Obtener el área no transparente de la imagen actual
        image_bbox = self.image.get_bounding_rect()
        
        # Calcular posición relativa al rectángulo del jugador
        adjusted_rect = pygame.Rect(
            self.rect.x + image_bbox.x,
            self.rect.y + image_bbox.y,
            image_bbox.width,
            image_bbox.height
        )
        
        # Dibujar hitbox ajustado
        character_rect_pos = camera.apply_rect(adjusted_rect)
        hitbox_surface = pygame.Surface((image_bbox.width, image_bbox.height), pygame.SRCALPHA)
        hitbox_surface.fill((0, 255, 0, 100))
        surface.blit(hitbox_surface, character_rect_pos)
