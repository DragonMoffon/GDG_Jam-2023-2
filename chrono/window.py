from arcade import Window as _Window, View
from chrono.nav import Navigation, CreationNavigation, PreserveNavigation

from chrono.game.game_view import Game
from chrono.menus.main_menu import MainMenu

class Window(_Window):

    def __init__(self):
        super().__init__(1280, 720, "Chronocide - UoA GDG Jam 2")
        self._navigations: dict[str, Navigation] = {}
        self._game_view: Game = None

    @classmethod
    def launch(cls):
        win = cls()
        win.register_nav("to_main_menu", CreationNavigation(MainMenu))
        win._game_view = Game()
        win.register_nav("to_game_sceneless", PreserveNavigation("to_game_sceneless", win._game_view, win._game_view.reset))

        win.center_window()
        win.nav("to_main_menu")
        win.run()

    def register_nav(self, name: str, nav: Navigation, *, replace: bool = False) -> None:
        if not replace and name in self._navigations:
            raise ValueError(f"{name} is already the navigation {self._navigations[name]}")
        self._navigations[name] = nav

    def deregister_nav(self, name: str) -> None:
        self._navigations.pop(name, None)

    def get_nav(self, name: str) -> Navigation:
        return self._navigations[name]
    
    def nav(self, name: str) -> View:
        v = self._navigations[name].navigate()
        if v is None:
            print('Failed to Navigate')
            return v
        self.show_view(v)
        return v