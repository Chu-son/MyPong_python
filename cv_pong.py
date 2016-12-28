#! /usr/bin/env python
# -*- coding:utf-8 -*-

import cv2
import numpy as np
import copy

class Ball(object):
    def __init__(self, coord):
        self.coord = coord
        self.mv_speed = [1.0, 1.0]

    def move(self):
        self.coord[0] += self.mv_speed[0]
        self.coord[1] += self.mv_speed[1]

class Bar():
    def __init__(self, pos):
        self.pos = pos
        self.length = 150
        self.thickness = 10
        self.color = (255, 255, 255)

    def draw_bar(self, field):
        cv2.line(field,
                (self.pos[0], self.pos[1]-self.length//2),
                (self.pos[0], self.pos[1]+self.length//2),
                self.color, self.thickness)

    def is_hit(self, ball_pos):
        # ここは変える
        if self.pos[0] - self.thickness//2 <= ball_pos[0] <= self.pos[0] + self.thickness//2 \
                and self.pos[1] - self.length//2 <= ball_pos[1] <= self.pos[1] + self.length//2:
                    return True
        else:
            return False

class Field(object):
    def __init__(self, size):
        self.size = size

def pong_start():
    y = 500
    x = 700
    field_base = np.zeros((y, x, 3), np.uint8)

    ball_pos = np.array(field_base.shape[:2][::-1])//2
    d_mv = np.array([5,5])

    bar_offset = 100
    bar1 = Bar([bar_offset, y//2])
    bar2 = Bar([x - bar_offset, y//2])

    while True:
        field = copy.deepcopy(field_base)
#       field = np.zeros((rows, cols, 3), np.uint8)

        ball_pos += d_mv
        print(ball_pos)

        if not 0 <= ball_pos[0] < x:
            d_mv[0] *= -1
        if not 0 <= ball_pos[1] < y:
            d_mv[1] *= -1

        if bar1.is_hit(ball_pos) or bar2.is_hit(ball_pos):
            d_mv[0] *= -1

        bar1.draw_bar(field)
        bar2.draw_bar(field)
        
        cv2.circle(field, tuple(ball_pos.tolist()), 10, (0,0,255), -1)

        cv2.imshow("field",field)

        if cv2.waitKey(1) > 0:
            break


if __name__ == "__main__":
    pong_start()

