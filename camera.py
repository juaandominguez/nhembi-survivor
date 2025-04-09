import pygame

class Camera:
    def __init__(self, width, height, screen_width, screen_height):
        """
        Class that handles camera movement in a level.

        :param width: Total width of the level in pixels.
        :param height: Total height of the level in pixels.
        :param screen_width: Width of the screen in pixels.
        :param screen_height: Height of the screen in pixels.
        """
        self.camera_rect = pygame.Rect(0, 0, screen_width, screen_height)  # Zona visible
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, target):
        """
        Makes the camera follow the player.

        :param target: Object with `x` and `y` attributes (positions in the level).
        """
        x = target.rect.centerx - self.screen_width // 2
        y = target.rect.centery - self.screen_height // 2

        # Limitar el desplazamiento dentro del nivel
        x = max(0, min(x, self.width - self.screen_width))
        y = max(0, min(y, self.height - self.screen_height))

        self.camera_rect.topleft = (x, y)

    def apply(self, entity):
        """
        Applies the camera offset to an entity.

        :param entity: Any object that has a `rect` (player, enemies, tiles, etc.).
        :return: Rect adjusted to the camera view.
        """
        return entity.rect.move(-self.camera_rect.x, -self.camera_rect.y)

    def apply_rect(self, rect):
        """
        Applies the offset to a rectangle, useful for drawing tiles.

        :param rect: A `pygame.Rect` to transform.
        :return: New rectangle adjusted to the camera view.
        """
        return rect.move(-self.camera_rect.x, -self.camera_rect.y)
