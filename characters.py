"""
Character classes and sprite management for the game.

This module contains all character-related classes including the base sprite class,
character class, player class, and enemy classes. It also includes utilities for
sprite sheet handling and debugging.
"""

import time
import pygame
import os
import math
from enum import IntEnum
from collections import namedtuple
from pygame.locals import *
from resource_manager import ResourceManager
from abc import ABC, abstractmethod

# -------------------------------------------------
# Constants and Enumerations
# -------------------------------------------------

DEBUG_SPRITES = False

class Direction(IntEnum):
    """Enumeration of possible movement directions."""
    IDLE = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4

class AnimationConstants:
    """Container for animation-related constants."""
    PLAYER_DELAY = 5  # Updates between frames for movement
    ATTACK_DELAY = 50  # Milliseconds per frame for attack
    HURT_DELAY = 100  # Milliseconds per frame for hurt animation

class MovementConstants:
    """Container for movement speed constants."""
    PLAYER = 0.25
    RAT = 0.60
    ALIEN = 0.27
    MINOTAUR = 0.26
    SKELETON = 0.85
    ZOMBIE = 0.28
    REPTILIAN = 0.26
    FRANK = 0.24
    FATTY = 0.22
    NHEMBITRON = 0.3

class HealthConstants:
    """Container for health constants."""
    PLAYER = 5
    RAT = 1
    ALIEN = 2
    MINOTAUR = 5
    SKELETON = 1
    ZOMBIE = 2
    REPTILIAN = 5
    FRANK = 3
    FATTY = 4
    NHEMBITRON = 15

class DamageConstants:
    """Container for damage constants."""
    PLAYER = 1
    RAT = 1
    ALIEN = 2
    MINOTAUR = 4
    SKELETON = 2
    ZOMBIE = 2
    REPTILIAN = 4
    FRANK = 3
    FATTY = 3
    NHEMBITRON = 5

class DirectionMapping:
    """Maps logical directions to sprite sheet directions."""
    SPRITE_DIRECTION = {
        Direction.IDLE: 2,
        Direction.LEFT: 1,
        Direction.RIGHT: 3,
        Direction.UP: 0,
        Direction.DOWN: 2,
    }

# Action definitions
ActionTuple = namedtuple('ActionTuple', 'prefix numImages')
AVAILABLE_ACTIONS = [
    ActionTuple('walk', [8, 8, 8, 8]),
    ActionTuple('slash', [6, 6, 6, 6]),
    ActionTuple('hurt', [6])
]

# -------------------------------------------------
# Sprite Classes
# -------------------------------------------------

class MySprite(pygame.sprite.Sprite):
    """Base sprite class for all game objects."""
    
    def __init__(self):
        super().__init__()
        self.position = (0, 0)
        self.speed = (0, 0)
        self.scroll = (0, 0)

    def set_position(self, position):
        """Set the sprite's position in the game world."""
        self.position = position
        self._update_rect_position()

    def _update_rect_position(self):
        """Update the sprite's rect based on position and scroll values."""
        if hasattr(self, 'rect'):
            self.rect.left = self.position[0] - self.scroll[0]
            self.rect.bottom = self.position[1] - self.scroll[1]

    def set_screen_position(self, scroll):
        """Update the sprite's screen position based on scroll values."""
        self.scroll = scroll
        if hasattr(self, 'rect'):
            self.rect.midbottom = (self.position[0] - scroll[0], self.position[1] - scroll[1])

    def increment_position(self, increment):
        """Move the sprite by the specified increment."""
        new_position = (
            self.position[0] + increment[0],
            self.position[1] + increment[1]
        )
        self.set_position(new_position)

    def update(self, *args):
        """Update the sprite's position based on its speed."""
        if args and not isinstance(self, Character):
            time_value = args[-1]
            increment_x = self.speed[0] * time_value
            increment_y = self.speed[1] * time_value
            self.increment_position((increment_x, increment_y))


class SpriteSheet:
    """Handles loading and managing sprite sheets and their frame data."""
    
    def __init__(self, image, coordinates_text):
        self.image = image
        self.coordinates_text = coordinates_text


