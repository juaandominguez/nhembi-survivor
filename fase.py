# -*- coding: utf-8 -*-

import pygame, scene
from scene import *
from characters import *
from pygame.locals import *

# -------------------------------------------------
# Clase Fase

class Fase(Scene):
    def __init__(self, director):

        # Habria que pasarle como parámetro el número de fase, a partir del cual se cargue
        #  un fichero donde este la configuracion de esa fase en concreto, con cosas como
        #   - Nombre del archivo con el decorado
        #   - Posiciones de las plataformas
        #   - Posiciones de los enemigos
        #   - Posiciones de inicio de los jugadores
        #  etc.
        # Y cargar esa configuracion del archivo en lugar de ponerla a mano, como aqui abajo
        # De esta forma, se podrian tener muchas fases distintas con esta clase

        # Primero invocamos al constructor de la clase padre
        Scene.__init__(self, director)


        # Que parte del decorado estamos visualizando
        self.scrollx = 0
        #  En ese caso solo hay scroll horizontal
        #  Si ademas lo hubiese vertical, seria self.scroll = (0, 0)

        # Creamos los sprites de los jugadores
        self.jugador = Player()
        self.grupoJugador = pygame.sprite.Group( self.jugador )

        # Ponemos a los jugadores en sus posiciones iniciales
        self.jugador.setPosition((200, 200))

        # Y los enemigos que tendran en este decorado
        enemy1 = Rat()
        enemy1.setPosition((1000, 418))

        # Creamos un grupo con los enemigos
        self.grupoEnemigos = pygame.sprite.Group( enemy1 )

        # Creamos un grupo con los Sprites que se mueven
        #  En este caso, solo los personajes, pero podría haber más (proyectiles, etc.)
        self.grupoSpritesDinamicos = pygame.sprite.Group( self.jugador, enemy1 )
        # Creamos otro grupo con todos los Sprites
        self.grupoSprites = pygame.sprite.Group( self.jugador, enemy1 )



    """  
    # Devuelve True o False según se ha tenido que desplazar el scroll
    def actualizarScrollOrdenados(self, jugadorIzq, jugadorDcha):
        # Si ambos jugadores se han ido por ambos lados de los dos bordes
        if (jugadorIzq.rect.left<MINIMO_X_JUGADOR) and (jugadorDcha.rect.right>MAXIMO_X_JUGADOR):

            # Colocamos al jugador que esté a la izquierda a la izquierda de todo
            jugadorIzq.setPosition((self.scrollx+MINIMO_X_JUGADOR, jugadorIzq.posicion[1]))
            # Colocamos al jugador que esté a la derecha a la derecha de todo
            jugadorDcha.setPosition((self.scrollx+MAXIMO_X_JUGADOR-jugadorDcha.rect.width, jugadorDcha.posicion[1]))
            
            return False; # No se ha actualizado el scroll

        # Si el jugador de la izquierda se encuentra más allá del borde izquierdo
        if (jugadorIzq.rect.left<MINIMO_X_JUGADOR):
            desplazamiento = MINIMO_X_JUGADOR - jugadorIzq.rect.left

            # Si el Scenerio ya está a la izquierda del todo, no lo movemos mas
            if self.scrollx <= 0:
                self.scrollx = 0

                # En su lugar, colocamos al jugador que esté más a la izquierda a la izquierda de todo
                jugadorIzq.setPosition((MINIMO_X_JUGADOR, jugadorIzq.posicion[1]))

                return False; # No se ha actualizado el scroll

            # Si no, es posible que el jugador de la derecha no se pueda desplazar
            #  tantos pixeles a la derecha por estar muy cerca del borde derecho
            elif ((MAXIMO_X_JUGADOR-jugadorDcha.rect.right)<desplazamiento):
                
                # En este caso, ponemos el jugador de la izquierda en el lado izquierdo
                jugadorIzq.setPosition((jugadorIzq.posicion[0]+desplazamiento, jugadorIzq.posicion[1]))

                return False; # No se ha actualizado el scroll

            # Si se puede hacer scroll a la izquierda
            else:
                # Calculamos el nivel de scroll actual: el anterior - desplazamiento
                #  (desplazamos a la izquierda)
                self.scrollx = self.scrollx - desplazamiento;

                return True; # Se ha actualizado el scroll

        # Si el jugador de la derecha se encuentra más allá del borde derecho
        if (jugadorDcha.rect.right>MAXIMO_X_JUGADOR):

            # Se calcula cuantos pixeles esta fuera del borde
            desplazamiento = jugadorDcha.rect.right - MAXIMO_X_JUGADOR

            # Si el Scenerio ya está a la derecha del todo, no lo movemos mas
            if self.scrollx + ANCHO_PANTALLA >= self.decorado.rect.right:
                self.scrollx = self.decorado.rect.right - ANCHO_PANTALLA

                # En su lugar, colocamos al jugador que esté más a la derecha a la derecha de todo
                jugadorDcha.setPosition((self.scrollx+MAXIMO_X_JUGADOR-jugadorDcha.rect.width, jugadorDcha.posicion[1]))

                return False; # No se ha actualizado el scroll

            # Si no, es posible que el jugador de la izquierda no se pueda desplazar
            #  tantos pixeles a la izquierda por estar muy cerca del borde izquierdo
            elif ((jugadorIzq.rect.left-MINIMO_X_JUGADOR)<desplazamiento):

                # En este caso, ponemos el jugador de la derecha en el lado derecho
                jugadorDcha.setPosition((jugadorDcha.posicion[0]-desplazamiento, jugadorDcha.posicion[1]))

                return False; # No se ha actualizado el scroll

            # Si se puede hacer scroll a la derecha
            else:

                # Calculamos el nivel de scroll actual: el anterior + desplazamiento
                #  (desplazamos a la derecha)
                self.scrollx = self.scrollx + desplazamiento;

                return True; # Se ha actualizado el scroll

        # Si ambos jugadores están entre los dos límites de la pantalla, no se hace nada
        return False;
 """




    # Se actualiza el decorado, realizando las siguientes acciones:
    #  Se indica para los personajes no jugadores qué movimiento desean realizar según su IA
    #  Se mueven los sprites dinámicos, todos a la vez
    #  Se comprueba si hay colision entre algun jugador y algun enemigo
    #  Se comprueba si algún jugador ha salido de la pantalla, y se actualiza el scroll en consecuencia
    #     Actualizar el scroll implica tener que desplazar todos los sprites por pantalla
    #  Se actualiza la posicion del sol y el color del cielo
    def update(self, tiempo):

        # Primero, se indican las acciones que van a hacer los enemigos segun como esten los jugadores
        for enemigo in iter(self.grupoEnemigos):
            pass
            #enemigo.mover_cpu(self.jugador1)
        # Esta operación es aplicable también a cualquier Sprite que tenga algún tipo de IA
        # En el caso de los jugadores, esto ya se ha realizado

        # Actualizamos los Sprites dinamicos
        # De esta forma, se simula que cambian todos a la vez
        # Esta operación de update ya comprueba que los movimientos sean correctos
        #  y, si lo son, realiza el movimiento de los Sprites

        #self.grupoSpritesDinamicos.update(self.grupoPlataformas, tiempo)

        # Dentro del update ya se comprueba que todos los movimientos son válidos
        #  (que no choque con paredes, etc.)

        # Los Sprites que no se mueven no hace falta actualizarlos,
        #  si se actualiza el scroll, sus posiciones en pantalla se actualizan más abajo
        # En cambio, sí haría falta actualizar los Sprites que no se mueven pero que tienen que
        #  mostrar alguna animación

        # Comprobamos si hay colision entre algun jugador y algun enemigo
        # Se comprueba la colision entre ambos grupos
        # Si la hay, indicamos que se ha finalizado la fase
        if pygame.sprite.groupcollide(self.grupoJugador, self.grupoEnemigos, False, False)!={}:
            # Se le dice al director que salga de esta Scene y ejecute la siguiente en la pila
            self.director.salirScene()

        # Actualizamos el scroll
  
        # Actualizamos el fondo:
        #  la posicion del sol y el color del cielo

        
    def render(self, pantalla):
        # Luego los Sprites
        self.grupoSprites.draw(pantalla)


    def handle_events(self, event):

        # Indicamos la acción a realizar segun la tecla pulsada para cada jugador
        teclasPulsadas = pygame.key.get_pressed()
        self.jugador.move(teclasPulsadas, K_UP, K_DOWN, K_LEFT, K_RIGHT)

