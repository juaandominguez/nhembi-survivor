# -*- coding: utf-8 -*-
import math
import pygame
import json
from menu import GameSettings,_render_text_with_outline
from scene import Scene
from characters import Rat, Alien, Minotaur, Skeleton, Zombie, Reptilian, Frank, Fatty, Nhembitron, Player, GunTurret
from pygame.locals import *
from level import Level
from camera import Camera
from resource_manager import ResourceManager
from minimap import MiniMap
from items import Coin, Tortilla

font = "PressStart2P-Regular.ttf"
# -------------------------------------------------
# Class LevelConfigLoader: Responsible for loading level configuration
class LevelConfigLoader:
    @staticmethod
    def load_config(config_name, config_file="levels_config.json"):
        with open(config_file) as f:
            configs = json.load(f)
        return configs[config_name]

# -------------------------------------------------
# Class EnemyFactory: Creates enemy instances based on their type
class EnemyFactory:
    ENEMY_MAP = {
        "Rat": Rat,
        "Alien": Alien,
        "Minotaur": Minotaur,
        "Skeleton": Skeleton,
        "Zombie": Zombie,
        "Reptilian": Reptilian,
        "Frank": Frank,
        "Fatty": Fatty,
        "Nhembitron": Nhembitron,
        "GunTurret": GunTurret,  # Add GunTurret to the enemy map
    }

    @staticmethod
    def create_enemy(enemy_type, position):
        enemy_class = EnemyFactory.ENEMY_MAP.get(enemy_type)
        if enemy_class is None:
            raise ValueError(f"Unknown type of enemy: {enemy_type}")
        enemy = enemy_class()
        enemy.set_position(position)
        return enemy

# -------------------------------------------------
# Class MusicManager: Handles music loading and playback
class MusicManager:
    def __init__(self):
        pygame.mixer.music.stop()
        self.music_channel = pygame.mixer.Channel(0)

    @staticmethod
    def play_music(resources, music_file):
        pygame.mixer.music.stop()  # Stop previous music
        pygame.time.wait(35)       # Pause to avoid glitches
        music_path = resources.load_music(music_file)
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.play(-1)

    def update_music_pan(self, screen_width, player_x):
        if self.music_channel is None:
            return
        # Calculate the ratio: 0 (player on the left) to 1 (player on the right)
        ratio = player_x / screen_width
        # Set volume: higher on the left if ratio is low, and vice versa
        left_vol = max(0.0, min(1.0, 1.0 - ratio))
        right_vol = max(0.0, min(1.0, ratio))
        self.music_channel.set_volume(left_vol, right_vol)

