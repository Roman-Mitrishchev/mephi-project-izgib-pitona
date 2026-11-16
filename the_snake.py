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

        Результат:
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

    Аргументы:
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
    """Запустить основной игровой цикл.

    Создаёт змейку и яблоко, затем обрабатывает события, обновляет
    состояние игровых объектов и перерисовывает игровое поле.
    Игровые экран и часы создаются при загрузке модуля.
    """
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
