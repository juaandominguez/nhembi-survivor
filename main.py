from director import Director


def main():
    # Create the director instance
    director = Director()
    
    # Create and push the initial scene (main menu)
    director.push_scene("menu")

    # Start the game
    director.run()

if __name__ == "__main__":
    main()

