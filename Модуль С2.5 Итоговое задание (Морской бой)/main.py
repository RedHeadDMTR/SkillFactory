from random import randint


# Класс точка
class Dot:
    def __init__(self, x, y):  # метод конструктор для инициализации атрибутов
        self.x = x  # создаем ссылки на атрибуты
        self.y = y

    def __eq__(self, other):  # метод для сравнения координат
        return self.x == other.x and self.y == other.y

    def __repr__(self):  # метод для вывода служебной информации
        return f'Dot({self.x}, {self.y})'  # Dot(1, 2)


# Класс исключений
class BoardException(Exception):
    pass


class BoardOutException(BoardException):
    def __str__(self):
        return 'Вы пытаетесь выстрелить за пределы доски'


class BoardUsedException(BoardException):
    def __str__(self):
        return 'Вы уже стреляли в эту клетку'


class BoardWrongShipException(BoardException):
    pass


# Класс корабль
class Ship:
    def __init__(self, nose, len_, orient):  # нос, длина, ориентация (вертикальный или горизонтальный)
        self.nose = nose
        self.len_ = len_
        self.orient = orient
        self.lives = len_

    @property                 # сделали метод свойством
    def dots(self):
        ship_dots = []
        for i in range(self.len_):  # проходимся циклом по длине корабля
            cur_x = self.nose.x  # присваиваем начальную точку носа по x
            cur_y = self.nose.y  # присваиваем начальную точку носа по y

            if self.orient == 0:  # если ориентация 0, то корабль выстроится по вертикали
                cur_x += i

            elif self.orient == 1:  # если ориентация 1, то корабль выстроится по горизонтали
                cur_y += i

            ship_dots.append(Dot(cur_x, cur_y))  # в список ship_dots отправятся координаты всех точек корабля

        return ship_dots  # возвратится список координат всех точек корабля

    def shooten(self, shot):  # проверка на промах или попадание в корабль
        return shot in self.dots


# Класс Доска
class Board:
    def __init__(self, hid=False, size=6):  # hid - скрытие игрового поля, size - размер поля
        self.size = size
        self.hid = hid

        self.count = 0  # количество битых кораблей

        self.field = [['O'] * size for _ in range(size)]  # игровая сетка

        self.busy = []  # занятые точки
        self.ships = []  # список кораблей

    def add_ship(self, ship):

        for d in ship.dots:
            if self.out(d) or d in self.busy:
                raise BoardWrongShipException()
        for d in ship.dots:
            self.field[d.x][d.y] = "■"
            self.busy.append(d)

        self.ships.append(ship)
        self.contour(ship)

    def contour(self, ship, verb=False):
        near = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 0), (0, 1),            # список точек которые окружают конкретную точку
            (1, -1), (1, 0), (1, 1)
        ]
        for d in ship.dots:
            for dx, dy in near:
                cur = Dot(d.x + dx, d.y + dy)
                if not (self.out(cur)) and cur not in self.busy:
                    if verb:
                        self.field[cur.x][cur.y] = "."
                    self.busy.append(cur)

    def __str__(self):  # отрисовка игрового поля
        res = ''
        res += '  | 1 | 2 | 3 | 4 | 5 | 6 |'
        for i, row in enumerate(self.field):
            res += f"\n{i + 1} | " + " | ".join(row) + " |"

        if self.hid:  # условие отвечающие за скрытие кораблей
            res = res.replace('■', 'O')
        return res

    def out(self, d):  # метод проверяет, находится ли точка за пределами доски
        return not ((0 <= d.x < self.size) and (0 <= d.y < self.size))

    def shot(self, d):
        if self.out(d):
            raise BoardOutException()

        if d in self.busy:
            raise BoardUsedException()

        self.busy.append(d)

        for ship in self.ships:
            if d in ship.dots:
                ship.lives -= 1
                self.field[d.x][d.y] = "X"
                if ship.lives == 0:
                    self.count += 1
                    self.contour(ship, verb=True)
                    print("Корабль уничтожен!")
                    return False
                else:
                    print("Корабль ранен!")
                    return True

        self.field[d.x][d.y] = "."
        print("Мимо!")
        return False

    def begin(self):
        self.busy = []


class Player:
    def __init__(self, board, enemy):
        self.board = board
        self.enemy = enemy

    def ask(self):
        raise NotImplementedError()

    def move(self):
        while True:
            try:
                target = self.ask()
                repeat = self.enemy.shot(target)
                return repeat
            except BoardException as e:
                print(e)


class AI(Player):
    def ask(self):
        d = Dot(randint(0, 5), randint(0, 5))
        print(f"Ход компьютера: {d.x + 1} {d.y + 1}")
        return d


class User(Player):
    def ask(self):
        while True:
            cords = input("Ваш ход: ").split()

            if len(cords) != 2:
                print(" Введите 2 координаты! ")
                continue

            x, y = cords

            if not (x.isdigit()) or not (y.isdigit()):
                print(" Введите числа! ")
                continue

            x, y = int(x), int(y)

            return Dot(x - 1, y - 1)


class Game:
    def __init__(self, size=6):
        self.size = size
        pl = self.random_board()
        co = self.random_board()
        co.hid = True

        self.ai = AI(co, pl)
        self.us = User(pl, co)

    def random_board(self):
        board = None
        while board is None:
            board = self.random_place()
        return board

    def random_place(self):
        lens = [3, 2, 2, 1, 1, 1, 1]
        board = Board(size=self.size)
        attempts = 0
        for l in lens:
            while True:
                attempts += 1
                if attempts > 2000:
                    return None
                ship = Ship(Dot(randint(0, self.size), randint(0, self.size)), l, randint(0, 1))
                try:
                    board.add_ship(ship)
                    break
                except BoardWrongShipException:
                    pass
        board.begin()
        return board

    def greet(self):
        print("-------------------")
        print("  Приветсвуем вас  ")
        print("      в игре       ")
        print("    морской бой    ")
        print("-------------------")
        print(" формат ввода: x y ")
        print(" x - номер строки  ")
        print(" y - номер столбца ")

    def loop(self):
        num = 0
        while True:
            print("-" * 20)
            print("Доска пользователя:")
            print(self.us.board)
            print("-" * 20)
            print("Доска компьютера:")
            print(self.ai.board)
            if num % 2 == 0:
                print("-" * 20)
                print("Ходит пользователь!")
                repeat = self.us.move()
            else:
                print("-" * 20)
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
