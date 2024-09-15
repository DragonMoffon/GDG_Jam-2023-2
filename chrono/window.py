from arcade import Window as _Window, View
from chrono.nav import Navigation, CreationNavigation, PreserveNavigation

from chrono.input import Input

from chrono.menus.main_menu import MainMenu
from chrono.game.game_view import GameView


class Window(_Window):

    def __init__(self):
        super().__init__(1280, 720, "Chronocide - UoA GDG Jam 2", update_rate=1 / 1000)
        Input.initialise()

        self._navigations: dict[str, Navigation] = {}
        self._game_view: GameView = None

    @classmethod
    def launch(cls):
        win = cls()
        win.register_nav("to_main_menu", CreationNavigation(MainMenu))
        win._game_view = GameView()
        win.register_nav(
            "to_game_levelless",
            PreserveNavigation(
                "to_game_levelless", win._game_view, win._game_view.reset
            ),
        )

        win.center_window()
        win.nav("to_main_menu")
        win.run()

    def _dispatch_updates(self, delta_time: float) -> None:
        Input.manager.update()
        super()._dispatch_updates(delta_time)

    def register_nav(
        self, name: str, nav: Navigation, *, replace: bool = False
    ) -> None:
        if not replace and name in self._navigations:
            raise ValueError(
                f"{name} is already the navigation {self._navigations[name]}"
            )
        self._navigations[name] = nav

    def deregister_nav(self, name: str) -> None:
        self._navigations.pop(name, None)

    def get_nav(self, name: str) -> Navigation:
        return self._navigations[name]

    def nav(self, name: str) -> View:
        v = self._navigations[name].navigate()
        if v is None:
            print("Failed to Navigate")
            return v
        self.show_view(v)
        return v