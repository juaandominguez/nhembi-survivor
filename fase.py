# -*- coding: utf-8 -*-

import pygame, scene
from scene import *
from characters import *
from pygame.locals import *
from level import Level
from camera import Camera

# -------------------------------------------------
# Clase Fase

class Fase(Scene):
    def __init__(self, director):
        # Primero invocamos al constructor de la clase padre
        Scene.__init__(self, director)

        # Cargar el nivel
        self.level = Level("levels/pasilloFIC.ldtk")
        
        # Configurar la cámara
        self.camera = Camera(self.level.width, self.level.height, ANCHO_PANTALLA, ALTO_PANTALLA)
        
        # Obtener las colisiones del nivel
        self.collisionTiles = self.level.get_level_collisions()
        
        # Creamos los sprites de los jugadores
        self.jugador = Player()
        self.grupoJugador = pygame.sprite.Group(self.jugador)

        # Ponemos a los jugadores en sus posiciones iniciales
        self.jugador.set_position((200, 200))

        # Y los enemigos que tendran en este decorado
        enemy1 = Rat()
        enemy1.set_position((400, 300))

        # Creamos un grupo con los enemigos
        self.grupoEnemigos = pygame.sprite.Group(enemy1)

        # Creamos un grupo con los Sprites que se mueven
        self.grupoSpritesDinamicos = pygame.sprite.Group(self.jugador, enemy1)
        # Creamos otro grupo con todos los Sprites
        self.grupoSprites = pygame.sprite.Group(self.jugador, enemy1)

    def update(self, tiempo):
        # Primero, se indican las acciones que van a hacer los enemigos segun como esten los jugadores
        for enemigo in iter(self.grupoEnemigos):
            enemigo.move_cpu(self.jugador)

        # Actualizamos los Sprites dinamicos
        self.grupoSpritesDinamicos.update(tiempo)

        # Actualizar la cámara para que siga al jugador
        self.camera.update(self.jugador)

        # Comprobamos si hay colision entre algun jugador y algun enemigo
        if pygame.sprite.groupcollide(self.grupoJugador, self.grupoEnemigos, False, False) != {}:
            # Se le dice al director que salga de esta Scene y ejecute la siguiente en la pila
            # self.director.pop_scene()
            pass
        
        # Comprobar colisiones con el mapa
        for tile in self.collisionTiles:
            if self.jugador.rect.colliderect(tile):
                # Determinar la dirección de la colisión
                dx = (self.jugador.rect.centerx - tile.centerx)
                dy = (self.jugador.rect.centery - tile.centery)
                
                # Ajustar la posición del jugador según la dirección de la colisión
                if abs(dx) > abs(dy):
                    # Colisión horizontal
                    if dx > 0:
                        self.jugador.rect.left = tile.right
                    else:
                        self.jugador.rect.right = tile.left
                else:
                    # Colisión vertical
                    if dy > 0:
                        self.jugador.rect.top = tile.bottom
                    else:
                        self.jugador.rect.bottom = tile.top

    def render(self, pantalla):
        # Primero dibujamos el nivel
        self.level.draw(pantalla, self.camera)
        
        # Luego los Sprites
        for sprite in self.grupoSprites:
            pantalla.blit(sprite.image, self.camera.apply(sprite))

    def handle_events(self, event):
        # Indicamos la acción a realizar segun la tecla pulsada para cada jugador
        teclasPulsadas = pygame.key.get_pressed()
        self.jugador.move(teclasPulsadas, K_UP, K_DOWN, K_LEFT, K_RIGHT)

