#!/usr/bin/env python3

# DO NOT MODIFY THE CODE BELOW
import sys, os
from typing import List, Tuple

os.environ["OMP_NUM_THREADS"] = "1"
os.environ["USE_SIMPLE_THREADED_LEVEL3"] = "1"
# DO NOT MODIFY THE CODE ABOVE

# add your own imports below
from time import time
# define your helper functions here


def index(x: int, y: int): return (x << 3) + y


def inside(x: int, y: int): return (0 <= x < 8) and (0 <= y < 8)


def coord(i: int): return divmod(i, 8)


def x_(i: int): return i >> 3  # i // 8


def y_(i: int): return i & 7  # i % 8


X, Y = 0, 1
INF = 1000000
start_time: float
# 8 disk-eating directions
DIRCTIONS_COORD = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
DIRCTIONS_INDEX = (-9, -8, -7, -1, 1, 7, 8, 9)
# ref: https://botzone.org.cn/game/ranklist/53e1db360003e29c2ba227b8?page=0
WEIGHT = (
    20, -3, 11,  8,  8, 11, -3, 20,
    -3, -7,  1,  1,  1,  1, -7, -3,
    11,  1,  2,  2,  2,  2,  1, 11,
     8,  1,  2, -3, -3,  2,  1,  8,
     8,  1,  2, -3, -3,  2,  1,  8,
    11,  1,  2,  2,  2,  2,  1, 11,
    -3, -7,  1,  1,  1,  1, -7, -3,
    20, -3, 11,  8,  8, 11, -3, 20
)
# 4 corners where stable disks origin
CORNERS = (((0, 0), (1, 1)), ((7, 0), (-1, 1)), ((0, 7), (1, -1)), ((7, 7), (-1, -1)))


class Reversi:
    _id: int  # 0: Black; 1: White
    _board: list
    _feasible: int  # for a certain place

    def __init__(self, player, board: List[int]):
        'player: 0 or 1, empty board: 2, len(allow) = 64'
        self._id = player
        self._board = board.copy()  # copy or not, that's the question

    def value(self) -> int:
        'give a weighted value for player AFTER play'
        value = 0
        if (space_num := self._board.count(2)) == 0:
            for disk in self._board:
                value += -1 if disk == self._id else 1
            return value
        # basic value: add all disks' weights
        for disk, weight in zip(self._board, WEIGHT):
            if disk == 1 - self._id:
                value += weight
            elif disk == self._id:
                value -= weight
        # begin part
        if space_num > 40:
            return value
        # search stable disks, from corner(i.e. triangle)
        stables = [False] * 64
        for corner, direction in CORNERS:
            x, y = corner
            if (corner_id := self._board[index(x, y)]) == 2:
                continue
            dx = 0  # i.e. delta x
            dy_max = 8
            while (dx < 8) and self._board[index(x, y)] == corner_id:
                dy = 0
                while (dy < dy_max) and self._board[index(x, y)] == corner_id:
                    dy += 1
                    if not stables[index(x, y)]:  # stable disk
                        stables[index(x, y)] = True
                        value += -30 if corner_id == self._id else 30
                    y += direction[Y]
                dx += 1
                dy_max = min(dy, dy_max)
                x += direction[X]
                y = corner[Y]
        return value

    def play(self, choice: int):
        'calculate the new board after one step'
        oppo = Reversi(1 - self._id, self._board)
        oppo._board[choice] = self._id
        # 8 available
        for i, direction in enumerate(DIRCTIONS_INDEX):
            if self._feasible & (1 << i) == 0:
                continue
            # filp
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
        for i, (direction_x, direction_y) in enumerate(DIRCTIONS_COORD):
            x = x_(choice) + direction_x
            y = y_(choice) + direction_y
            if not (inside(x, y) and self._board[index(x, y)] == 1 - self._id):
                continue
            while True:
                x += direction_x
                y += direction_y
                if inside(x, y):
                    if (disk := self._board[index(x, y)]) == 1 - self._id:
                        continue
                    elif disk == self._id:
                        self._feasible |= (1 << i)
                break
        return (self._feasible > 0)

    def alpha_beta(self, depth: int, alpha: int, beta: int, AI_turn: bool):
        global start_time
        if time() - start_time > 2.9:
            return INF if AI_turn else -INF
        if depth == 0 or self._board.count(2) == 0:
            return self.value()
        if AI_turn:
            value = -INF
            for strat in range(64):
                if not self.feasible(strat):
                    continue
                child = self.play(strat)
                value = max(value, child.alpha_beta(depth - 1, alpha, beta, False))
                if value >= beta:
                    break  # purning
                alpha = max(alpha, value)
        else:
            value = INF
            for strat in range(64):
                if not self.feasible(strat):
                    continue
                child = self.play(strat)
                value = min(value, child.alpha_beta(depth - 1, alpha, beta, True))
                if value <= alpha:
                    break
                beta = min(beta, value)
        return value