class AnimationManager:
    """Manages character animations and sprite frames."""
    
    def __init__(self, image_prefix):
        self.sprite_sheets = {}
        self.frame_rects = {}
        self.current_action = 'walk'
        
        # Initialize frame rect dictionaries
        for action in AVAILABLE_ACTIONS:
            self.frame_rects[action.prefix] = {}
            for direction in Direction:
                self.frame_rects[action.prefix][direction] = []
                
        self._load_actions(image_prefix)
    
    def _load_actions(self, image_prefix):
        """Load sprite sheets and coordinate data for all actions."""
        for action in AVAILABLE_ACTIONS:
            try:
                sprite_sheet_path = f"{image_prefix}/{action.prefix}.png"
                sprite_sheet = ResourceManager.load_image(sprite_sheet_path)
                coords_path = f"{image_prefix}/{action.prefix}.txt"
                coords_text = ResourceManager.load_coordinates(coords_path)
                self.sprite_sheets[action.prefix] = SpriteSheet(sprite_sheet, coords_text)
                self._process_coordinates(action, coords_text)
                if DEBUG_SPRITES:
                    self._visualize_sprite_sheet(
                        sprite_sheet, 
                        self.frame_rects,
                        f"Sprite Debug - {image_prefix}/{action.prefix}"
                    )
            except Exception as e:
                print(f"Error loading sprites for {image_prefix}/{action.prefix}: {e}")
    
    def _process_coordinates(self, action, coords_text):
        """Process sprite sheet coordinate data into usable rectangles."""
        data = coords_text.split()
        for direction in range(len(action.numImages)):
            self.frame_rects[action.prefix][direction] = []
            for frame in range(action.numImages[direction]):
                index = sum(action.numImages[prev_dir] * 4 for prev_dir in range(direction)) + frame * 4
                if index + 3 < len(data):
                    rect = pygame.Rect(
                        (int(data[index]), int(data[index+1])),
                        (int(data[index+2]), int(data[index+3])))
                    self.frame_rects[action.prefix][direction].append(rect)
        
        # Handle idle direction if it doesn't have dedicated frames
        if not self.frame_rects[action.prefix][Direction.IDLE] and self.frame_rects[action.prefix][Direction.DOWN]:
            self.frame_rects[action.prefix][Direction.IDLE] = [self.frame_rects[action.prefix][Direction.DOWN][0]]
    
    def get_max_frame_dimensions(self):
        """Calculate maximum dimensions across all frames."""
        max_width = 0
        max_height = 0
        for action in AVAILABLE_ACTIONS:
            action_name = action.prefix
            for direction in Direction:
                for frame_rect in self.frame_rects[action_name][direction]:
                    max_width = max(max_width, frame_rect.width)
                    max_height = max(max_height, frame_rect.height)
        return max_width, max_height

    def _visualize_sprite_sheet(self, sprite_sheet, rectangles, title="Sprite Debug"):
        """Debug utility to visualize sprite sheet rectangles."""
        pass


class Damageable(ABC):
    """Interface for any entity that can take damage."""
    
    @abstractmethod
    def take_damage(self, damage):
        """Take the specified amount of damage."""
        pass
    
    @abstractmethod
    def get_damage(self):
        """Return the damage this entity inflicts."""
        pass


