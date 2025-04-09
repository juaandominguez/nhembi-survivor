import pygame
from resource_manager import ResourceManager

font = "PressStart2P-Regular.ttf"

class MiniMap:
    def __init__(self, x, y, width, height, map_width, map_height):
        self.x = x  # Position on screen
        self.y = y
        self.width = width  # MiniMap size
        self.height = height
        self.map_width = map_width  # Full map size
        self.map_height = map_height
        self.surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)  # Transparent background
        self.border_thickness = 2
        self.visible = True
        self.toggle_cooldown = 0
        self.toggle_cooldown_max = 100  # 300ms cooldown between toggles

        self.resources = ResourceManager()
        self.font = self.resources.load_font(font, 20)
        
        # Create a border rectangle
        self.border_rect = pygame.Rect(self.x - self.border_thickness, self.y - self.border_thickness, 
                                      self.width + 2*self.border_thickness, 
                                      self.height + 2*self.border_thickness)
        
        # Add cache for map details to improve performance
        self.map_cache = None
        self.last_collision_rects = None
        
        # Add update timing to reduce redraw frequency
        self.last_update_time = 0
        self.update_frequency = 10  # Only update minimap every 10ms
        self.force_redraw = True
        
        # For optimizing enemy positions
        self.enemies_cache = []
        self.last_enemy_update = 0
        self.enemy_update_frequency = 10  # Update enemy positions every 10ms

    def toggle_visibility(self):
        """Toggle the visibility of the minimap if cooldown has elapsed"""
        current_time = pygame.time.get_ticks()
        if current_time - self.toggle_cooldown > self.toggle_cooldown_max:
            self.visible = not self.visible
            self.toggle_cooldown = current_time

    def draw_map_details(self, collision_rects, level_data=None, level_decorations=None):
        """
        Draw map structure details on the minimap
        
        Args:
            collision_rects: List of collision rectangle objects
            level_data: Optional level tile data for detailed rendering
            level_decorations: Optional decoration tile data
        """
        # Check if we can use cache
        if self.map_cache is not None and collision_rects == self.last_collision_rects and not self.force_redraw:
            self.surface.blit(self.map_cache, (0, 0))
            return
            
        # Create new cache surface
        map_cache = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Scale positions to minimap size
        scale_x = self.width / self.map_width
        scale_y = self.height / self.map_height
        
        # Simplify collision_rects processing for large maps
        # For maps larger than 3000 pixels, we'll sample every nth rectangle
        sample_rate = 1
        if self.map_width > 3000 or self.map_height > 3000:
            sample_rate = 3
            
        # Process collision rects at the sampling rate
        visible_rects = []
        for i, rect in enumerate(collision_rects):
            if i % sample_rate != 0:
                continue
                
            mini_width = max(1, int(rect.width * scale_x))
            mini_height = max(1, int(rect.height * scale_y))
            # Skip very small rects that won't be visible
            if mini_width > 0 and mini_height > 0:
                mini_x = int(rect.x * scale_x)
                mini_y = int(rect.y * scale_y)
                visible_rects.append((mini_x, mini_y, mini_width, mini_height))
        
        # Draw walls and collision areas
        for mini_x, mini_y, mini_width, mini_height in visible_rects:
            mini_rect = pygame.Rect(mini_x, mini_y, mini_width, mini_height)
            pygame.draw.rect(map_cache, (180, 180, 180, 200), mini_rect)
            
        # Store the new cache
        self.map_cache = map_cache
        self.last_collision_rects = collision_rects
        self.force_redraw = False
        
        # Draw cached map to surface
        self.surface.blit(self.map_cache, (0, 0))

    def draw(self, screen, player_pos, enemies, items=None, screen_size=(800, 600), level_details=None):
        """
        Draw the minimap with player, enemies, and optional collectible items
        
        Args:
            screen: The pygame surface to draw on
            player_pos: (x, y) position of the player
            enemies: List of (x, y) positions of enemies
            items: Optional list of (x, y) positions of collectible items
            screen_size: Size of the game screen (for FOV calculation)
            level_details: Dictionary with collision_rects, level_data and level_decorations
        """
        if not self.visible:
            return
            
        # Check update frequency to avoid redrawing every frame
        current_time = pygame.time.get_ticks()
        should_update_minimap = current_time - self.last_update_time > self.update_frequency
        
        if not should_update_minimap:
            # Just blit the existing surface if no update needed
            screen.blit(self.surface, (self.x, self.y))
            # Draw border around the minimap (border always shows)
            pygame.draw.rect(screen, (255, 255, 255), self.border_rect, self.border_thickness)
            return
            
        # Update timestamp
        self.last_update_time = current_time
        
        # Clear minimap with semi-transparent black background
        self.surface.fill((0, 0, 0, 180))  # Increased opacity for better visibility
        
        # Draw level details if provided
        if level_details:
            collision_rects = level_details.get('collision_rects', [])
            self.draw_map_details(collision_rects)
        
        # Draw border around the minimap
        pygame.draw.rect(screen, (255, 255, 255), self.border_rect, self.border_thickness)

        # Scale positions to minimap size
        scale_x = self.width / self.map_width
        scale_y = self.height / self.map_height
        
        # Draw player's field of view (FOV)
        # Calculate FOV rectangle based on screen size and player position
        fov_width = screen_size[0] 
        fov_height = screen_size[1]
        
        # Scale FOV to minimap coordinates
        fov_mini_width = int(fov_width * scale_x)
        fov_mini_height = int(fov_height * scale_y)
        
        # Center FOV on player's position
        fov_mini_x = int(player_pos[0] * scale_x) - fov_mini_width // 2
        fov_mini_y = int(player_pos[1] * scale_y) - fov_mini_height // 2
        
        # Draw FOV rectangle (white semi-transparent)
        fov_rect = pygame.Rect(fov_mini_x, fov_mini_y, fov_mini_width, fov_mini_height)
        pygame.draw.rect(self.surface, (255, 255, 255, 40), fov_rect)
        pygame.draw.rect(self.surface, (255, 255, 255, 100), fov_rect, 1)  # Border

        # Draw player (Green Dot)
        player_mini_x = int(player_pos[0] * scale_x)
        player_mini_y = int(player_pos[1] * scale_y)
        
        # Draw player as green dot
        pygame.draw.circle(self.surface, (0, 255, 0), (player_mini_x, player_mini_y), 4)
        pygame.draw.circle(self.surface, (255, 255, 255), (player_mini_x, player_mini_y), 4, 1)  # White outline

        # Update enemy cache less frequently
        if current_time - self.last_enemy_update > self.enemy_update_frequency:
            self.enemies_cache = []
            # For large maps with many enemies, reduce the number processed
            enemy_limit = len(enemies)
            if self.map_width > 3000 and enemy_limit > 20:
                enemy_limit = min(20, enemy_limit)
                
            for i, enemy in enumerate(enemies):
                if i >= enemy_limit:
                    break
                enemy_mini_x = int(enemy[0] * scale_x)
                enemy_mini_y = int(enemy[1] * scale_y)
                self.enemies_cache.append((enemy_mini_x, enemy_mini_y))
            self.last_enemy_update = current_time
            
        # Draw enemies (Red Dots) from cache
        for enemy_mini_x, enemy_mini_y in self.enemies_cache:
            pygame.draw.circle(self.surface, (255, 0, 0), (enemy_mini_x, enemy_mini_y), 3)
        
        # Draw collectible items (Yellow Dots) if provided - simplify for large maps
        if items:
            item_limit = len(items)
            if self.map_width > 3000 and item_limit > 10:
                item_limit = 10
                
            for i, item in enumerate(items):
                if i >= item_limit:
                    break
                item_mini_x = int(item[0] * scale_x)
                item_mini_y = int(item[1] * scale_y)
                pygame.draw.circle(self.surface, (255, 255, 0), (item_mini_x, item_mini_y), 2)

        # Add a simplified radar pulse effect that uses less CPU - only on smaller maps
        if self.map_width <= 3000:
            pulse_time = pygame.time.get_ticks() % 2000
            if pulse_time < 1000:  # Only active half the time
                pulse_size = pulse_time / 1000 * 15  # 0-15 px pulse
                pygame.draw.circle(self.surface, (0, 255, 0, 50), (player_mini_x, player_mini_y), pulse_size, 1)

        # Blit minimap to the screen
        screen.blit(self.surface, (self.x, self.y))
        
        # Only draw label on frame updates (not every frame)
        font = pygame.font.Font(None, 20)
        text = font.render("MINIMAP", True, (255, 255, 255))
        text_rect = text.get_rect(midtop=(self.x + self.width // 2, self.y - 20))
        screen.blit(text, text_rect)

