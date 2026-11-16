"""Реализовать классическую игру «Змейка» с помощью Pygame.

Модуль содержит:
    GameObject: базовый класс игровых объектов.
    Apple: класс яблока, размещаемого на игровом поле.
    Snake: класс змейки и логика её движения.
    handle_keys: обработчик событий клавиатуры и окна.
    main: функция инициализации и запуска игры.
"""

from random import choice
import sys

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

SPEED = 7

screen = None
clock = None


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

        Атрибуты:
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

        Атрибуты:
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

    Методы:
        randomize_position: Выбрать свободную позицию для яблока.
        draw: Отрисовать яблоко на игровом поле.

    Класс наследует метод draw_cell() от GameObject.
    """

    def __init__(self, body_color=APPLE_COLOR, occupied_positions=None):
        """Создать яблоко с заданным цветом и свободной позицией.

        Атрибуты:
            body_color: Цвет яблока. По умолчанию используется APPLE_COLOR.
            occupied_positions: Занятые клетки. По умолчанию список пуст.

        Исключения:
            RuntimeError: Если на игровом поле нет свободной клетки.
        """
        super().__init__(position=None, body_color=body_color)
        self.randomize_position(occupied_positions)

    def randomize_position(self, occupied_positions=None):
        """Выбрать свободную позицию для яблока.

        При первом создании яблока позиция ещё не задана, поэтому выбирается
        случайная свободная клетка. При последующих вызовах новая позиция
        выбирается только тогда, когда текущая клетка занята змейкой. Метод
        обновляет атрибут self.position.

        Атрибуты:
            occupied_positions: Координаты занятых клеток. По умолчанию
                список занятых клеток пуст.

        Исключения:
            RuntimeError: Если на игровом поле не осталось свободных клеток.
        """
        occupied_positions = set(occupied_positions or [])
        if (
            self.position is not None
            and self.position not in occupied_positions
        ):
            return

        free_positions = [
            (x * GRID_SIZE, y * GRID_SIZE)
            for x in range(GRID_WIDTH)
            for y in range(GRID_HEIGHT)
            if (x * GRID_SIZE, y * GRID_SIZE) not in occupied_positions
        ]

        if not free_positions:
            raise RuntimeError(
                'На игровом поле не осталось свободных клеток для яблока.'
            )

        self.position = choice(free_positions)

    def draw(self):
        """Нарисовать яблоко и границу занимаемой им клетки."""
        self.draw_cell(self.position)


class Snake(GameObject):
    """Представить змейку и управлять её перемещением.

    Класс наследует от GameObject атрибут body_color и метод draw_cell().

    Атрибуты:
        length: Текущая длина змейки.
        positions: Координаты всех сегментов змейки.
        direction: Текущее направление движения.
        next_direction: Направление, которое будет применено на следующем ходу.
        last: Координаты последнего удалённого сегмента.
        body_color: Цвет змейки.

    Методы:
        update_direction: Применить выбранное направление движения.
        move: Переместить змейку на одну клетку.
        draw: Отрисовать голову и стереть прежнее положение хвоста.
        grow: Увеличить длину змейки.
        get_head_position: Получить координаты головы.
        reset: Сбросить состояние змейки.
    """

    def __init__(self, body_color=SNAKE_COLOR):
        """Создать змейку с заданным цветом и начальным состоянием.

        Атрибуты:
            body_color: Цвет змейки. По умолчанию используется SNAKE_COLOR.
        """
        super().__init__(position=None, body_color=body_color)
        self.reset()

    def update_direction(self):
        """Применить новое направление, заданное пользователем."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Переместить голову и обновить положение сегментов тела.

        При выходе за границу поля змейка появляется с противоположной
        стороны. Метод обновляет positions и last. Последний сегмент
        удаляется, если длина змейки не выросла.
        """
        head_x, head_y = self.get_head_position()
        delta_x, delta_y = self.direction

        new_head = (
            (head_x + delta_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + delta_y * GRID_SIZE) % SCREEN_HEIGHT,
        )

        self.positions.insert(0, new_head)

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Нарисовать новую голову и стереть прежнее положение хвоста.

        Остальные сегменты не перерисовываются: их изображения уже находятся
        на соответствующих клетках игровой поверхности.
        """
        if self.last is not None:
            self.draw_cell(
                self.last,
                body_color=BOARD_BACKGROUND_COLOR,
                border_color=None,
            )

        self.draw_cell(self.get_head_position())

    def grow(self):
        """Увеличить длину змейки и восстановить удалённый сегмент хвоста.

        Увеличивает атрибут length. Если при последнем перемещении хвостовой
        сегмент был удалён, добавляет его обратно в positions.
        """
        self.length += 1
        if self.last is not None:
            self.positions.append(self.last)
            self.last = None

    def get_head_position(self):
        """Вернуть координаты головы змейки.

        Возвращает:
            Кортеж с координатами верхнего левого угла головного сегмента.
        """
        return self.positions[0]

    def reset(self):
        """Сбросить змейку в исходное состояние.

        Устанавливает начальную длину, позицию, направление движения и
        очищает сохранённые данные о следующем направлении и хвосте.
        """
        self.length = 1
        self.positions = [INITIAL_POSITION]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обработать события окна и клавиатуры.

    При нажатии клавиш-стрелок обновляет next_direction переданного объекта.
    При закрытии окна или нажатии Esc завершает работу Pygame и программы.

    Атрибуты:
        game_object: Игровой объект, направление которого нужно изменить.

    Исключения:
        SystemExit: При закрытии окна или нажатии клавиши Esc.
    """
    for event in pg.event.get():
        if event.type == pg.QUIT:
            pg.quit()
            sys.exit()

        if event.type != pg.KEYDOWN:
            continue

        if event.key == pg.K_ESCAPE:
            pg.quit()
            sys.exit()

        if event.key in TURNS:
            new_direction, opposite = TURNS[event.key]
            if game_object.direction != opposite:
                game_object.next_direction = new_direction


def main():
    """Инициализировать игру и запустить основной игровой цикл.

    Создаёт игровое окно, змейку и яблоко, затем обрабатывает события,
    обновляет состояние объектов и перерисовывает игровое поле.
    Изменяет глобальные переменные screen и clock.
    """
    global screen, clock

    pg.init()
    screen = pg.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pg.display.set_caption('Змейка')
    clock = pg.time.Clock()

    snake = Snake()
    apple = Apple(occupied_positions=snake.positions)

    screen.fill(BOARD_BACKGROUND_COLOR)
    snake.draw()
    apple.draw()
    pg.display.update()

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.grow()
            try:
                apple.randomize_position(snake.positions)
            except RuntimeError:
                snake.draw()
                pg.display.update()
                print('Поздравляем! Вы заполнили всё игровое поле.')
                pg.quit()
                return

        elif snake.get_head_position() in snake.positions[4:]:
            snake.reset()
            apple.randomize_position(snake.positions)
            screen.fill(BOARD_BACKGROUND_COLOR)

        snake.draw()
        apple.draw()
        pg.display.update()


if __name__ == '__main__':
    main()
