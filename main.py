from director import Director
from Escenas.main_menu import MainMenu

def main():
    # Create the director instance
    director = Director()
    
    # Create and push the initial scene (main menu)
    initial_scene = MainMenu(director)
    director.push_scene(initial_scene)
    
    # Start the game
    director.run()

if __name__ == "__main__":
    main()

