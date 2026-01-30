import arcade
from menu_view import MainMenuView, WIN_W, WIN_H
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


def main():
    window = arcade.Window(WIN_W, WIN_H, "MegaGameUltra")
    window.show_view(MainMenuView())
    arcade.run()

if __name__ == "__main__":
    main()
