from random import randint

# Классы исключений
# Общий класс исключений
class BoardException(Exception):
    pass

# выстрелили за доску
class BoardOutEcxeption(BoardException):
    def __str__(self):
        return "Вы пытаетесь выстрелить за доску!"

# уже стреляли в этй клетку
class BoardUsedException(BoardException):
    def __str__(self):
        return "Вы уже стреляли в эту клетку!"

# для размещения кораблей
class BoardWrongShipException(BoardException):
    pass

# Класс точек на поле
class Dot:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return f'Dot({self.x}, {self.y})'

# Класс корабля
class Ship:
    def __init__(self, bow, length, roat):
        self.bow = bow
        self.length = length
        self.roat = roat
        self.lives = length

    @property
    def dots(self):
        ship_dots = []
        for i in range(self.length):
            curent_x = self.bow.x
            curent_y = self.bow.y

            if self.roat == 0:
                curent_x += i

            elif self.roat == 1:
                curent_y += i

            ship_dots.append(Dot(curent_x, curent_y))

        return ship_dots

    def shooten(self, shot):
        return shot in self.dots

# класс доски
class Board:
    def __init__(self, hidden = False, size = 6):
        self.hidden = hidden
        self.size = size
        # счетчик пораженных кораблей
        self.count = 0
        # атрибут содержит сетку, если в клетке О, в нее не стреляли
        self.field = [["o"] * size for _ in range(size)]
        # счетчик занятых клеток
        self.busy = []
        # список кораблей доски
        self.ships = []

    # размещение корабля на поле
    def add_ship(self, ship):
        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contur(ship)

    # метод для проверки смежных с кораблем ячеек
    def contur(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                curent = Dot(d.x + dx, d.y + dy)
                if not(self.out(curent)) and curent not in self.busy:
                    if verb:
                        self.field[curent.x][curent.y] = "."
                    self.busy.append(curent)

    # создание поля
    def __str__(self):
        res = ""
        res += "  | 1 | 2 | 3 | 4 | 5 | 6 |"
        for i, row in enumerate(self.field):
            res += f"\n{i+1} | " + " | ".join(row) + " |"

        if self.hidden:
            res = res.replace("■", "о")
        return res

    # Метод для проверки не вышел ли корабль за рамки поля
    def out(self, d):
        return not((0 <= d.x < self.size) and (0 <= d.y < self.size))

    # выстрел по кораблю
    def shot(self, d):
        if self.out(d):
            raise BoardOutEcxeption()
        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            # 26.48 мин видео
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "x"
                if ship.lives == 0:
                    self.count += 1
                    self.contur(ship, verb=True)
                    print("Корабль уничтожен")
                    return False
                else:
                    print("Корабль ранен")
                    return True
        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []

# класс игрока общий (доска и враг)
class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    # метод выстрела
    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


# класс игрока-компьютер
class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


# класс игрока-пользователя
class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print("Введите две координаты! ")
                continue
            x, y = cords

            if not(x.isdigit()) or not(y.isdigit()):
                print("Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x-1, y-1)


# Класс игры
class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hidden = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.try_board()
        return board

    def try_board(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for length in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), length, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("*****************")
        print("  Здравствуйте!  ")
        print("    Поиграем в   ")
        print("   Морской бой   ")
        print("*****************")
        print("формат ввода: x y")
        print(" x - номер строки")
        print("y - номер столбца")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя: ")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера")
            print(self.ai.board)
            print("-" * 20)
            if num % 2 == 0:
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("Ходит компьютер!")
                repeat = self.ai.move()
            if repeat:
                num -= 1

            if self.ai.board.count == 7:
                print("-" * 20)
                print("Пользователь выиграл!")
                break
            if self.us.board.count == 7:
                print("-" * 20)
                print("Компьютер выиграл!")
                break
            num += 1
    def start(self):
        self.greet()
        self.loop()

g = Game()
g.start()
