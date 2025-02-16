import pygame
from pygame.locals import *

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
            # "down": self.load_frames(0, 3),
            "down": self.load_frames(2, 3),
            # "up": self.load_frames(1, 3),
            "up": self.load_frames(0, 3),
            # "left": self.load_frames(2, 3),
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
            dy -= self.speed
        if keys_pressed[K_s]:
            dy += self.speed
        if keys_pressed[K_a]:
            dx -= self.speed
        if keys_pressed[K_d]:
            dx += self.speed

        # Update position with boundary checking
        self.rect.x = max(0, min(self.rect.x + dx, screen_width - self.rect.width))
        self.rect.y = max(0, min(self.rect.y + dy, screen_height - self.rect.height))

        # Update direction based on movement
        if dx != 0 or dy != 0:
            self.moving = True
            if dy > 0:
                self.direction = "down"
            elif dy < 0:
                self.direction = "up"
            elif dx < 0:
                self.direction = "left"
            elif dx > 0:
                self.direction = "right"

        self.animate()

    def draw(self, surface):
        surface.blit(self.image, self.rect)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Adventure Game")
        self.clock = pygame.time.Clock()
        self.running = True
        self.player = Player(
            x=SCREEN_WIDTH // 2,
            y=SCREEN_HEIGHT // 2,
            speed=PLAYER_SPEED
        )

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == QUIT:
                self.running = False

    def update(self):
        keys_pressed = pygame.key.get_pressed()
        self.player.move(keys_pressed, SCREEN_WIDTH, SCREEN_HEIGHT)

    def render(self):
        self.screen.fill(COLORS["grass"])
        self.player.draw(self.screen)
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