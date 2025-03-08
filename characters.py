import pygame, sys, os
from pygame.locals import *
from scene import *
from resource_manager import *
from collections import namedtuple

# -------------------------------------------------
# -------------------------------------------------
# Constants
# -------------------------------------------------
# -------------------------------------------------

ActionTuple = namedtuple('ActionTuple', 'prefix numImages') 
AVAILABLE_ACTIONS =[ActionTuple('walk',[8,8,8,8]), ActionTuple('slash',[6,6,6,6]), ActionTuple('hurt',[6])]


# Movements
IDLE = 0
LEFT = 1
RIGHT = 2
UP = 3
DOWN = 4


# Speed from different characters
SPEED_MULTIPLIER = 0.2
SPEED_PLAYER = (0.1,0.1)
ANIMATION_PLAYER_DELAY = 5 # updates between frames, should be different for each posture

# -------------------------------------------------
# -------------------------------------------------
# Clases de los objetos del juego
# -------------------------------------------------
# -------------------------------------------------


# -------------------------------------------------
# Class MySprite
class MySprite(pygame.sprite.Sprite):
    "Sprites from the game"
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.position = (0, 0)
        self.speed = (0, 0)
        self.scroll   = (0, 0)

    def setPosition(self, posicion):
        self.position = posicion
        self.rect.left = self.position[0] - self.scroll[0]
        self.rect.bottom = self.position[1] - self.scroll[1]

    def setScreenPosition(self, scrollDecoration):
        self.scroll = scrollDecoration;
        (scrollx, scrolly) = self.scroll;
        (posx, posy) = self.position;
        self.rect.left = posx - scrollx;
        self.rect.bottom = posy - scrolly;

    def incrementPosition(self, increment):
        (posx, posy) = self.position
        (incrementx, incrementy) = increment
        self.setPosition((posx+incrementx, posy+incrementy))

    def update(self, time):
        incrementx = self.speed[0]*time
        incrementy = self.speed[1]*time
        self.incrementPosition((incrementx, incrementy))



# -------------------------------------------------
# Clases Personaje

#class Personaje(pygame.sprite.Sprite):
class Character(MySprite):
    "Any character from the game"

    def __init__(self, imagePrefix, speedMovement, animationDelay):

        MySprite.__init__(self);

        SpriteCharacter= namedtuple('SpriteCharacter', 'image coords') 

        # Map{action, (image, coordinates)}
        self.spriteCharacter = {}

        self.coordinatesFile = []

        for action in AVAILABLE_ACTIONS:
            self.spriteCharacter[action.prefix] = SpriteCharacter(ResourceManager.loadImage(imagePrefix + '/' + action.prefix + '.png'),
                                            ResourceManager.loadCoordinates(imagePrefix + '/' + action.prefix + '.txt'))
            self.coordinates = self.spriteCharacter[action.prefix].coords
            data = self.coordinates.split()
            print(f"Data for action {action.prefix}: {len(data)} {len(action.numImages)}") 
            self.coordinatesFile.append([])
            for line in range(0, len(action.numImages)):
                self.coordinatesFile.append([])
                tmp = self.coordinatesFile[line]
                for i in range(0, action.numImages[line]):
                    index = line * len(action.numImages) + i * 4
                    tmp.append(pygame.Rect((int(data[index]), int(data[index+1])), (int(data[index+2]), int(data[index+3]))))

        self.movement = IDLE

        # Delay for the movement of the character in the animation
        self.movementDelay = 0;

        # Initial posture of the sprite
        self.numPosture = IDLE

        print(f"Coordinates: {self.coordinatesFile}")

        # Rect of the sprite
        self.rect = pygame.Rect(0, 0, self.coordinatesFile[self.numPosture][0][0], self.coordinatesFile[self.numPosture][0][0])

        self.speedMovement = speedMovement
        self.animationDelay = animationDelay

        self.updatePosture()


    # Base method to perform the movement: simply indicates which one will do, and stores it
    def move(self, movement):
        self.movement = movement


    def updatePosture(self, action = 'walk'):
        self.movementDelay += 1
        
        if self.movementDelay >= self.animationDelay:
            self.movementDelay = 0
            
        if self.movement != IDLE:
            self.numPosture += 1
            if self.numPosture >= len(self.coordinatesFile[self.movement]):
                self.numPosture = 0

        print(f"{self.coordinatesFile[self.movement][self.numPosture]}")
        
        self.image = self.spriteCharacter[action].image.subsurface(self.coordinatesFile[self.movement][self.numPosture])



    def update(self, time):

        (speedx, speedy) = self.speed

        if self.movement == UP:
            speedy = -self.speedMovement
        elif self.movement == DOWN:
            speedy = self.speedMovement

        if self.movement == LEFT:
            speedx = -self.speedMovement
        elif self.movement == RIGHT:
            speedx = self.speedMovement


        if speedx != 0 or speedy != 0:
            self.moving = True
            length = (speedx ** 2 + speedy ** 2) ** 0.5 
            speedx = (speedx / length) * self.speed
            speedy = (speedy / length) * self.speed

            if abs(speedy) > abs(speedx):
                self.movement = DOWN if speedy > 0 else UP
            else:
                self.movement = RIGHT if speedx > 0 else LEFT


        self.updatePosture()

        self.speed = (speedx, speedy)

        MySprite.update(self, time)
        
        return



