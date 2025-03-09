"""
Character classes and sprite management for the game.

This module contains all character-related classes including the base sprite class,
character class, player class, and enemy classes. It also includes utilities for
sprite sheet handling and debugging.
"""

import pygame
import os
from enum import IntEnum
from collections import namedtuple
from pygame.locals import *
from resource_manager import ResourceManager

# -------------------------------------------------
# Constants and Enumerations
# -------------------------------------------------

# Debug mode - set to False in production
DEBUG_SPRITES = False

# Define action tuples with animation frame counts for each direction
ActionTuple = namedtuple('ActionTuple', 'prefix numImages')
AVAILABLE_ACTIONS = [
    ActionTuple('walk', [8, 8, 8, 8]),
    ActionTuple('slash', [6, 6, 6, 6]),
    ActionTuple('hurt', [6])
]

# Direction enumeration
class Direction(IntEnum):
    """Enumeration of possible movement directions."""
    IDLE = 0
    LEFT = 1
    RIGHT = 2
    UP = 3
    DOWN = 4

# Direction to sprite mapping
# This maps movement directions to the correct sprite direction in the sprite sheet
DIRECTION_TO_SPRITE = {
    Direction.IDLE: 0,  # Idle uses the first row
    Direction.LEFT: 1,  # Left uses the second row
    Direction.RIGHT: 3, # Right uses the fourth row
    Direction.UP: 0,    # Up uses the fifth row
    Direction.DOWN: 2,  # Down uses the third row
}

# Character movement speeds
SPEED_MULTIPLIER = 0.5
ANIMATION_PLAYER_DELAY = 5  # Updates between frames

# -------------------------------------------------
# Sprite Classes
# -------------------------------------------------

class MySprite(pygame.sprite.Sprite):
    """Base sprite class for all game objects."""
    
    def __init__(self):
        """Initialize the sprite with default position and speed."""
        super().__init__()
        self.position = (0, 0)
        self.speed = (0, 0)
        self.scroll = (0, 0)

    def set_position(self, position):
        """Set the sprite's absolute position in the world."""
        self.position = position
        self.rect.left = self.position[0] - self.scroll[0]
        self.rect.bottom = self.position[1] - self.scroll[1]

    def set_screen_position(self, scroll):
        """Update the sprite's screen position based on world position and scroll."""
        self.scroll = scroll
        if hasattr(self, 'rect'):
            self.rect.midbottom = (self.position[0] - scroll[0], self.position[1] - scroll[1])

    def increment_position(self, increment):
        """Move the sprite by the given increment."""
        new_position = (
            self.position[0] + increment[0],
            self.position[1] + increment[1]
        )
        self.set_position(new_position)

    def update(self, time):
        """Update the sprite's position based on its speed and elapsed time."""
        increment_x = self.speed[0] * time
        increment_y = self.speed[1] * time
        self.increment_position((increment_x, increment_y))


class SpriteSheet:
    """Handles loading and managing sprite sheets and their frame data."""
    
    def __init__(self, image, coordinates_text):
        """
        Initialize a sprite sheet.
        
        Args:
            image (Surface): The sprite sheet image
            coordinates_text (str): Text containing frame coordinates
        """
        self.image = image
        self.coordinates_text = coordinates_text
        

