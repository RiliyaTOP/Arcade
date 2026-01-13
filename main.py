import arcade
from main_window import MainMenuView, SCREEN_WIDTH, SCREEN_HEIGHT, SCREEN_TITLE

def main():
    window = arcade.Window(
        SCREEN_WIDTH, 
        SCREEN_HEIGHT, 
        SCREEN_TITLE,
        resizable=True
    )
    main_menu = MainMenuView()
    window.show_view(main_menu)
    arcade.run()

if __name__ == "__main__":
    main()