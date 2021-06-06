from src.shared import Coord


class SnakeGameException(Exception):
    def __init__(self, coord: Coord):
        self.coord = coord


class WallHit(SnakeGameException):
    def __str__(self):
        return f"The snake hit the wall at the coordinates (x: {self.coord.x}, y: {self.coord.y})"


class BodyHit(SnakeGameException):
    def __str__(self):
        return f"The snake hit its own body at the coordinates (x: {self.coord.x}, y: {self.coord.y})"


class QuitGame(Exception):
    pass