class Character(MySprite):
    """Base class for all game characters with animations."""
    
    def __init__(self, image_prefix, speed_movement, animation_delay):
        """
        Initialize a character with animations.
        
        Args:
            image_prefix (str): Path prefix for sprite sheets
            speed_movement (float): Movement speed multiplier
            animation_delay (int): Delay between animation frames
        """
        super().__init__()
        
        # Map of action name to sprite sheet
        self.sprite_sheets = {}
        
        # Initialize coordinates file with empty lists for each direction
        self.frame_rects = [[] for _ in range(5)]  # One list per direction
        
        # Current action - default to 'walk'
        self.current_action = 'walk'
        
        # Frame indices for each direction
        self.frame_indices = {direction: 0 for direction in Direction}
        
        # Load all available actions
        self._load_actions(image_prefix)
        
        # Set initial movement state
        self.movement = Direction.IDLE
        self.moving = False
        
        # Animation timing
        self.movement_delay = 0
        self.speed_movement = speed_movement
        self.animation_delay = animation_delay
        
        # Initialize the sprite's appearance
        self.update_posture()
    
    def _load_actions(self, image_prefix):
        """
        Load all action sprites and coordinates.
        
        Args:
            image_prefix (str): Path prefix for sprite sheets
        """
        for action in AVAILABLE_ACTIONS:
            try:
                # Load the sprite sheet image
                sprite_sheet_path = f"{image_prefix}/{action.prefix}.png"
                sprite_sheet = ResourceManager.loadImage(sprite_sheet_path)
                
                # Load the coordinates file
                coords_path = f"{image_prefix}/{action.prefix}.txt"
                coords_text = ResourceManager.loadCoordinates(coords_path)
                
                # Store in the sprite sheets dictionary
                self.sprite_sheets[action.prefix] = SpriteSheet(sprite_sheet, coords_text)
                
                # Process coordinates for the walk action
                if action.prefix == 'walk':
                    self._process_walk_coordinates(action, coords_text)
                    
                    # Debug visualization
                    if DEBUG_SPRITES:
                        visualize_sprite_sheet(
                            sprite_sheet, 
                            self.frame_rects,
                            f"Sprite Debug - {image_prefix}/{action.prefix}"
                        )
                    
            except Exception as e:
                print(f"Error loading sprites for {image_prefix}/{action.prefix}: {e}")
    
    def _process_walk_coordinates(self, action, coords_text):
        """
        Process the walk action coordinates.
        
        Args:
            action (ActionTuple): The action data
            coords_text (str): The coordinates text data
        """
        data = coords_text.split()
        
        # Process coordinates for each direction
        for direction in range(len(action.numImages)):
            # Clear any existing frames for this direction
            self.frame_rects[direction] = []
            
            # Load each frame's coordinates for this direction
            for frame in range(action.numImages[direction]):
                # Calculate the index in the data array
                # Each frame has 4 values (x, y, width, height)
                index = 0
                for prev_dir in range(direction):
                    index += action.numImages[prev_dir] * 4
                index += frame * 4
                
                if index + 3 < len(data):
                    # Create rectangle for this frame
                    rect = pygame.Rect(
                        (int(data[index]), int(data[index+1])),
                        (int(data[index+2]), int(data[index+3]))
                    )
                    self.frame_rects[direction].append(rect)
        
        # Ensure all directions have at least one frame
        if not self.frame_rects[Direction.IDLE] and self.frame_rects[Direction.DOWN]:
            self.frame_rects[Direction.IDLE] = [self.frame_rects[Direction.DOWN][0]]
        
        # Initialize rect if we have valid frames
        if self.frame_rects[Direction.IDLE]:
            first_frame = self.frame_rects[Direction.IDLE][0]
            self.rect = pygame.Rect(0, 0, first_frame.width, first_frame.height)
        else:
            # Fallback to a default rect
            self.rect = pygame.Rect(0, 0, 32, 32)

    def move(self, movement):
        """
        Set the character's movement direction.
        
        Args:
            movement (Direction): The direction to move
        """
        self.movement = movement

    def update_posture(self, action='walk'):
        """
        Update the character's animation frame.
        
        Args:
            action (str): The action animation to use
        """
        # Set current action
        self.current_action = action
        
        # Update animation timing
        self.movement_delay += 1
        
        # Check if it's time to update the animation frame
        if self.movement_delay >= self.animation_delay:
            self.movement_delay = 0
            
            # Only update the frame if we're not idle
            if self.movement != Direction.IDLE:
                # Get the correct sprite direction
                sprite_direction = DIRECTION_TO_SPRITE.get(self.movement, 0)
                
                # Update the frame index for this direction
                self.frame_indices[self.movement] += 1
                
                # Check if we need to wrap around
                if (sprite_direction < len(self.frame_rects) and 
                    self.frame_rects[sprite_direction]):
                    max_frames = len(self.frame_rects[sprite_direction])
                    if self.frame_indices[self.movement] >= max_frames:
                        self.frame_indices[self.movement] = 0
        
        # Get the current frame data
        sprite_direction = DIRECTION_TO_SPRITE.get(self.movement, 0)
        frame_index = self.frame_indices[self.movement]
        
        # Update the sprite image
        self._update_sprite_image(sprite_direction, frame_index)
    
    def _update_sprite_image(self, sprite_direction, frame_index):
        """
        Update the sprite's image based on direction and frame.
        
        Args:
            sprite_direction (int): The sprite sheet direction
            frame_index (int): The frame index
        """
        # Ensure we have valid indices and frames
        if (sprite_direction < len(self.frame_rects) and 
            self.frame_rects[sprite_direction]):
            
            # Make sure frame_index is within bounds
            max_frames = len(self.frame_rects[sprite_direction])
            if frame_index >= max_frames:
                frame_index = 0
                self.frame_indices[self.movement] = 0
                
            if self.current_action in self.sprite_sheets:
                try:
                    # Get the sprite rectangle
                    sprite_rect = self.frame_rects[sprite_direction][frame_index]
                    
                    # Get the sprite sheet
                    sprite_sheet = self.sprite_sheets[self.current_action].image
                    
                    # Make sure the sprite rect is within the image bounds
                    if (sprite_rect.right <= sprite_sheet.get_width() and 
                        sprite_rect.bottom <= sprite_sheet.get_height()):
                        
                        # Store the current rect position
                        old_rect = self.rect.copy() if hasattr(self, 'rect') else None
                        
                        # Get the subsurface
                        self.image = sprite_sheet.subsurface(sprite_rect)
                        
                        # Update the rect to match the new image size
                        if old_rect:
                            # Create a new rect with the new image dimensions
                            self.rect = self.image.get_rect()
                            
                            # Preserve the position from the old rect
                            self.rect.midbottom = old_rect.midbottom
                        else:
                            # If there was no previous rect, create a new one
                            self.rect = self.image.get_rect()
                            
                        # Update screen position based on world position and scroll
                        self.set_screen_position(self.scroll)
                    else:
                        self._handle_sprite_error(
                            f"Sprite rect out of bounds: {sprite_rect}, "
                            f"image size: {sprite_sheet.get_width()}x{sprite_sheet.get_height()}",
                            sprite_direction
                        )
                            
                except ValueError as e:
                    self._handle_sprite_error(
                        f"Error updating sprite: {e}, movement: {self.movement}, "
                        f"sprite_direction: {sprite_direction}, frame: {frame_index}",
                        sprite_direction
                    )
    
    def _handle_sprite_error(self, error_message, sprite_direction):
        """
        Handle sprite rendering errors by falling back to a safe frame.
        
        Args:
            error_message (str): The error message to log
            sprite_direction (int): The sprite direction that caused the error
        """
        print(error_message)
        
        # Reset to a safe state
        self.frame_indices[self.movement] = 0
        
        # Try to use the first frame as fallback
        if self.frame_rects[sprite_direction]:
            first_rect = self.frame_rects[sprite_direction][0]
            if self.current_action in self.sprite_sheets:
                sprite_sheet = self.sprite_sheets[self.current_action].image
                self.image = sprite_sheet.subsurface(first_rect)

    def update(self, time):
        """
        Update the character's position and animation.
        
        Args:
            time (int): Elapsed time since last update
        """
        # Calculate speed based on movement direction
        speed_x, speed_y = 0, 0

        if self.movement == Direction.UP:
            speed_y = -self.speed_movement
        elif self.movement == Direction.DOWN:
            speed_y = self.speed_movement
        elif self.movement == Direction.LEFT:
            speed_x = -self.speed_movement
        elif self.movement == Direction.RIGHT:
            speed_x = self.speed_movement

        # Update the speed
        self.speed = (speed_x, speed_y)

        # Update the posture/animation
        self.update_posture('walk')

        # Call the parent class update to handle the actual movement
        super().update(time)


