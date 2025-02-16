import pygame as pg
from Escenas.main_menu import MainMenu
from Escenas.scene_manager import SceneManager
from Escenas.settings_menu import SettingsScene
from Escenas.new_game_scene import NewGameScene

pg.init()

screen = pg.display.set_mode((800, 600))
pg.display.set_caption("Ñembis Fate: The last survivor")
clock = pg.time.Clock()

# Escenas
scene_manager = SceneManager(screen)
main_menu_scene = MainMenu(screen, scene_manager)
scene_manager.add_scene("MainMenuScene", main_menu_scene)
settings_scene = SettingsScene(screen, scene_manager)
scene_manager.add_scene("SettingsScene", settings_scene)
game_scene = NewGameScene(screen, scene_manager)
scene_manager.add_scene("NewGameScene", game_scene)
scene_manager.switch_scene("MainMenuScene")


while True:
    scene_manager.run_current_scene()

    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            quit()

    pg.display.update()
    clock.tick(60)