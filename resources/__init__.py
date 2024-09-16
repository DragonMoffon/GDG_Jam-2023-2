from typing import Callable
from contextlib import contextmanager
import importlib.resources as pkg_resources

from arcade import (
    load_texture as load_arcade_texture,
    load_spritesheet as load_arcade_spritesheet,
    Texture,
    SpriteSheet,
)
import resources.audio as audio
import resources.data as data
import resources.fonts as fonts
import resources.textures as texts
import resources.shaders as shaders

__all__ = (
    "make_package_file_opener",
    "make_package_string_loader",
    "make_package_binary_loader",
    "make_package_path_finder",
    "get_font_path",
    "get_wav_path",
    "get_ogg_path",
    "get_data_path",
    "get_png_path",
    "get_shader_path",
    "get_shader_text",
    "get_data_text",
    "open_png",
)


def make_package_file_opener(
    package,
    data_type: str,
    mode: str = "r",
    buffering: int = -1,
    encoding: str | None = None,
    errors: str | None = None,
    newline: str | None = None,
    closefd: bool = True,
    opener: Callable[[str, int], int] | None = None,
):
    """
    Create a reusable function for opening files of a particular type at a particular location
    Can also set new defaults for the `open` function used internally.

    See `open` for other arguments

    :param package: the location to open at, as a package str.
    :param data_type: the type to put as the `.type` for a file
    :return: A function which creates a context manager around an opened file
    """

    @contextmanager
    def _file_loader(
        name: str,
        _mode: str = mode,
        _buffering: int = buffering,
        _encoding: str | None = encoding,
        _errors: str | None = errors,
        _newline: str | None = newline,
        _closefd: bool = closefd,
        _opener: Callable[[str, int], int] | None = opener,
    ):
        """
        Open a file with a predetermined type and location with given name.
        Also has the arguments for `open` available. Custom defaults can be provided
        at the same time as the type and location

        See `open` for other arguments

        :param name: The name of the file to open (without .type) at the end.
        """
        file_name = f"{name}.{data_type}"
        file = None
        try:
            with pkg_resources.path(package, file_name) as path:
                file = open(
                    path,
                    _mode,
                    _buffering,
                    _encoding,
                    _errors,
                    _newline,
                    _closefd,
                    _opener,
                )
            yield file
        finally:
            if file is not None:
                file.close()

    return _file_loader


def make_package_string_loader(package, data_type: str, encoding: str = "utf-8"):
    def _str_loader(name: str):
        file_name = f"{name}.{data_type}"
        return pkg_resources.read_text(package, file_name, encoding=encoding)

    return _str_loader


def make_package_binary_loader(package, data_type: str):
    def _binary_loader(name: str):
        file_name = f"{name}.{data_type}"
        return pkg_resources.read_binary(package, file_name)

    return _binary_loader


def make_package_path_finder(package, data_type: str):
    def _path_finder(name: str):
        file_name = f"{name}.{data_type}"
        with pkg_resources.path(package, file_name) as path:
            return path.absolute()

    return _path_finder


# get path
get_font_path = make_package_path_finder(fonts, "ttf")
get_wav_path = make_package_path_finder(audio, "wav")
get_ogg_path = make_package_path_finder(audio, "ogg")
get_data_path = make_package_path_finder(data, "toml")
get_png_path = make_package_path_finder(texts, "png")
get_shader_path = make_package_path_finder(shaders, "glsl")

# get text
get_shader_text = make_package_string_loader(shaders, "glsl")
get_data_text = make_package_string_loader(data, "toml")

# open file
open_png = make_package_file_opener(texts, "png", mode="rb")


# load textures
def load_texture(name: str) -> Texture:
    return load_arcade_texture(get_png_path(name))


def load_spritesheet(name: str) -> SpriteSheet:
    return load_arcade_spritesheet(get_png_path(name))