class Player(Character):
    """Player character class."""
    
    def __init__(self):
        """Initialize the player character."""
        super().__init__('thiagic', SPEED_MULTIPLIER, ANIMATION_PLAYER_DELAY)

    def move(self, keys_pressed, up_key, down_key, left_key, right_key):
        """
        Move the player based on keyboard input.
        
        Args:
            keys_pressed (dict): Dictionary of pressed keys
            up_key: Key for moving up
            down_key: Key for moving down
            left_key: Key for moving left
            right_key: Key for moving right
        """
        if keys_pressed[up_key]:
            super().move(Direction.UP)
        elif keys_pressed[down_key]:
            super().move(Direction.DOWN)
        elif keys_pressed[left_key]:
            super().move(Direction.LEFT)
        elif keys_pressed[right_key]:
            super().move(Direction.RIGHT)
        else:
            super().move(Direction.IDLE)


class Enemy(Character):
    """Base class for all enemy characters."""
    
    def __init__(self, image_prefix, speed_movement, animation_delay):
        """
        Initialize an enemy character.
        
        Args:
            image_prefix (str): Path prefix for sprite sheets
            speed_movement (float): Movement speed multiplier
            animation_delay (int): Delay between animation frames
        """
        super().__init__(image_prefix, speed_movement, animation_delay)
        self.moving = False

    def move_cpu(self, player):
        """
        Base AI method for enemies.
        Should be implemented by child classes.
        
        Args:
            player (Player): The player character to target
        """
        # Default behavior is to not move
        super().move(Direction.IDLE)


