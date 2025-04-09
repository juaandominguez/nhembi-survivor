import json
import pygame

class Level:
    def __init__(self, level_file):
        """ Loads the level from an LDtk file and uses a tileset """
        self.level_tileset = "./levels/suelos_paredes.png"
        self.level_decorations = "./levels/muebles.png"
        self.tileset_image = pygame.image.load(self.level_tileset).convert_alpha()
        self.tileset_decorations = pygame.image.load(self.level_decorations).convert_alpha()
        self.tile_size = 16  # Tile size in pixels
        
        # Add performance flags
        self.use_tile_batching = False  # Will be set to True for large maps
        self.tiles_batch_size = 500  # Number of tiles to process in one batch
        
        # Load level data
        self.level_data, self.level_decorations, self.level_collisions = self.load_level(level_file)
        
        # Pre-render large maps in chunks to improve performance
        if self.width > 3000 or self.height > 3000:
            self.use_tile_batching = True
            self.prerender_chunks()
        

    def prerender_chunks(self):
        """Pre-render map in chunks for better performance on large maps"""
        # Create chunk size based on screen dimensions (a bit larger to reduce number of chunks)
        self.chunk_size = 1024  # Size of each chunk in pixels
        
        # Calculate number of chunks in each dimension
        self.chunks_x = (self.width + self.chunk_size - 1) // self.chunk_size
        self.chunks_y = (self.height + self.chunk_size - 1) // self.chunk_size
        
        # Create a dictionary to store rendered chunks
        self.chunks = {}
        
        # Create a set to track which chunks have been rendered
        self.rendered_chunks = set()

    def get_chunk_key(self, x, y):
        """Get the key for a chunk based on world coordinates"""
        chunk_x = x // self.chunk_size
        chunk_y = y // self.chunk_size
        return (chunk_x, chunk_y)
        
    def render_chunk(self, chunk_x, chunk_y):
        """Render a specific chunk of the map"""
        # Create a new surface for this chunk
        chunk_surface = pygame.Surface((self.chunk_size, self.chunk_size), pygame.SRCALPHA)
        
        # Calculate the world coordinates for this chunk
        world_x = chunk_x * self.chunk_size
        world_y = chunk_y * self.chunk_size
        
        # Define the area this chunk covers
        chunk_rect = pygame.Rect(world_x, world_y, self.chunk_size, self.chunk_size)
        
        # Draw tiles that fall within this chunk
        for x, y, src_x, src_y, tile_id in self.level_data:
            if chunk_rect.collidepoint(x, y):
                # Adjust coordinates relative to chunk
                rel_x = x - world_x
                rel_y = y - world_y
                tile_rect = pygame.Rect(src_x, src_y, self.tile_size, self.tile_size)
                chunk_surface.blit(self.tileset_image, (rel_x, rel_y), tile_rect)
                
        # Draw decoration tiles in this chunk
        for x, y, src_x, src_y, tile_id in self.level_decorations:
            if chunk_rect.collidepoint(x, y):
                # Adjust coordinates relative to chunk
                rel_x = x - world_x
                rel_y = y - world_y
                tile_rect = pygame.Rect(src_x, src_y, self.tile_size, self.tile_size)
                chunk_surface.blit(self.tileset_decorations, (rel_x, rel_y), tile_rect)
        
        # Save this chunk
        self.chunks[(chunk_x, chunk_y)] = chunk_surface
        self.rendered_chunks.add((chunk_x, chunk_y))
        
        return chunk_surface

    def load_level(self, level_file):
        """ Loads level data from an LDtk file (JSON) """
        with open(level_file, 'r', encoding='utf-8') as f:
            project = json.load(f)  # Load file as JSON

        level_data_tileset = []
        level_data_decorations = []
        level_collisions = []

        # Get the first level (or search for a specific one by name)
        level = project["levels"][0]
        
        # Set level dimensions
        self.width = level["pxWid"]
        self.height = level["pxHei"]

        # For large maps, we'll optimize by checking if we need all tiles
        is_large_map = self.width > 3000 or self.height > 3000

        # Search for the tile layer
        for layer in level["layerInstances"]:
            if layer["__identifier"] == "Suelo_paredes" or layer["__identifier"] == "Muebles": 
                # For large maps, process tiles in batches to avoid memory spikes
                tiles = layer["gridTiles"]
                
                for tile in tiles:
                    tile_x = tile["px"][0]  # Position in pixels (x)
                    tile_y = tile["px"][1]  # Position in pixels (y)
                    tile_src_x = tile["src"][0]  # Position in the tileset (x)
                    tile_src_y = tile["src"][1]  # Position in the tileset (y)
                    tile_id = tile["t"]  # Tile ID within the tileset

                    if layer["__identifier"] == "Suelo_paredes":
                        level_data_tileset.append((tile_x, tile_y, tile_src_x, tile_src_y, tile_id))
                    else:
                        level_data_decorations.append((tile_x, tile_y, tile_src_x, tile_src_y, tile_id))

            if layer["__identifier"] == "Collisions": # Check if the layer is "Collisions" (the LDtk identifier for what is seen in the level)
                # For collision rects on large maps, limit processing
                tiles = layer["gridTiles"]
                
                # For large maps, use a sampling approach to reduce collision rectangles
                sample_rate = 1
                if is_large_map:
                    # For large maps, check collision tiles less frequently
                    # This is a tradeoff - fewer collision checks for better performance
                    # The game might have slightly less accurate collisions, but should be acceptable
                    sample_rate = 2
                
                for i, tile in enumerate(tiles):
                    if is_large_map and i % sample_rate != 0:
                        continue
                        
                    x = tile["px"][0]
                    y = tile["px"][1]
                    level_collisions.append(pygame.Rect(x, y, self.tile_size, self.tile_size))
     
        return level_data_tileset, level_data_decorations, level_collisions


    def draw(self, screen, camera):
        """ Draws the level on the screen based on the Tile Layer """
        # Get camera's visible area
        camera_rect = pygame.Rect(camera.camera_rect.x, camera.camera_rect.y, 
                                 camera.screen_width, camera.screen_height)
        # Add a buffer zone (one extra tile in each direction)
        buffer = self.tile_size * 2
        visible_area = pygame.Rect(camera_rect.x - buffer, camera_rect.y - buffer,
                                 camera_rect.width + buffer*2, camera_rect.height + buffer*2)
        
        # If using tile batching for large maps
        if self.use_tile_batching:
            # Get the chunks that are visible in the current view
            min_chunk_x = max(0, visible_area.left // self.chunk_size)
            max_chunk_x = min(self.chunks_x - 1, visible_area.right // self.chunk_size)
            min_chunk_y = max(0, visible_area.top // self.chunk_size)
            max_chunk_y = min(self.chunks_y - 1, visible_area.bottom // self.chunk_size)
            
            # For each visible chunk
            for chunk_x in range(min_chunk_x, max_chunk_x + 1):
                for chunk_y in range(min_chunk_y, max_chunk_y + 1):
                    chunk_key = (chunk_x, chunk_y)
                    
                    # If chunk is not rendered yet, render it
                    if chunk_key not in self.rendered_chunks:
                        self.render_chunk(chunk_x, chunk_y)
                    
                    # Draw the chunk at the appropriate position
                    chunk_surface = self.chunks[chunk_key]
                    world_x = chunk_x * self.chunk_size
                    world_y = chunk_y * self.chunk_size
                    chunk_rect = pygame.Rect(world_x, world_y, self.chunk_size, self.chunk_size)
                    screen.blit(chunk_surface, camera.apply_rect(chunk_rect))
        else:
            # For smaller maps, use the original tile-by-tile approach
            # Only draw tiles that are within the visible area
            for x, y, src_x, src_y, tile_id in self.level_data:
                tile_pos = pygame.Rect(x, y, self.tile_size, self.tile_size)
                if visible_area.colliderect(tile_pos):
                    tile_rect = pygame.Rect(src_x, src_y, self.tile_size, self.tile_size)
                    screen.blit(self.tileset_image, camera.apply_rect(tile_pos), tile_rect)
                    
            for x, y, src_x, src_y, tile_id in self.level_decorations:
                tile_pos = pygame.Rect(x, y, self.tile_size, self.tile_size)
                if visible_area.colliderect(tile_pos):
                    tile_rect = pygame.Rect(src_x, src_y, self.tile_size, self.tile_size)
                    screen.blit(self.tileset_decorations, camera.apply_rect(tile_pos), tile_rect)

    def get_level_collisions(self):
        return self.level_collisions