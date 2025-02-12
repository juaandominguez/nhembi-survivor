import pygame as pg

pg.init()

screen = pg.display.set_mode((800, 600))
pg.display.set_caption("Ñembis Fate: The last survivor")
clock = pg.time.Clock()

while True:
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()
    pg.display.update()
    clock.tick(60)