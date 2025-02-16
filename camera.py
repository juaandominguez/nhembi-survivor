import pygame

class Camera:
    def __init__(self, width, height, screen_width, screen_height):
        """
        Clase que maneja el desplazamiento de la cámara en un nivel.

        :param width: Ancho total del nivel en píxeles.
        :param height: Alto total del nivel en píxeles.
        :param screen_width: Ancho de la pantalla en píxeles.
        :param screen_height: Alto de la pantalla en píxeles.
        """
        self.camera_rect = pygame.Rect(0, 0, screen_width, screen_height)  # Zona visible
        self.width = width
        self.height = height
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, target):
        """
        Hace que la cámara siga al jugador.
        
        :param target: Objeto con atributos `x` y `y` (posiciones en el nivel).
        """
        x = target.rect.centerx - self.screen_width // 2
        y = target.rect.centery - self.screen_height // 2

        # Limitar el desplazamiento dentro del nivel
        x = max(0, min(x, self.width - self.screen_width))
        y = max(0, min(y, self.height - self.screen_height))

        self.camera_rect.topleft = (x, y)

    def apply(self, entity):
        """
        Aplica el desplazamiento de la cámara a una entidad.
        
        :param entity: Cualquier objeto que tenga un `rect` (jugador, enemigos, tiles, etc.).
        :return: Rect ajustado a la vista de la cámara.
        """
        return entity.rect.move(-self.camera_rect.x, -self.camera_rect.y)

    def apply_rect(self, rect):
        """
        Aplica el desplazamiento a un rectángulo, útil para dibujar tiles.
        
        :param rect: Un `pygame.Rect` a transformar.
        :return: Nuevo rectángulo ajustado a la vista de la cámara.
        """
        return rect.move(-self.camera_rect.x, -self.camera_rect.y)