def reversi_ai(player: int, board: List[int], allow: List[bool]) -> Tuple[int, int]:
    'player: 0 or 1, empty board: 2, len(allow) = 64'
    # set timer
    global start_time
    start_time = time()
    # create Reversi
    now = Reversi(player, board)
    print(space_num := now._board.count(2), file=sys.stderr, flush=True)
    # find strategies
    ai_strats = [i for i, feasible in enumerate(allow) if feasible]
    best_4_strat = best_6_strat = ai_strats[0]
    # shallow recursion, can definitely be done
    shallow = 4 if space_num > 12 else 8
    max_value = -INF
    for i, strat in enumerate(ai_strats):
        now.feasible(strat)
        node = now.play(strat)
        value = node.alpha_beta(shallow, -INF, INF, False)
        if value > max_value:
            max_value = value
            best_4_strat = strat
        # print time used: < 3s
        time_consume = time() - start_time
        print(f'{i}/{len(ai_strats)}: ({shallow}) {time_consume}',
              file=sys.stderr, flush=True)
    print(coord(best_4_strat), file=sys.stderr, flush=True)
    # deep recursion
    deep = shallow + 2
    max_value = -INF
    for i, strat in enumerate(ai_strats):
        now.feasible(strat)
        node = now.play(strat)
        value = node.alpha_beta(deep, -INF, INF, False)
        if value > max_value:
            max_value = value
            best_6_strat = strat
        # TLE
        time_consume = time() - start_time
        print(f'{i}/{len(ai_strats)}: ({deep}) {time_consume}',
              file=sys.stderr, flush=True)
        if time_consume > 2.9:
            break
    else:
        print(coord(best_6_strat), file=sys.stderr, flush=True)
        return coord(best_6_strat)
    return coord(best_4_strat)

# DO NOT MODIFY ANY CODE BELOW
# **不要修改**以下的代码


def ask_next_pos(board, player):
    '''
    返回player在当前board下的可落子点
    '''
    ask_message = ['#', str(player)]
    for i in board:
        ask_message.append(str(i))
    ask_message.append('#')
    sys.stdout.buffer.write(ai_convert_byte("".join(ask_message)))
    sys.stdout.flush()
    data = sys.stdin.buffer.read(64)
    str_list = list(data.decode())
    return [int(i) == 1 for i in str_list]


def ai_convert_byte(data_str):
    '''
    传输数据的时候加数据长度作为数据头
    '''
    message_len = len(data_str)
    message = message_len.to_bytes(4, byteorder='big', signed=True)
    message += bytes(data_str, encoding="utf8")
    return message


def send_opt(data_str):
    '''
    发送自己的操作
    '''
    sys.stdout.buffer.write(ai_convert_byte(data_str))
    sys.stdout.flush()


def start():
    '''
    循环入口
    '''
    read_buffer = sys.stdin.buffer
    while True:
        data = read_buffer.read(67)
        now_player = int(data.decode()[1])
        str_list = list(data.decode()[2:-1])
        board_list = [int(i) for i in str_list]
        next_list = ask_next_pos(board_list, now_player)
        x, y = reversi_ai(now_player, board_list, next_list)
        send_opt(str(x)+str(y))


if __name__ == '__main__':
    start()
