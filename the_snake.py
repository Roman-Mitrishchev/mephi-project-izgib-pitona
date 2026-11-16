"""Реализовать классическую игру «Змейка» с помощью Pygame.

Модуль содержит:
    GameObject: базовый класс игровых объектов.
    Apple: класс яблока, размещаемого на игровом поле.
    Snake: класс змейки и логика её движения.
    handle_keys: обработчик событий клавиатуры и окна.
    main: функция инициализации и запуска игры.
"""

import sys
from random import choice

import pygame as pg

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
INITIAL_POSITION = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

TURNS = {
    pg.K_UP: (UP, DOWN),
    pg.K_DOWN: (DOWN, UP),
    pg.K_LEFT: (LEFT, RIGHT),
    pg.K_RIGHT: (RIGHT, LEFT),
}

BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
PURPLE = (160, 32, 240)
CYAN = (93, 216, 228)

BOARD_BACKGROUND_COLOR = BLACK
BORDER_COLOR = CYAN
APPLE_COLOR = RED
SNAKE_COLOR = GREEN

SPEED = 20

pg.init()
screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pg.display.set_caption('Змейка')
clock = pg.time.Clock()


class GameObject:
    """Представить базовый класс игрового объекта.

    Атрибуты:
        position: Координаты объекта на игровом поле.
        body_color: Цвет объекта.

    Методы:
        draw_cell: Отрисовать одну ячейку игрового поля.
        draw: Определить интерфейс отрисовки объекта.

    Интерфейс для дочерних классов:
        Дочерние классы должны переопределять метод draw().
    """

    def __init__(
        self,
        position=INITIAL_POSITION,
        body_color=None,
    ):
        """Инициализировать объект с заданными позицией и цветом.

        Аргументы:
            position: Координаты объекта. По умолчанию — центр поля.
            body_color: Цвет объекта. По умолчанию не задан.
        """
        self.position = position
        self.body_color = body_color

    def draw_cell(
        self,
        position,
        body_color=None,
        border_color=BORDER_COLOR,
    ):
        """Отрисовать одну ячейку игрового поля.

        Цвет заливки по умолчанию берётся из атрибута объекта. При
        необходимости можно передать другой цвет или отключить границу.
        Отрисовка выполняется непосредственно на игровой поверхности screen.

        Аргументы:
            position: Координаты верхнего левого угла ячейки.
            body_color: Цвет заливки. По умолчанию используется цвет объекта.
            border_color: Цвет границы. Значение None отключает границу.
        """
        color = self.body_color if body_color is None else body_color
        cell = pg.Rect(position, (GRID_SIZE, GRID_SIZE))
        pg.draw.rect(screen, color, cell)

        if border_color is not None:
            pg.draw.rect(screen, border_color, cell, 1)

    def draw(self):
        """Определить обязательный метод отрисовки игрового объекта.

        Дочерние классы должны переопределять этот метод. Вызов базовой
        реализации вызывает NotImplementedError с именем класса, в котором
        метод не был переопределён.

        Исключения:
            NotImplementedError: Если дочерний класс не переопределил draw().
        """
        raise NotImplementedError(
            f'Метод draw() не переопределён в классе {type(self).__name__}.'
        )


class Apple(GameObject):
    """Представить яблоко, которое появляется в свободной клетке поля.

    Атрибуты:
        position: Координаты яблока на игровом поле.
        body_color: Цвет яблока.
