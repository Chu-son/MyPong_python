#! /usr/bin/env python
# -*- coding:utf-8 -*-
import copy
import numpy as np

class Agent():
    AGENT_MOVE_STOP = 0
    AGENT_MOVE_TOP = 1
    AGENT_MOVE_BOTTOM = 2

    AGENT_LEFT = 1
    AGENT_RIGHT = 2

    def __init__(self, bar):
        self._bar = bar
        self._d_mv = 10

        self._movement = 0

    def _set_move_direction(self, direction):
        if direction == Agent.AGENT_MOVE_TOP:
            self._movement = -self._d_mv
        elif direction == Agent.AGENT_MOVE_BOTTOM:
            self._movement = self._d_mv
        else:
            self._movement = 0

    def _action(self, data):
        raise NotImplementedError

    def move(self, data):
        self._action(data)

        self._bar.set_d_mv(self._movement)
        self._bar.move()

class RandomAgent(Agent):
    def __init__(self, bar):
        super().__init__(bar)

    def _action(self, data):
        if random.random() - 0.5 < 0:
            self._set_move_direction(Agent.AGENT_MOVE_TOP)
        else:
            self._set_move_direction(Agent.AGENT_MOVE_BOTTOM)

class TrackingAgent(Agent):
    def __init__(self, bar):
        super().__init__(bar)

    def _action(self, ball):
        if ball.pos[1] - self._bar.pos[1] > 0:
            self._set_move_direction(Agent.AGENT_MOVE_BOTTOM)
        else :
            self._set_move_direction(Agent.AGENT_MOVE_TOP)


class TrackingAgent2(Agent):
    def __init__(self, bar):
        super().__init__(bar)

    def _action(self, ball):
        top = ball.pos[1] - self._bar.get_pos()[0][1] -10
        bottom = ball.pos[1] - self._bar.get_pos()[1][1] +10

        near_side = top if abs(top)<abs(bottom) else bottom

        if near_side > 0:
            self._set_move_direction(Agent.AGENT_MOVE_BOTTOM)
        else :
            self._set_move_direction(Agent.AGENT_MOVE_TOP)

class TrackingAgent3(Agent):
    def __init__(self, bar):
        super().__init__(bar)

    def _action(self, ball):
        target_point = self._get_target_point(ball)

        if target_point[1] - self._bar.pos[1] > 0:
            self._set_move_direction(Agent.AGENT_MOVE_BOTTOM)
        else :
            self._set_move_direction(Agent.AGENT_MOVE_TOP)

    def _get_target_point(self, ball):
        dist = ball.pos[0] - self._bar.pos[0]
        dist_pre = ball.pre_pos[0] - self._bar.pos[0]

        if abs(dist) < abs(dist_pre) :
            target_point = self._estimate_point(ball)
        else:
            target_point = [self._bar.pos[0], self._bar._field.size[1]//2]

        return target_point

    def _calc_intersection_point(self, line1, line2):
        a, b = line1
        c, d = line2

        dev = (b[1] - a[1]) * (d[0] - c[0]) - (b[0] - a[0]) * (d[1] - c[1])
        if dev == 0:
            return list(map(lambda x:x/2,self._bar._field.size))
        d1 = c[1] * d[0] - c[0] * d[1]
        d2 = a[1] * b[0] - a[0] * b[1]

        x = ( d1 * (b[0] - a[0]) - d2 * (d[0] - c[0]) ) / dev
        y = ( d1 * (b[1] - a[1]) - d2 * (d[1] - c[1]) ) / dev

        return [x, y]

    def _estimate_point(self, ball):
        intersection = self._calc_intersection_point([ball.pos, ball.pre_pos], self._bar.get_pos())
        y = intersection[1] % self._bar._field.size[1]
        count = intersection[1] // self._bar._field.size[1]
        y = -y if count%2 != 0 else y
        y = self._bar._field.size[1] + y if y < 0 else y
        return [intersection[0], y]

class TrackingAgent4(TrackingAgent3):
    def __init__(self, bar):
        super().__init__(bar)

    def _action(self, ball):
        target_point= self._get_target_point(ball)

        top = target_point[1] - self._bar.get_pos()[0][1] -15
        bottom = target_point[1] - self._bar.get_pos()[1][1] +15

        near_side = top if abs(top)<abs(bottom) else bottom

        if near_side > 0:
            self._set_move_direction(Agent.AGENT_MOVE_BOTTOM)
        else :
            self._set_move_direction(Agent.AGENT_MOVE_TOP)

class Player(Agent):
    def __init__(self, bar):
        super().__init__(bar)
        self.movement = 0

    def _action(self, key):
        if key == 2490368:
            self._set_move_direction(Agent.AGENT_MOVE_TOP)
        elif key == 2621440:
            self._set_move_direction(Agent.AGENT_MOVE_BOTTOM)
        elif key == 2555904 or key == 2424832 or key == 32:
            self._set_move_direction(Agent.AGENT_MOVE_STOP)

