import pygame
from pygame.locals import *
import sys
import numpy as np


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


class Model:
    def __init__(self):
        self.W = np.random.random((6, 3)) * 6 - 3
        self.W2 = np.random.random((1, 7)) * 6 - 3

    def out(self, x):
        Iy = np.dot(self.W, np.vstack((x, 1)))
        y = sigmoid(Iy)
        Z = np.dot(self.W2, np.vstack((y, 1)))
        return sigmoid(Z)

    def update(self, w, w2):
        self.W = w
        self.W2 = w2


class Box:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.veloX = 0
        self.veloY = 0
        self.width = width
        self.height = height
        self.isDeath = False
        self.tag = "None"

    def draw(self, pygame, screen):
        pass

    def update(self):
        self.x += self.veloX
        self.y += self.veloY

    def col(self, obj2):
        if self.x < obj2.x + obj2.width and self.x + self.width > obj2.x and self.y < obj2.y + obj2.height and self.y + self.height > obj2.y:
            return True


class Player(Box):
    G = 1.5
    score = 0

    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.model = Model()
        self.time = 0

    def draw(self, pygame, screen):
        pygame.draw.rect(screen, (255, 0, 0), (int(self.x), int(self.y), self.width, self.height), 0)

    def update(self):
        self.time += 1
        super().update()
        self.veloY += self.G
        if self.y < 0 or self.y + self.height > 400:
            self.isDeath = True

    def jump(self):
        self.veloY = -12

    def do(self):
        X = np.array([[point.x - self.x], [self.y - point.y]])
        if self.model.out(X) > 0.5:
            self.jump()

    def __lt__(self, other):
        return self.time < other.time

    def __gt__(self, other):
        return self.time > other.time


class Object(Box):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.veloX = -3
        self.tag = "OUT"

    def draw(self, pygame, screen):
        pygame.draw.rect(screen, (0, 0, 0), (int(self.x), int(self.y), self.width, self.height), 0)

    def update(self):
        super().update()
        if self.x + self.width < 0:
            self.isDeath = True


class NextPoint(Box):
    def draw(self, pygame, screen):
        pygame.draw.rect(screen, (0, 0, 0), (int(self.x), int(self.y), self.width, self.height), 0)


class Dummy(Box):
    def __init__(self, x, y, width, height):
        super().__init__(x, y, width, height)
        self.veloX = -3
        self.tag = "OK"

    # def draw(self, pygame, screen):
    #     pygame.draw.rect(screen, (0, 0, 255), (int(self.x), int(self.y), self.width, self.height), 0)


objects = []
player = []
flag = False
point = NextPoint(0, 0, 0, 0)
nextObj = NextPoint(0, 0, 0, 0)
time = 0


def main():
    global point, flag, nextObj, time
    pygame.init()  # 初期化
    screen = pygame.display.set_mode((600, 400))  # ウィンドウサイズの指定
    pygame.display.set_caption("GA_FLAPPY")  # ウィンドウの上の方に出てくるアレの指定
    clock = pygame.time.Clock()  # A clock object to limit the frame rate.
    reset()

    while True:
        for event in pygame.event.get():  # 終了処理
            # if event.type == KEYDOWN:
            #     player.veloY = -12
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        screen.fill((255, 255, 255,))  # 背景色の指定。RGBだと思う
        for p in player:
            if not p.isDeath:
                if time % 2 == 0:
                    p.do()
                p.update()
                p.draw(pygame, screen)
        if time % 80 == 0:
            rand = int(np.random.rand() * 200 + 50)
            objects.append(Object(600, 0, 50, rand))
            objects.append(Object(600, rand + 120, 50, 10000))
            objects.append(Dummy(600 + 50 + 30, rand, 5, 120))
        #
        # if point.x < player.x:
        #     flag = False
        min = 1000
        for o in objects[:]:
            o.update()
            o.draw(pygame, screen)
            for p in player:
                if 0 < o.x + o.width - p.x < min:
                    min = o.x + o.width - p.x
                    nextObj = o
                if o.col(p):
                    if o.tag == "OK":
                        p.score += 1
                        o.isDeath = True
                    else:
                        p.isDeath = True
            if o.isDeath:
                objects.remove(o)
        point = NextPoint(nextObj.x + nextObj.width, nextObj.y + nextObj.height + 60, 10, 10)
        point.draw(pygame, screen)
        pygame.display.update()  # 画面更新
        for p in player:
            if not p.isDeath:
                break
            reset(True)
        time += 1

        clock.tick(60)


def reset(flag=False):
    global objects, player, time
    objects = []
    lastPlayer = []
    if flag:
        player.sort(reverse=True)
        lastPlayer = player
    player = []
    for i in range(10):
        player.append(Player(100, 170, 30, 30))
    if flag:
        for i in range(9):
            player[i].model.update(lastPlayer[i].model.W, lastPlayer[i].model.W2)
        for i in range(4, 8, 2):
            swap = int(np.random.rand() * 4 + 1)
            temp1 = player[i].model.W[swap:len(player[i].model.W), :]
            player[i].model.W = np.vstack((np.delete(player[i].model.W, np.s_[swap:len(player[i].model.W):1], 0),
                                           player[i + 1].model.W[swap:len(player[i + 1].model.W), :]))
            player[i + 1].model.W = np.vstack(
                (np.delete(player[i + 1].model.W, np.s_[swap:len(player[i].model.W):1], 0), temp1))
            swap = int(np.random.rand() * 4 + 1)
            a = player[i].model.W2.T
            b = player[i + 1].model.W2.T
            temp1 = a[swap:len(a)]
            a = np.vstack((np.delete(a, np.s_[swap:len(a):1], 0), b[swap:len(b), :]))
            b = np.vstack((np.delete(b, np.s_[swap:len(a):1], 0), temp1))
            player[i].model.W2 = a.T
            player[i + 1].model.W2 = b.T

        lastPlayer = np.random.choice(lastPlayer, 1, replace=False)
        for i in range(9, 10):
            player[i].model.update(lastPlayer[0].model.W, lastPlayer[0].model.W2)
        for i in range(10):
            if np.random.rand() > 0.9:
                a = np.random.rand() * 5
                v = np.random.rand() * 2
                player[i].model.W[int(a), int(v)] = np.random.rand() * 6 - 3
            if np.random.rand() > 0.9:
                a = np.random.rand() * 5
                player[i].model.W2[0, int(a)] = np.random.rand() * 6 - 3

    time = -1


if __name__ == "__main__":
    main()