class Character(MySprite, Damageable):
    """Base class for all game characters with animations."""
    
    def __init__(self, image_prefix, speed_movement, animation_delay, health=1, damage=1):
        super().__init__()
        self.movement_vector = (0, 0)
        self.facing_direction = Direction.IDLE
        self.health = health
        self.damage = damage
        self.speed_movement = speed_movement
        self.animation_delay = animation_delay
        
        # Animation state
        self.animation_manager = AnimationManager(image_prefix)
        self.frame_indices = {direction: 0 for direction in Direction}
        self.movement_delay = 0
        
        # Combat state
        self.is_hurt = False
        self.hurt_frame_index = 0
        self.last_hurt_update = 0
        self.attack_in_progress = False
        self.attack_frame_index = 0
        self.last_attack_update = 0
        
        # Set initial dimensions based on sprite frames
        max_width, max_height = self.animation_manager.get_max_frame_dimensions()
        self.rect = pygame.Rect(0, 0, max_width, max_height)
        
        # Load sounds
        self.death_sound = ResourceManager.load_sound("daño.mp3")
        self.attack_sound = ResourceManager.load_sound("ataque_enemigo.mp3")
        
        self.update_posture()

    @property
    def current_action(self):
        """Get the character's current animation action.
        This property exists for backward compatibility with code that expects current_action
        to be a direct attribute of Character rather than inside animation_manager.
        """
        return self.animation_manager.current_action
    
    @current_action.setter
    def current_action(self, value):
        """Set the character's current animation action."""
        self.animation_manager.current_action = value

    def get_damage(self):
        """Return the damage this character inflicts."""
        return self.damage

    def take_damage(self, damage):
        """Take damage and trigger hurt animation."""
        if not self.is_hurt:
            self.health -= damage
            self.is_hurt = True
            self.animation_manager.current_action = 'hurt'
            self.hurt_frame_index = 0
            self.last_hurt_update = pygame.time.get_ticks()
            self.attack_in_progress = False

    def move(self, movement):
        """Update movement vector and facing direction."""
        if isinstance(movement, tuple):
            self._handle_vector_movement(movement)
        else:
            self._handle_direction_movement(movement)

    def _handle_vector_movement(self, movement_vector):
        """Handle movement specified as a vector."""
        self.movement_vector = movement_vector
        if movement_vector != (0, 0):
            dx, dy = movement_vector
            # Determine facing direction based on movement vector
            if abs(dx) >= abs(dy):
                self.facing_direction = Direction.RIGHT if dx > 0 else Direction.LEFT
            else:
                self.facing_direction = Direction.DOWN if dy > 0 else Direction.UP

    def _handle_direction_movement(self, direction):
        """Handle movement specified as a Direction enum."""
        if direction != Direction.IDLE:
            self.facing_direction = direction
            
        mapping = {
            Direction.UP: (0, -1),
            Direction.DOWN: (0, 1),
            Direction.LEFT: (-1, 0),
            Direction.RIGHT: (1, 0),
            Direction.IDLE: (0, 0)
        }
        self.movement_vector = mapping.get(direction, (0, 0))

    def attack(self):
        """Initiate attack animation if not already attacking or hurt."""
        if not self.attack_in_progress and not self.is_hurt:
            self.attack_in_progress = True
            self.animation_manager.current_action = 'slash'
            self.attack_sound.play()
            self.attack_frame_index = 0
            self.last_attack_update = pygame.time.get_ticks()

    def update_posture(self):
        """Update character's visual appearance based on state."""
        if self.is_hurt:
            self._update_hurt_animation()
        elif self.attack_in_progress:
            self._update_attack_animation()
        else:
            self._update_movement_animation()

    def _update_hurt_animation(self):
        """Update hurt animation frames."""
        now = pygame.time.get_ticks()
        if now - self.last_hurt_update > AnimationConstants.HURT_DELAY:
            self.last_hurt_update = now
            self.hurt_frame_index += 1
            if self.hurt_frame_index >= len(self.animation_manager.frame_rects['hurt'][0]):
                self._finish_hurt_animation()
                return
            self._update_sprite_image(0, self.hurt_frame_index, 'hurt')

    def _finish_hurt_animation(self):
        """Handle end of hurt animation."""
        self.is_hurt = False
        if self.health <= 0:
            self.death_sound.play(fade_ms=1000)
            self.kill()
        else:
            self.animation_manager.current_action = 'walk'
            self.hurt_frame_index = 0

    def _update_attack_animation(self):
        """Update attack animation frames."""
        now = pygame.time.get_ticks()
        if now - self.last_attack_update > AnimationConstants.ATTACK_DELAY:
            self.last_attack_update = now
            self.attack_frame_index += 1
            sprite_direction = DirectionMapping.SPRITE_DIRECTION.get(self.facing_direction, 2)
            
            if self.animation_manager.frame_rects['slash'].get(sprite_direction):
                max_frames = len(self.animation_manager.frame_rects['slash'][sprite_direction])
                if self.attack_frame_index >= max_frames:
                    self.attack_in_progress = False
                    self.animation_manager.current_action = 'walk'
                    self.attack_frame_index = 0
                else:
                    self._update_sprite_image(sprite_direction, self.attack_frame_index, 'slash')
            else:
                self.attack_in_progress = False
                self.animation_manager.current_action = 'walk'

    def _update_movement_animation(self):
        """Update walking/idle animation frames."""
        action = self.animation_manager.current_action
        
        if self.movement_vector == (0, 0):
            # Idle state
            sprite_direction = DirectionMapping.SPRITE_DIRECTION.get(self.facing_direction, 2)
            self.frame_indices[self.facing_direction] = 0
            self._update_sprite_image(sprite_direction, 0, action)
        else:
            # Moving state
            self._animate_movement(action)

    def _animate_movement(self, action):
        """Handle movement animation cycling."""
        self.movement_delay += 1
        if self.movement_delay >= self.animation_delay:
            self.movement_delay = 0
            if self.facing_direction != Direction.IDLE:
                sprite_direction = DirectionMapping.SPRITE_DIRECTION.get(self.facing_direction, 2)
                self.frame_indices[self.facing_direction] += 1
                frames = self.animation_manager.frame_rects[action][sprite_direction]
                if self.frame_indices[self.facing_direction] >= len(frames):
                    self.frame_indices[self.facing_direction] = 0
                    
        sprite_direction = DirectionMapping.SPRITE_DIRECTION.get(self.facing_direction, 2)
        frame_index = self.frame_indices[self.facing_direction]
        self._update_sprite_image(sprite_direction, frame_index, action)

    def _update_sprite_image(self, sprite_direction, frame_index, action):
        """Update the character's visual sprite based on animation frame."""
        frames = self.animation_manager.frame_rects[action]
        if sprite_direction < len(frames) and frames[sprite_direction]:
            max_frames = len(frames[sprite_direction])
            frame_index = frame_index % max_frames
            try:
                sprite_rect = frames[sprite_direction][frame_index]
                sprite_sheet = self.animation_manager.sprite_sheets[self.animation_manager.current_action].image
                
                if self._is_sprite_rect_valid(sprite_rect, sprite_sheet):
                    self._render_sprite_frame(sprite_sheet, sprite_rect)
                    
            except ValueError as e:
                self._handle_sprite_error(f"Error updating sprite: {e}", sprite_direction, action)

    def _is_sprite_rect_valid(self, sprite_rect, sprite_sheet):
        """Check if sprite rect is within the bounds of the sprite sheet."""
        return (sprite_rect.right <= sprite_sheet.get_width() and 
                sprite_rect.bottom <= sprite_sheet.get_height())

    def _render_sprite_frame(self, sprite_sheet, sprite_rect):
        """Render the current sprite frame onto the sprite's image surface."""
        old_midbottom = self.rect.midbottom  # Save position
        
        # Create transparent surface of max size
        self.image = pygame.Surface(self.rect.size, pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))
        
        # Get current frame and center at bottom
        original_image = sprite_sheet.subsurface(sprite_rect)
        img_rect = original_image.get_rect(
            midbottom=(self.rect.width//2, self.rect.height)
        )
        
        self.image.blit(original_image, img_rect)
        self.rect.midbottom = old_midbottom  # Restore position
        self.set_screen_position(self.scroll)

    def _handle_sprite_error(self, error_message, sprite_direction, action):
        """Handle errors when updating sprites."""
        print(error_message)
        self.frame_indices[self.facing_direction] = 0
        frames = self.animation_manager.frame_rects[action][sprite_direction]
        if frames:
            first_rect = frames[0]
            self.image = self.animation_manager.sprite_sheets[self.animation_manager.current_action].image.subsurface(first_rect)

    def _normalize_movement_vector(self):
        """Normalize the movement vector for consistent speed in all directions."""
        dx, dy = self.movement_vector
        if dx != 0 and dy != 0:
            factor = 1 / (2 ** 0.5)  # Normalize diagonal movement
            return dx * factor, dy * factor
        return dx, dy

    def _handle_collision(self, axis, speed, collision_list, time):
        """Handle collision response for a specific axis."""
        if not collision_list:
            return
            
        if axis == 'x':
            if speed > 0:
                self.rect.right = min(c.rect.left for c in collision_list)
            else:
                self.rect.left = max(c.rect.right for c in collision_list)
        else:  # axis == 'y'
            if speed > 0:
                self.rect.bottom = min(c.rect.top for c in collision_list)
            else:
                self.rect.top = max(c.rect.bottom for c in collision_list)

    def update(self, collisionTiles, time):
        """Update character position, handle collisions, and animate."""
        if self.attack_in_progress:
            self.update_posture()
            return
            
        # Normalize movement vector for consistent speed
        dx, dy = self._normalize_movement_vector()
        
        # Calculate speed components
        speed_x = dx * self.speed_movement
        speed_y = dy * self.speed_movement
        
        # Move in X direction and handle collisions
        self.rect.x += speed_x * time
        collision_list = pygame.sprite.spritecollide(self, collisionTiles, False)
        self._handle_collision('x', speed_x, collision_list, time)
        
        # Move in Y direction and handle collisions
        self.rect.y += speed_y * time
        collision_list = pygame.sprite.spritecollide(self, collisionTiles, False)
        self._handle_collision('y', speed_y, collision_list, time)
        
        # Update stored position
        self.position = (self.rect.centerx, self.rect.bottom)
        
        # Update animation
        self.update_posture()


class Player(Character):
    """Player character class."""
    
    def __init__(self):
        super().__init__('thiagic', MovementConstants.PLAYER, AnimationConstants.PLAYER_DELAY, health=HealthConstants.PLAYER, damage=DamageConstants.PLAYER)
        self.attack_key_pressed_last_frame = False
        self.attack_sound = ResourceManager.load_sound("slash.mp3")
        self.max_health = self.health
        self.coins = 0
        self.invincible = False
        self.invincible_start_time = 0
        self.invincible_duration = 2000  # 2 seconds
        self.invincible_used = False
        self.shield_image = ResourceManager.load_image("shield.png")
        self.shield_image.set_alpha(128)  # Set transparency

    def move(self, keys_pressed, up_key, down_key, left_key, right_key, attack_key):
        """Handle player movement and attacks based on key input."""
        self._handle_attack_input(keys_pressed, attack_key)
        movement_vector = self._get_movement_vector(keys_pressed, up_key, down_key, left_key, right_key)
        super().move(movement_vector)

    def _handle_attack_input(self, keys_pressed, attack_key):
        """Handle attack key input with press detection."""
        current_attack_pressed = keys_pressed[attack_key]
        if current_attack_pressed and not self.attack_key_pressed_last_frame:
            self.attack()
        self.attack_key_pressed_last_frame = current_attack_pressed
        
    def _get_movement_vector(self, keys_pressed, up_key, down_key, left_key, right_key):
        """Determine movement vector from pressed keys."""
        dx, dy = 0, 0
        if keys_pressed[left_key]:
            dx -= 1
        if keys_pressed[right_key]:
            dx += 1
        if keys_pressed[up_key]:
            dy -= 1
        if keys_pressed[down_key]:
            dy += 1
        return (dx, dy)

    def save_state(self):
        """Create and return a memento with the player's current state."""
        return PlayerMemento(self.health)

    def load_state(self, memento):
        """Restore player state from a memento."""
        self.health = memento.health

    def heal(self):
        """Restore one point of health up to max health."""
        self.health = min(self.max_health, self.health + 1)

    def gain_coins(self, amount):
        """Add coins to the player's inventory."""
        self.coins += amount

    def take_damage(self, damage):
        """Take damage and trigger hurt animation."""
        if not self.invincible and not self.is_hurt:
            self.health -= damage
            self.is_hurt = True
            self.animation_manager.current_action = 'hurt'
            self.hurt_frame_index = 0
            self.last_hurt_update = pygame.time.get_ticks()
            self.attack_in_progress = False

    def activate_invincibility(self):
        """Activate invincibility for the player."""
        if not self.invincible_used:
            self.invincible = True
            self.invincible_start_time = pygame.time.get_ticks()
            self.invincible_used = True

    def update_invincibility(self):
        """Update invincibility status based on duration."""
        if self.invincible:
            current_time = pygame.time.get_ticks()
            if current_time - self.invincible_start_time > self.invincible_duration:
                self.invincible = False


class PlayerMemento:
    """Memento class for storing player state."""
    
    def __init__(self, health):
        self.health = health


class Enemy(Character):
    """Base class for all enemy characters."""
    
    def __init__(self, image_prefix, speed_movement, animation_delay, health=1, damage=1):
        super().__init__(image_prefix, speed_movement, animation_delay, health, damage)
        self.moving = False
        
    def move_cpu(self, player):
        """AI movement toward the player."""
        dx = player.position[0] - self.position[0]
        dy = player.position[1] - self.position[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5
        
        if distance < 10:
            self.move((0, 0))  # Stop if too close
            return
            
        # Normalize movement vector
        mvx = dx / distance
        mvy = dy / distance
        self.move((mvx, mvy))


# Enemy types - each with specific stats
class Rat(Enemy):
    """Rat enemy class."""
    def __init__(self):
        super().__init__('enemies/enemy_rat', MovementConstants.RAT, AnimationConstants.PLAYER_DELAY, HealthConstants.RAT, DamageConstants.RAT)

class Alien(Enemy):
    """Alien enemy class."""
    def __init__(self):
        super().__init__('enemies/enemy_alien', MovementConstants.ALIEN, AnimationConstants.PLAYER_DELAY, HealthConstants.ALIEN, DamageConstants.ALIEN)
        
class Minotaur(Enemy):
    """Minotaur enemy class."""
    def __init__(self):
        super().__init__('enemies/enemy_minotaur', MovementConstants.MINOTAUR, AnimationConstants.PLAYER_DELAY, HealthConstants.MINOTAUR, DamageConstants.MINOTAUR)
        self.death_sound = ResourceManager.load_sound("minotaur.mp3")

class Skeleton(Enemy):
    """Skeleton enemy class."""
    def __init__(self):
        super().__init__('enemies/enemy_skeleton', MovementConstants.SKELETON, AnimationConstants.PLAYER_DELAY, HealthConstants.SKELETON, DamageConstants.SKELETON)

class Zombie(Enemy):
    """Zombie enemy class."""
    def __init__(self):
        super().__init__('enemies/enemy_zombi', MovementConstants.ZOMBIE, AnimationConstants.PLAYER_DELAY, HealthConstants.ZOMBIE, DamageConstants.ZOMBIE)

class Reptilian(Enemy):
    """Reptilian enemy class."""
    def __init__(self):
        super().__init__('enemies/enemy_reptiliano', MovementConstants.REPTILIAN, AnimationConstants.PLAYER_DELAY, HealthConstants.REPTILIAN, DamageConstants.REPTILIAN)

class Frank(Enemy):
    """Frank enemy class."""
    def __init__(self):
        super().__init__('enemies/enemy_frank_head', MovementConstants.FRANK, AnimationConstants.PLAYER_DELAY, HealthConstants.FRANK, DamageConstants.FRANK)

class Fatty(Enemy):
    """Fatty enemy class."""
    def __init__(self):
        super().__init__('enemies/enemy_gordibola', MovementConstants.FATTY, AnimationConstants.PLAYER_DELAY, HealthConstants.FATTY, DamageConstants.FATTY)

class Nhembitron(Enemy):
    """Nhembitron enemy class."""
    def __init__(self):
        super().__init__('enemies/enemy_nhembitron', MovementConstants.NHEMBITRON, AnimationConstants.PLAYER_DELAY, HealthConstants.NHEMBITRON, DamageConstants.NHEMBITRON)


# -------------------------------------------------
# Gun and Bullet Classes
# -------------------------------------------------

class Bullet(MySprite):
    """Bullet class for projectiles fired from guns."""
    
    def __init__(self, position, target_position, speed=5, damage=1):
        super().__init__()
        self.position = position
        self.original_position = position
        self.target_position = target_position
        self.damage = damage
        self.max_distance = 500  # Maximum travel distance
        
        # Load bullet sprite
        self.original_image = ResourceManager.load_image("bullet.png")
        
        # Initialize bullet direction and appearance
        self._setup_bullet_trajectory(position, target_position, speed)
        
    def _setup_bullet_trajectory(self, position, target_position, speed):
        """Calculate bullet trajectory and orientation."""
        dx = target_position[0] - position[0]
        dy = target_position[1] - position[1]
        distance = (dx**2 + dy**2)**0.5
        
        if distance > 0:
            self.speed = (dx/distance * speed, dy/distance * speed)
            # Calculate angle and rotate image
            angle = math.degrees(math.atan2(-dy, dx))
            self.image = pygame.transform.rotate(self.original_image, angle)
        else:
            self.speed = (0, 0)
            self.image = self.original_image
        
        # Set up initial position
        self.rect = self.image.get_rect(center=position)
        
    def update(self, collisionTiles=None, time=None):
        """Update bullet position and check for collisions or max distance."""
        # Handle different parameter patterns
        if collisionTiles is not None and not isinstance(collisionTiles, pygame.sprite.Group):
            time = collisionTiles
            collisionTiles = None
            
        # Default time value if none provided
        if time is None:
            time = 1
        
        # Let parent class update position
        super().update(time)
        
        # Update rect position
        self.rect.center = self.position
        
        # Check if bullet has traveled maximum distance
        if self._has_traveled_max_distance():
            self.kill()
            return
            
        # Check collision with tiles if provided
        if collisionTiles and self._check_collision(collisionTiles):
            self.kill()
            
    def _has_traveled_max_distance(self):
        """Check if bullet has exceeded its maximum travel distance."""
        current_distance = ((self.position[0] - self.original_position[0])**2 + 
                           (self.position[1] - self.original_position[1])**2)**0.5
        return current_distance > self.max_distance
        
    def _check_collision(self, collisionTiles):
        """Check if bullet collides with any tiles."""
        return pygame.sprite.spritecollide(self, collisionTiles, False)


class Gun(MySprite):
    """Gun class that fires bullets at the player."""
    
    def __init__(self, position=(0, 0), fire_rate=2000, bullet_speed=3, damage=1):
        super().__init__()
        self.position = position
        self.fire_rate = fire_rate  # Time between shots in milliseconds
        self.bullet_speed = bullet_speed
        self.damage = damage
        self.last_shot_time = 0
        self.target_position = position  # Initial target position
        
        self._load_sprites()
        self._setup_animation()
        self._load_sounds()
        
    def _load_sprites(self):
        """Load gun sprites from spritesheet."""
        self.original_image = pygame.transform.flip(ResourceManager.load_image("AK47.png"), True, False)
        self.frame_count = 20  # 1 column, 20 rows
        self.frame_height = self.original_image.get_height() // self.frame_count
        self.frame_width = self.original_image.get_width()
        
        # Extract frames from spritesheet
        self.frames = []
        for i in range(self.frame_count):
            frame_rect = pygame.Rect(0, i * self.frame_height, self.frame_width, self.frame_height)
            frame_image = self.original_image.subsurface(frame_rect)
            self.frames.append(frame_image)
            
    def _setup_animation(self):
        """Set up animation-related variables."""
        self.current_frame = 0
        self.animation_delay = 100  # Time per frame in ms
        self.last_frame_update = pygame.time.get_ticks()
        self.image = self.frames[self.current_frame]
        self.rect = self.image.get_rect(center=self.position)
        self.bullets = pygame.sprite.Group()
        
    def _load_sounds(self):
        """Load gun-related sound effects."""
        self.fire_sound = ResourceManager.load_sound("fire_sound.mp3")

    def update(self, collisionTiles=None, player=None, time=None):
        """Update gun state, animations, and bullets."""
        # Handle default time parameter
        if time is None:
            time = 1
            
        super().update(time)
        
        # Update bullets
        for bullet in self.bullets:
            bullet.update(collisionTiles, time)
        
        # Fire at player if in range
        self._handle_firing(player)
        
        # Update animation
        self._update_animation()
        
        # Update gun orientation
        self._update_orientation()
    
    def _handle_firing(self, player):
        """Handle firing logic when player is in range."""
        if player:
            current_time = pygame.time.get_ticks()
            self.target_position = player.position
            if current_time - self.last_shot_time > self.fire_rate:
                self.fire_at(player.position)
                self.last_shot_time = current_time
                
    def _update_animation(self):
        """Update gun animation frames."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_frame_update > self.animation_delay:
            self.current_frame = (self.current_frame + 1) % self.frame_count
            self.last_frame_update = current_time
            
    def _update_orientation(self):
        """Update gun orientation to face the target."""
        dx = self.target_position[0] - self.position[0]
        dy = self.target_position[1] - self.position[1]
        distance = (dx**2 + dy**2)**0.5
        
        if distance > 0:
            angle = math.degrees(math.atan2(-dy, dx))
            
            # Flip if facing opposite direction
            if angle > 90 or angle < -90:
                current_frame_image = pygame.transform.flip(self.frames[self.current_frame], False, True)
            else:
                current_frame_image = self.frames[self.current_frame]
            
            # Rotate image
            self.image = pygame.transform.rotate(current_frame_image, angle)
        else:
            self.image = self.frames[self.current_frame]
        
        # Update rect position
        self.rect = self.image.get_rect(center=self.position)
    
    def fire_at(self, target_position):
        """Fire a bullet toward the target position."""
        bullet = Bullet(self.position, target_position, self.bullet_speed, self.damage)
        self.bullets.add(bullet)
        self.fire_sound.play()
        return bullet


class GunTurret(MySprite, Damageable):
    """A stationary turret that fires bullets at the player."""
    
    def __init__(self, position=(0, 0), fire_rate=2000, bullet_speed=3, damage=1, health=3):
        super().__init__()
        self.position = position
        self.health = health
        self.max_health = health
        self.is_hurt = False
        self.hurt_timer = 0
        self.hurt_effect_duration = 200  # milliseconds
        self.hurt_flash_interval = 50  # Flash interval in milliseconds
        self.scroll = (0, 0)
        
        # Create gun component
        self.gun = Gun(position, fire_rate, bullet_speed, damage)
        
        # Set initial image and rect
        self.image = self.gun.image
        self.original_image = self.gun.image.copy()
        self.rect = self.image.get_rect(center=position)
        
    def set_position(self, position):
        """Set position of turret and its gun."""
        super().set_position(position)
        self.gun.position = self.position
        
    def get_damage(self):
        """Return damage inflicted by the turret's gun."""
        return self.gun.damage
        
    def take_damage(self, damage):
        """Take damage and handle turret destruction."""
        self.health -= damage
        self.is_hurt = True
        self.hurt_timer = pygame.time.get_ticks()
        
        if self.health <= 0:
            self.kill()
    
    def _update_hurt_effect(self):
        """Update visual hurt effect if turret is damaged."""
        if not self.is_hurt:
            return
            
        current_time = pygame.time.get_ticks()
        if current_time - self.hurt_timer > self.hurt_effect_duration:
            self.is_hurt = False
            return

        # Implement flashing effect based on time intervals
        if (current_time - self.hurt_timer) // self.hurt_flash_interval % 2 == 0:
            # Apply red tint to show damage
            self._apply_damage_tint()
        else:
            # Reset to normal appearance during flash off period
            self._reset_appearance()
    
    def _apply_damage_tint(self):
        """Apply a red tint to the turret to show damage."""
        # Create a copy of the current image 
        tinted_image = self.gun.image.copy()
        
        # Create a red overlay surface
        overlay = pygame.Surface(tinted_image.get_size(), pygame.SRCALPHA)
        overlay.fill((255, 0, 0, 100))  # Red with 100 alpha (partial transparency)
        
        # Apply the overlay
        tinted_image.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
        
        # Update the image while preserving rect position
        old_center = self.rect.center
        self.image = tinted_image
        self.rect = self.image.get_rect(center=old_center)
    
    def _reset_appearance(self):
        """Reset turret appearance to normal."""
        # Simply use the gun's current image
        old_center = self.rect.center
        self.image = self.gun.image
        self.rect = self.image.get_rect(center=old_center)
    
    def update(self, collisionTiles, time=None, player=None):
        """Update turret state and its gun component."""
        # Update gun component if player is in range
        if player:
            self.gun.update(collisionTiles, player, time)
            
            # Update turret image to match gun orientation (if not hurt)
            if not self.is_hurt:
                self._reset_appearance()
        
        # Handle hurt effect last to override normal appearance when damaged
        self._update_hurt_effect()
    
    def get_bullets(self):
        """Get all bullets from the gun component."""
        return self.gun.bullets
            
    def render(self, surface, camera):
        """Render the turret and its bullets."""
        # Render the turret
        turret_pos = camera.apply(self)
        surface.blit(self.image, turret_pos)
        
        # Render all bullets
        for bullet in self.gun.bullets:
            bullet_pos = camera.apply(bullet)
            surface.blit(bullet.image, bullet_pos)