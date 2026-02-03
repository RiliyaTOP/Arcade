import arcade
from menu_view import MainMenuView, WIN_W, WIN_H, save_settings
import warnings
warnings.filterwarnings("ignore", category=UserWarning)


def main():
    class AppWindow(arcade.Window):
        def on_close(self):
            try:
                save_settings()
            except Exception:
                pass
            super().on_close()

    window = AppWindow(WIN_W, WIN_H, "MegaGameUltra")
    window.show_view(MainMenuView())
    arcade.run()

if __name__ == "__main__":
    main()