# -------------------------------------------------
# Class Fase
class Fase(Scene):
    def __init__(self, director, screen, config_name):
        super().__init__(director, screen)
        self.screen = screen
        # Load level configuration using LevelConfigLoader
        self.config = LevelConfigLoader.load_config(config_name)
        self.config_name = config_name
        self.resources = ResourceManager()
        self.font = self.resources.load_font(font, 24)
        self.count_font = self.resources.load_font(font, 36)
        # Initialize the level
        self.level = Level(self.config["level_file"])
        # Configure the camera using GameSettings
        settings = GameSettings()

        xres = pygame.display.Info().current_w  if settings.settings['resolution'] == "FULL" else settings.settings['resolution'][0]
        yres =  pygame.display.Info().current_h  if settings.settings['resolution'] == "FULL" else settings.settings['resolution'][1]
        self.camera = Camera(
            self.level.width,
            self.level.height,
            xres,
            yres
        )
        self.minimap_width = 200
        self.minimap_height = 150

        minimap_x = xres - self.minimap_width - 20
        minimap_y = 20
        self.minimap = MiniMap(
            minimap_x,
            minimap_y,
            self.minimap_width,
            self.minimap_height,
            self.level.width,
            self.level.height
        )

        # Add help text timing
        self.show_help_text = True
        self.help_text_timer = 5000  # Show for 5 seconds
        self.help_text_start = pygame.time.get_ticks()

        # Configure collisions
        self.collisionTiles = self.level.get_level_collisions()
        self.groupTiles = pygame.sprite.Group()
        for tile in self.collisionTiles:
            self.groupTiles.add(Obstacle(tile))

        # Cache level details for minimap to avoid recalculating every frame
        self.minimap_level_details = {
            'collision_rects': self.collisionTiles,
        }

        # Add performance optimization flags
        self.large_map = self.level.width > 3000 or self.level.height > 3000
        self.update_frequency = 1  # Update every frame by default
        if self.large_map:
            self.update_frequency = 2  # Update every 2 frames

        self.current_frame = 0
        self.enemy_positions_cache = []
        self.last_enemy_update = 0
        self.enemy_update_interval = 100  # ms

        # Configure player
        self.jugador = Player()
        self.grupoJugador = pygame.sprite.Group(self.jugador)
        self.jugador.set_position(tuple(self.config["player_start"]))

        # Configure enemies
        self.grupoEnemigos = pygame.sprite.Group()
        self.grupoTurrets = pygame.sprite.Group()  # New group for turrets
        self.grupoBullets = pygame.sprite.Group()  # New group for bullets
        self.grupoSpritesDinamicos = pygame.sprite.Group(self.jugador)
        enemy_config = self.config["enemies"]
        enemy_types = enemy_config.get("types", [])
        enemy_positions = enemy_config.get("positions", [])

        if len(enemy_types) != len(enemy_positions):
            raise ValueError("The 'types' and 'positions' lists must have the same length.")

        for enemy_type, position in zip(enemy_types, enemy_positions):
            enemy = EnemyFactory.create_enemy(enemy_type, position)
            if isinstance(enemy, GunTurret):
                self.grupoTurrets.add(enemy)
            else:
                self.grupoEnemigos.add(enemy)
            self.grupoSpritesDinamicos.add(enemy)

        # General sprite group (player, enemies, and turrets)
        self.grupoSprites = pygame.sprite.Group(self.jugador, *self.grupoEnemigos, *self.grupoTurrets)

        self.grupoTortillas = pygame.sprite.Group()
        if "tortillas" in self.config:
            for pos in self.config["tortillas"]["positions"]:
                tortilla = Tortilla(pos)
                self.grupoTortillas.add(tortilla)
                self.grupoSprites.add(tortilla)

        self.grupoMonedas = pygame.sprite.Group()
        if "coins" in self.config:
            for pos in self.config["coins"]["positions"]:
                coin = Coin(pos)
                self.grupoMonedas.add(coin)
                self.grupoSprites.add(coin)

        self.end_level = self.config["coins"]["positions"].__len__()

        # Configure next level and music
        self.next_level = self.config.get("next_level", None)
        self.music = self.config.get("music", None)
        if self.music:
            self.musicmgr = MusicManager()
            self.musicmgr.play_music(self.resources, self.music)

        # Configure health bar and coins
        self.health_bar = HealthBar(10, 10, 250, 30, self.jugador.health)
        self.coin_bar = CoinBar(10, 50)

        # --- Countdown and visual effect configuration ---
        self.countdown_active = True
        self.countdown_duration = 3000
        self.countdown_start = None
        self.max_circle_radius = math.hypot(self.screen.get_width(), self.screen.get_height())

    def on_enter(self):
        """Called when the phase is activated (push)."""
        if self.music:
            MusicManager.play_music(self.resources, self.music)
        # Start the countdown and visual effect
        self.countdown_start = pygame.time.get_ticks()
        self.countdown_active = True

    def on_exit(self):
        """Called when the phase is deactivated (pop)."""
        pygame.mixer.music.stop()

    def update(self, tiempo):
        # If the countdown is active, do not update movements or collisions
        if self.countdown_active:
            current_time = pygame.time.get_ticks()
            if current_time - self.countdown_start >= self.countdown_duration:
                self.countdown_active = False
            return  # Exit without updating game logic

        # Normal game update (no longer in countdown)
        self.current_frame += 1
        full_update = (self.current_frame % self.update_frequency == 0)
        current_time = pygame.time.get_ticks()
        if self.show_help_text and current_time - self.help_text_start > self.help_text_timer:
            self.show_help_text = False

        if current_time - self.last_enemy_update > self.enemy_update_interval or not self.enemy_positions_cache:
            self.enemy_positions_cache = []
            for enemigo in self.grupoEnemigos:
                self.enemy_positions_cache.append((enemigo.rect.centerx, enemigo.rect.centery))
            self.last_enemy_update = current_time

        if self.large_map and len(self.grupoEnemigos) > 30:
            subset_size = len(self.grupoEnemigos) // 3
            start_idx = (self.current_frame % 3) * subset_size
            end_idx = min(start_idx + subset_size, len(self.grupoEnemigos))
            active_enemies = list(self.grupoEnemigos)[start_idx:end_idx]
            for enemigo in active_enemies:
                enemigo.move_cpu(self.jugador)
                if pygame.sprite.collide_rect_ratio(0.5)(self.jugador, enemigo):
                    if enemigo.current_action != 'hurt':
                        enemigo.attack()
                        self.jugador.take_damage(enemigo.get_damage())
        else:
            for enemigo in self.grupoEnemigos:
                enemigo.move_cpu(self.jugador)
                if pygame.sprite.collide_rect_ratio(0.5)(self.jugador, enemigo):
                    if enemigo.current_action != 'hurt':
                        enemigo.attack()
                        self.jugador.take_damage(enemigo.get_damage())

        for sprite in self.grupoSpritesDinamicos:
            if not isinstance(sprite, GunTurret):
                sprite.update(self.groupTiles, tiempo)

        for turret in self.grupoTurrets:
            turret.update(self.groupTiles, tiempo, self.jugador)
            for bullet in turret.gun.bullets:
                dx = bullet.position[0] - self.jugador.position[0]
                dy = bullet.position[1] - self.jugador.position[1]
                distance = (dx ** 2 + dy ** 2) ** 0.5
                if distance < 40:
                    self.jugador.take_damage(bullet.damage)
                    bullet.kill()

        if self.jugador.attack_in_progress:
            enemies_hit = pygame.sprite.spritecollide(
                self.jugador,
                self.grupoEnemigos,
                False,
                collided=pygame.sprite.collide_rect_ratio(1)
            )
            for enemy in enemies_hit:
                enemy.take_damage(1)

        self.camera.update(self.jugador)

        for enemy in list(self.grupoEnemigos):
            if not enemy.alive():
                self.grupoEnemigos.remove(enemy)
                self.grupoSpritesDinamicos.remove(enemy)
                self.grupoSprites.remove(enemy)

        tortillas_collected = pygame.sprite.spritecollide(self.jugador, self.grupoTortillas, dokill=True)
        for tortilla in tortillas_collected:
            self.jugador.heal()
            tortilla.make_sound()

        coins_collected = pygame.sprite.spritecollide(self.jugador, self.grupoMonedas, dokill=True)
        for coin in coins_collected:
            self.jugador.gain_coins(1)
            coin.make_sound()
        self.grupoMonedas.update()

        if self.jugador.health <= 0:
            self.director.push_scene("lose")
        else:
            self.health_bar.update(self.jugador.health)

        self.coin_bar.update(self.jugador.coins)
        if self.jugador.coins >= self.end_level:
            if self.next_level == "win":
                self.director.push_scene(self.next_level)
            else:
                self.director.change_scene(self.next_level)

        self.jugador.update_invincibility()
        self.musicmgr.update_music_pan(self.screen.get_width(), self.jugador.rect.centerx)

    def render_game(self, pantalla):
        # Full scene rendering (level, sprites, HUD, minimap, etc.)
        pantalla.fill((0, 0, 0))
        self.level.draw(pantalla, self.camera)

        if self.large_map and len(self.grupoSprites) > 100:
            camera_rect = pygame.Rect(self.camera.camera_rect.x, self.camera.camera_rect.y,
                                      self.camera.screen_width, self.camera.screen_height)
            buffer = 100
            visible_area = pygame.Rect(camera_rect.x - buffer, camera_rect.y - buffer,
                                       camera_rect.width + buffer * 2, camera_rect.height + buffer * 2)
            for sprite in self.grupoSprites:
                if visible_area.colliderect(sprite.rect):
                    pantalla.blit(sprite.image, self.camera.apply(sprite))
            for turret in self.grupoTurrets:
                if visible_area.colliderect(turret.rect):
                    for bullet in turret.gun.bullets:
                        if visible_area.colliderect(bullet.rect):
                            pantalla.blit(bullet.image, self.camera.apply(bullet))
        else:
            for sprite in self.grupoSprites:
                pantalla.blit(sprite.image, self.camera.apply(sprite))
            for turret in self.grupoTurrets:
                for bullet in turret.gun.bullets:
                    pantalla.blit(bullet.image, self.camera.apply(bullet))

        if not self.countdown_active:
            self.health_bar.render(pantalla)
            self.coin_bar.render(pantalla)

        if self.minimap.visible:
            if not self.enemy_positions_cache:
                enemy_positions = [(enemy.rect.centerx, enemy.rect.centery) for enemy in self.grupoEnemigos]
            else:
                enemy_positions = self.enemy_positions_cache

            tortilla_positions = []
            if self.large_map:
                tortilla_limit = min(10, len(self.grupoTortillas))
                for i, tortilla in enumerate(self.grupoTortillas):
                    if i >= tortilla_limit:
                        break
                    tortilla_positions.append(tortilla.rect.midbottom)
            else:
                tortilla_positions = [tortilla.rect.midbottom for tortilla in self.grupoTortillas]

            screen_size = (pantalla.get_width(), pantalla.get_height())
            self.minimap.draw(
                pantalla,
                (self.jugador.rect.centerx, self.jugador.rect.centery),
                enemy_positions,
                tortilla_positions,
                screen_size,
                self.minimap_level_details
            )

        if self.show_help_text:
            help_text = self.font.render("Press 'M' to toggle minimap", True, (255, 255, 255))
            text_rect = help_text.get_rect(center=(pantalla.get_width() // 2, 50))
            shadow = self.font.render("Press 'M' to toggle minimap", True, (0, 0, 0))
            shadow_rect = shadow.get_rect(center=(pantalla.get_width() // 2 + 2, 52))
            pantalla.blit(shadow, shadow_rect)
            pantalla.blit(help_text, text_rect)

        if self.jugador.invincible:
            shield_rect = self.jugador.shield_image.get_rect(center=self.camera.apply(self.jugador).center)
            pantalla.blit(self.jugador.shield_image, shield_rect)

    def render(self, pantalla):
        # First, render the full scene
        self.render_game(pantalla)

        # If the countdown is active, apply the overlay with the expanding circle and counter
        if self.countdown_active:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.countdown_start
            seconds_left = math.ceil((self.countdown_duration - elapsed) / 1000)
            radius = (elapsed / self.countdown_duration) * self.max_circle_radius

            # Create the overlay with alpha channel
            overlay = pygame.Surface(pantalla.get_size(), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 255))
            # "Cut" a transparent circle centered on the player
            pygame.draw.circle(overlay, (0, 0, 0, 0), self.jugador.rect.center, int(radius))
            pantalla.blit(overlay, (0, 0))

            # Draw the counter in the center
            text_surface = _render_text_with_outline(self.count_font, str(seconds_left), (255, 255, 255), (0, 0, 0))
            text_rect = text_surface.get_rect(center=(pantalla.get_width() // 2, pantalla.get_height() // 2))
            pantalla.blit(text_surface, text_rect)

    def events(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == K_p:
                self.director.push_scene("pause")
            elif event.key == K_m:
                self.minimap.toggle_visibility()
            elif event.key == K_e:
                self.jugador.activate_invincibility()

        teclasPulsadas = pygame.key.get_pressed()
        if not self.countdown_active:
            self.jugador.move(teclasPulsadas, K_w, K_s, K_a, K_d, K_SPACE)

    def on_resolution_change(self, screen):
        self.screen = screen
        self.camera = Camera(
            self.level.width,
            self.level.height,
            screen.get_width(),
            screen.get_height()
        )
        self.minimap = MiniMap(
            screen.get_width() - self.minimap_width - 20,
            20,
            self.minimap_width,
            self.minimap_height,
            self.level.width,
            self.level.height
        )


# -------------------------------------------------
# Class Obstacle: Represents solid objects for collisions
class Obstacle(pygame.sprite.Sprite):
    def __init__(self, rectangle):
        super().__init__()
        self.rect = rectangle
        # Empty image for efficiency
        self.image = pygame.Surface((0, 0))

# -------------------------------------------------
# Class HealthBar: Displays the player's health
class HealthBar(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, initial_health):
        super().__init__()
        self.resources = ResourceManager()  # Possible coupling point: ResourceManager is expected to be well-defined.
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.max_health = initial_health
        self.current_health = initial_health
        self._load_health_image()
        self.rect = self.image.get_rect(topleft=(x, y))

    def _load_health_image(self):
        try:
            base_image = self.resources.load_image(f"life/{self.current_health}vidas.png")
            self.image = pygame.transform.scale(base_image, (self.width, self.height))
        except Exception as e:
            print(f"Error loading health image: {e}")
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((255, 0, 0))

    def update(self, current_health=None, *args):
        if current_health is not None and current_health != self.current_health:
            self.current_health = current_health
            self._load_health_image()
        self.rect.topleft = (self.x, self.y)

    def render(self, surface):
        surface.blit(self.image, self.rect)

class CoinBar(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.resources = ResourceManager()
        self.x = x
        self.y = y
        self.coins = 0
        self._load_coin_image()
        self.font = self.resources.load_font(font, 28) # Font for the text
        self.rect = self.image.get_rect(topleft=(x, y))

    def _load_coin_image(self):
        try:
            self.image = pygame.transform.scale(self.resources.load_image("Icono Moneda.png"), (48, 48))
        except Exception as e:
            print(f"Error loading coin image: {e}")
            self.image = pygame.Surface((32, 32))
            self.image.fill((255, 255, 0))

    def update(self, coins=None, *args):
        if coins is not None and coins != self.coins:
            self.coins = coins
        self.rect.topleft = (self.x, self.y)

    def render(self, surface):
        surface.blit(self.image, self.rect)
        coin_text = self.font.render(str(self.coins), True, (0, 0, 0))
        text_rect = coin_text.get_rect(topleft=(self.rect.left+13, self.y+10))
        surface.blit(coin_text, text_rect)


