from random import randint

import pygame

SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

BOARD_BACKGROUND_COLOR = (0, 0, 0)
BORDER_COLOR = (93, 216, 228)
APPLE_COLOR = (255, 0, 0)
SNAKE_COLOR = (0, 255, 0)

SPEED = 7

pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption('Изгиб питона')
clock = pygame.time.Clock()


class GameObject:
    """Базовый класс игрового объекта."""

    def __init__(self):
        """Задать начальную позицию и цвет объекта."""
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.body_color = None

    def draw(self):
        """Отрисовать объект на игровом поле.
        Метод предназначен для переопределения в дочерних классах.
        """
        pass


class Apple(GameObject):
    """Класс яблока, которое появляется в случайной клетке поля."""

    def __init__(self):
        """Создать яблоко, задать его цвет и начальную позицию."""
        super().__init__()
        self.body_color = APPLE_COLOR
        self.randomize_position()

    def randomize_position(self):
        """Переместить яблоко в случайную клетку игрового поля."""
        self.position = (
            randint(0, GRID_WIDTH - 1) * GRID_SIZE,
            randint(0, GRID_HEIGHT - 1) * GRID_SIZE,
        )

    def draw(self):
        """Нарисовать яблоко."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)


class Snake(GameObject):
    """Класс змейки: хранит сегменты и управляет их перемещением."""

    def __init__(self):
        """Создать змейку длиной в один сегмент."""
        super().__init__()
        self.length = 1
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.body_color = SNAKE_COLOR
        self.last = None

    def update_direction(self):
        """Применить новое направление, заданное пользователем."""
        if self.next_direction is not None:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Переместить голову на одну клетку и обновить положение тела.
        При выходе за границу поля змейка появляется с противоположной
        стороны. Последний сегмент удаляется, если длина змейки не выросла.
        """
        head_x, head_y = self.get_head_position()
        delta_x, delta_y = self.direction

        new_head = (
            (head_x + delta_x * GRID_SIZE) % SCREEN_WIDTH,
            (head_y + delta_y * GRID_SIZE) % SCREEN_HEIGHT,
        )

        self.positions.insert(0, new_head)
        self.position = new_head

        if len(self.positions) > self.length:
            self.last = self.positions.pop()
        else:
            self.last = None

    def draw(self):
        """Нарисовать сегменты змейки и стереть прежнее положение хвоста."""
        for position in self.positions[:-1]:
            rect = pygame.Rect(position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, self.body_color, rect)

        head_rect = pygame.Rect(
            self.positions[0], (GRID_SIZE, GRID_SIZE)
        )
        pygame.draw.rect(screen, self.body_color, head_rect)

        if self.last is not None:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self):
        """Вернуть координаты головы змейки."""
        return self.positions[0]

    def reset(self):
        """Вернуть змейку в исходное состояние после столкновения."""
        self.length = 1
        self.position = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.positions = [self.position]
        self.direction = RIGHT
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Обработать закрытие окна и нажатия клавиш управления змейкой."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit

        if event.type != pygame.KEYDOWN:
            continue

        if event.key == pygame.K_UP and game_object.direction != DOWN:
            game_object.next_direction = UP
        elif event.key == pygame.K_DOWN and game_object.direction != UP:
            game_object.next_direction = DOWN
        elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
            game_object.next_direction = LEFT
        elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
            game_object.next_direction = RIGHT

def main():
    """Инициализировать игру и запустить основной игровой цикл."""

    snake = Snake()
    apple = Apple()

    while apple.position in snake.positions:
        apple.randomize_position()

    screen.fill(BOARD_BACKGROUND_COLOR)
    pygame.display.update()

    while True:
        clock.tick(SPEED)

        handle_keys(snake)
        snake.update_direction()
        snake.move()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            apple.randomize_position()
            while apple.position in snake.positions:
                apple.randomize_position()

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()
            while apple.position in snake.positions:
                apple.randomize_position()
            screen.fill(BOARD_BACKGROUND_COLOR)

        snake.draw()
        apple.draw()
        pygame.display.update()


if __name__ == '__main__':
    main()