# -------------------------------------------------
# Clase Jugador

class Player(Character):
    "Thiagic"
    def __init__(self):
        # Invocamos al constructor de la clase padre con la configuracion de este personaje concreto
        Character.__init__(self,'thiagic', SPEED_MULTIPLIER, ANIMATION_PLAYER_DELAY);


    def move(self, teclasPulsadas, arriba, abajo, izquierda, derecha):
        if teclasPulsadas[arriba]:
            Player.move(self,UP)
        elif teclasPulsadas[izquierda]:
            Player.move(self,LEFT)
        elif teclasPulsadas[derecha]:
            Player.move(self,RIGHT)
        else:
            Player.move(self,IDLE)


# -------------------------------------------------
# Clase NoJugador

class NoJugador(Character):
    "El resto de personajes no jugadores"
    def __init__(self, archivoImagen, archivoCoordenadas, numImagenes, velocidad, velocidadSalto, retardoAnimacion):
        # Primero invocamos al constructor de la clase padre con los parametros pasados
        Character.__init__(self, archivoImagen, archivoCoordenadas, numImagenes, velocidad, velocidadSalto, retardoAnimacion);

    # Aqui vendria la implementacion de la IA segun las posiciones de los jugadores
    # La implementacion por defecto, este metodo deberia de ser implementado en las clases inferiores
    #  mostrando la personalidad de cada enemigo
    def mover_cpu(self, jugador1, jugador2):
        # Por defecto un enemigo no hace nada
        #  (se podria programar, por ejemplo, que disparase al jugador por defecto)
        return

# -------------------------------------------------
# Clase Sniper
""" 
class Sniper(NoJugador):
    "El enemigo 'Sniper'"
    def __init__(self):
        # Invocamos al constructor de la clase padre con la configuracion de este personaje concreto
        NoJugador.__init__(self,'Sniper.png','coordSniper.txt', [5, 10, 6], VELOCIDAD_SNIPER, VELOCIDAD_SALTO_SNIPER, RETARDO_ANIMACION_SNIPER);

    # Aqui vendria la implementacion de la IA segun las posiciones de los jugadores
    # La implementacion de la inteligencia segun este personaje particular
    def mover_cpu(self, jugador1, jugador2):

        # Movemos solo a los enemigos que esten en la pantalla
        if self.rect.left>0 and self.rect.right<ANCHO_PANTALLA and self.rect.bottom>0 and self.rect.top<ALTO_PANTALLA:

            # Por ejemplo, intentara acercarse al jugador mas cercano en el eje x
            # Miramos cual es el jugador mas cercano
            if abs(jugador1.posicion[0]-self.posicion[0])<abs(jugador2.posicion[0]-self.posicion[0]):
                jugadorMasCercano = jugador1
            else:
                jugadorMasCercano = jugador2
            # Y nos movemos andando hacia el
            if jugadorMasCercano.posicion[0]<self.posicion[0]:
                Personaje.move(self,LEFT)
            else:
                Personaje.move(self,RIGHT)

        # Si este personaje no esta en pantalla, no hara nada
        else:
            Personaje.move(self,IDLE)

 """