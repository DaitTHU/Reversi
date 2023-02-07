#!/usr/bin/env python3
from time import time

INF = 1000000
TIME_LIMIT = 2.9
start_time: float
# 8 disk-eating directions
DCOORD = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
DINDEX = (-9, -8, -7, -1, 1, 7, 8, 9)
# ref: https://botzone.org.cn/game/ranklist/53e1db360003e29c2ba227b8?page=0
WEIGHT = (
    20, -3, 11,  8,  8, 11, -3, 20,
    -3, -7, -4,  1,  1, -4, -7, -3,
    11, -4,  2,  2,  2,  2, -4, 11,
     8,  1,  2, -3, -3,  2,  1,  8,
     8,  1,  2, -3, -3,  2,  1,  8,
    11, -4,  2,  2,  2,  2, -4, 11,
    -3, -7, -4,  1,  1, -4, -7, -3,
    20, -3, 11,  8,  8, 11, -3, 20
)
# 4 corners (index, spread_direction), where stable disks origin
CORNERS = ((0, (8, 1)), (7, (8, -1)), (56, (-8, 1)), (63, (-8, -1)))


class Reversi:
    _id: int  # 0(black) or 1(white)
    _board: list  # len = 8 * 8 = 64, 2 means empty
    _space: int  # number of space(2)
    _feasible: int  # for a certain grid

    @staticmethod
    def coord(i: int): return divmod(i, 8)
    @staticmethod
    def index(x: int, y: int): return x * 8 + y
    @staticmethod
    def inside(x: int, y: int): return 0 <= x < 8 and 0 <= y < 8

    def __init__(self, player: int, board: list, space: int):
        'player: 0(black) or 1(white),\nborad: 64-len list consisting of 0, 1, 2(empty)'
        self._id = player
        self._board = board.copy()  # copy or not, that's the question
        self._space = space

    def grid(self, x: int, y: int) -> int: return self._board[x * 8 + y]

    def value(self) -> int:
        'give a weighted value for player AFTER play'
        value = 0
        # ending: count disk num: self - oppo
        if self._space == 0:
            return 2 * sum(disk ^ self._id for disk in self._board) - 64
        # basic value: add all disks' weights
        for disk, weight in zip(self._board, WEIGHT):
            if disk == 1 - self._id:
                value += weight
            elif disk == self._id:
                value -= weight
        # opening: not necessary to count stable disks
        if self._space > 40:
            return value
        # search stable disks, from corner(i.e. triangle)
        stable = [False] * 64
        for corner, (dx, dy) in CORNERS:
            if (corner_id := self._board[corner]) == 2:
                continue
            y_max = 7
            for x in range(7):
                if self._board[corner] != corner_id:
                    break
                near = corner
                for y in range(y_max):
                    if not stable[near]:
                        stable[near] = True
                        value += -100 if corner_id == self._id else 100
                    near += dy
                    if self._board[near] != corner_id:
                        break
                corner += dx
                y_max = min(y + 1, y_max)
        return value

    def play(self, choice: int):
        'generate the new board after one step'
        oppo = Reversi(1 - self._id, self._board, self._space - 1)
        oppo._board[choice] = self._id
        # 8 directions
        for i, direction in enumerate(DINDEX):
            if self._feasible & (1 << i):  # filp
                near = choice + direction
                while self._board[near] == oppo._id:
                    oppo._board[near] = self._id
                    near += direction
        return oppo

    def feasible(self, choice: int) -> bool:
        self._feasible = 0
        if self._board[choice] != 2:
            return False
        # 8 directions
        for i, (dx, dy) in enumerate(DCOORD):
            x = choice // 8 + dx
            y = choice % 8 + dy
            if not (Reversi.inside(x, y) and self.grid(x, y) == 1 - self._id):
                continue
            while True:
                x += dx
                y += dy
                if Reversi.inside(x, y):
                    if self.grid(x, y) == 1 - self._id:
                        continue
                    elif self.grid(x, y) == self._id:
                        self._feasible |= (1 << i)
                break
        return (self._feasible > 0)

    def alpha_beta(self, depth: int, alpha: int = -INF, beta: int = INF, AI_turn: bool = False):
        '''
        depth: depth of the alpha-beta purning,\n
        alpha: worst maximum score,\n
        beta: worst minimum score,\n
        AI_turn: whether it's AI's turn,\n
        \tAI evaluates oppo's choice after each choices
        '''
        if time() - start_time > TIME_LIMIT:
            return INF if AI_turn else -INF
        if depth == 0 or self._space == 0:
            return self.value()
        if AI_turn:
            value = -INF
            for strategy in range(64):
                if not self.feasible(strategy):
                    continue
                child = self.play(strategy)
                value = max(value, child.alpha_beta(depth - 1, alpha, beta, False))
                if value >= beta:
                    break  # purning
                alpha = max(alpha, value)
        else:
            value = INF
            for strategy in range(64):
                if not self.feasible(strategy):
                    continue
                child = self.play(strategy)
                value = min(value, child.alpha_beta(depth - 1, alpha, beta, True))
                if value <= alpha:
                    break
                beta = min(beta, value)
        return value


def reversi_ai(player: int, board: list[int], allow: list[bool]) -> int:
    '''
    player: 0(black) or 1(white),\n
    borad: 64-len list consisting of 0, 1, 2(empty),\n
    allow: 64-len bool list, whether the grid is feasible
    '''
    # set timer
    global start_time
    start_time = time()
    # create Reversi
    now = Reversi(player, board, board.count(2))
    #print(now._space, '\nshallow recursion')
    # find strategies
    AI_strategies = [i for i, feasible in enumerate(allow) if feasible]
    shallow_strategy = deep_strategy = AI_strategies[0]
    # shallow recursion, definitely can be done
    depth = 4 if now._space > 14 else 8
    max_value = -INF
    for i, strategy in enumerate(AI_strategies):
        now.feasible(strategy)
        node = now.play(strategy)
        value = node.alpha_beta(depth)
        if value > max_value:
            max_value = value
            shallow_strategy = strategy
        # print time used: < 3s
        #print(f'{i}/{len(AI_strategies)}: {time() - start_time:.3f} s')
    #print(Reversi.coord(shallow_strategy), '\ndeep recursion')
    # deep recursion
    depth += 2
    max_value = -INF
    for i, strategy in enumerate(AI_strategies):
        now.feasible(strategy)
        node = now.play(strategy)
        value = node.alpha_beta(depth)
        if value > max_value:
            max_value = value
            deep_strategy = strategy
        # TLE
        time_consume = time() - start_time
        #print(f'{i}/{len(AI_strategies)}: {time_consume:.3f} s')
        if time_consume > TIME_LIMIT:
            print('break.')
            break
    else:
        #print(Reversi.coord(deep_strategy))
        return deep_strategy
    return shallow_strategy


if __name__ == '__main__':
    pass