class Rat(Enemy):
    """Rat enemy class with simple chase AI."""
    
    def __init__(self):
        """Initialize the rat enemy."""
        super().__init__('enemies/enemy_rat', SPEED_MULTIPLIER, ANIMATION_PLAYER_DELAY)

    def move_cpu(self, player):
        """
        Move the rat towards the player.
        
        Args:
            player (Player): The player character to chase
        """
        # Calculate direction to player
        dx = player.position[0] - self.position[0]
        dy = player.position[1] - self.position[1]
        distance = max(1, (dx ** 2 + dy ** 2) ** 0.5)
        
        # If the player is too close, don't move
        min_distance = 20
        if distance < min_distance:
            super().move(Direction.IDLE)
            return
            
        # Determine the primary movement direction
        if abs(dx) > abs(dy):
            # Horizontal movement predominant
            super().move(Direction.RIGHT if dx > 0 else Direction.LEFT)
        else:
            # Vertical movement predominant
            super().move(Direction.DOWN if dy > 0 else Direction.UP)


# -------------------------------------------------
# Debug Utilities
# -------------------------------------------------

def visualize_sprite_sheet(sprite_sheet, rectangles, title="Sprite Debug"):
    """
    Display a debug window showing the sprite sheet with rectangles overlaid.
    
    Args:
        sprite_sheet (Surface): The pygame Surface containing the sprite sheet
        rectangles (list): A list of lists, where each inner list contains the rectangles for a direction
        title (str): The window title
    """
    if not DEBUG_SPRITES:
        return
        
    # Create a copy of the sprite sheet to draw on
    debug_surface = sprite_sheet.copy()
    
    # Set up colors for different directions
    direction_colors = [
        (255, 0, 0),      # IDLE - Red
        (0, 255, 0),      # LEFT - Green
        (0, 0, 255),      # DOWN - Blue
        (255, 255, 0),    # RIGHT - Yellow
        (255, 0, 255),    # UP - Magenta
    ]
    
    # Draw rectangles on the debug surface
    font = pygame.font.SysFont('Arial', 12)
    
    for direction, rects in enumerate(rectangles):
        if direction >= len(direction_colors):
            color = (255, 255, 255)  # White for any additional directions
        else:
            color = direction_colors[direction]
            
        for i, rect in enumerate(rects):
            if rect is not None:
                # Draw rectangle outline
                pygame.draw.rect(debug_surface, color, rect, 1)
                
                # Draw index number
                text = font.render(f"{direction}:{i}", True, (255, 255, 255))
                text_rect = text.get_rect(center=(rect.centerx, rect.centery))
                
                # Create a small background for the text
                bg_rect = text_rect.inflate(4, 4)
                pygame.draw.rect(debug_surface, (0, 0, 0), bg_rect)
                
                # Draw the text
                debug_surface.blit(text, text_rect)
    
    # Create a legend
    legend_height = 20 * len(direction_colors)
    legend_surface = pygame.Surface((200, legend_height))
    legend_surface.fill((50, 50, 50))
    
    direction_names = ["IDLE", "LEFT", "DOWN", "RIGHT", "UP"]
    for i, (color, name) in enumerate(zip(direction_colors, direction_names)):
        text = font.render(f"{name} (Direction {i})", True, color)
        legend_surface.blit(text, (10, i * 20 + 5))
    
    # Create the final display surface
    display_height = debug_surface.get_height() + legend_height
    display_surface = pygame.Surface((debug_surface.get_width(), display_height))
    display_surface.fill((50, 50, 50))
    display_surface.blit(debug_surface, (0, 0))
    display_surface.blit(legend_surface, (0, debug_surface.get_height()))
    
    # Display the debug window
    pygame.display.set_caption(title)
    screen = pygame.display.set_mode((display_surface.get_width(), display_surface.get_height()))
    screen.blit(display_surface, (0, 0))
    pygame.display.flip()
    
    # Wait for user to close the window
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                waiting = False