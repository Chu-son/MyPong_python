#! /usr/bin/env python
# -*- coding:utf-8 -*-

import cv2
import numpy as np
import copy
import random
import time
import math


class Ball():
    BALL_DIRECTION_LEFT = 1
    BALL_DIRECTION_RIGHT = 2
    BALL_DIRECTION_TOP = 4
    BALL_DIRECTION_BOTTOM = 8
    def __init__(self, pos, field):
        self.start_pos = np.array(pos)
        self.pos = np.array(pos) # [x, y]
        self.d_sign = [1,1]

        self._speed_range = [5,15]
        self._speed = self._speed_range[0]
        self._angle_range = [0,60]
        self._angle = self._angle_range[0]
        self._calc_d_mv()

        self._field = field

        self.pre_pos = self.pos
        self.restarted = True

    def _calc_d_mv(self):
#        d_x = self._speed * self.d_sign[0]
#        d_y = abs(self._speed) * math.tan(math.radians(self._angle)) * self.d_sign[1]
        d_x = abs(self._speed) * math.cos(math.radians(self._angle)) * self.d_sign[0]
        d_y = abs(self._speed) * math.sin(math.radians(self._angle)) * self.d_sign[1]

        self.d_mv = np.array([int(d_x), int(d_y)])

    def draw_ball(self, field):
        cv2.circle(field, tuple(self.pos.tolist()), 10, (0,0,255), -1)

    def move(self):
        self.restarted = False
        self._calc_d_mv()

        self.pre_pos = copy.deepcopy(self.pos)
        self.pos += self.d_mv

        if self._field.is_hit_horizontal(self.pos):
            #self.flip(Pong.PONG_HORIZONTAL)
            return self._field.hit_side(self.pos)
        if self._field.is_hit_vertical(self.pos):
            self.flip(Pong.PONG_VERTICAL)

        return self._field.FIELD_NOT_HIT

    def flip(self, direction):
        if direction == Pong.PONG_HORIZONTAL:
            self.d_sign[0] *= -1
        elif direction == Pong.PONG_VERTICAL:
            self.d_sign[1] *= -1

    def move_direction(self):
        h = Ball.BALL_DIRECTION_LEFT if self.d_sign[0] < 0 else Ball.BALL_DIRECTION_RIGHT
        v = Ball.BALL_DIRECTION_TOP if self.d_sign[1] < 0 else Ball.BALL_DIRECTION_BOTTOM
        return [h, v]

    def restart(self):
        self.pos = copy.deepcopy(self.start_pos)
        self.pre_pos = copy.deepcopy(self.start_pos)
        self._speed = self._speed_range[0]
        self._angle = random.uniform(0,45)
        self.flip(Pong.PONG_HORIZONTAL)
        self.restarted = True

class Bar():
    def __init__(self, pos, field):
        self.pos = pos
        self.length = 150
        self.thickness = 10
        self.color = (255, 255, 255)

        self._field = field

        self._hit = False

    def get_pos(self):
        # (top, bottom)
        return ((self.pos[0], self.pos[1]-self.length//2),
                (self.pos[0], self.pos[1]+self.length//2))

    def set_pos_top(self, pos):
        self.pos[1] = pos + self.length//2
    def set_pos_bottom(self, pos):
        self.pos[1] = pos - self.length//2

    def draw_bar(self, field):
        cv2.line(field,
                self.get_pos()[0],
                self.get_pos()[1],
                self.color, self.thickness)

    def is_hit(self, ball):
        # ここは変える
#        if self.pos[0] - self.thickness//2 <= ball_pos[0] <= self.pos[0] + self.thickness//2 \
#                and self.pos[1] - self.length//2 <= ball_pos[1] <= self.pos[1] + self.length//2:
#                    return True
#        else:
#            return False

        ax, ay = ball.pos
        bx, by = ball.pre_pos
        cx, cy = self.get_pos()[0]
        dx, dy = self.get_pos()[1]
        
        ta = (cx - dx) * (ay - cy) + (cy - dy) * (cx - ax)
        tb = (cx - dx) * (by - cy) + (cy - dy) * (cx - bx)
        tc = (ax - bx) * (cy - ay) + (ay - by) * (ax - cx)
        td = (ax - bx) * (dy - ay) + (ay - by) * (ax - dx)

        ta /= ta if ta > 0 else -ta if ta < 0 else 1
        tc /= tc if tc > 0 else -tc if tc < 0 else 1

        is_hit = not self._hit and tc * td <= 0 and ta * tb <= 0
        self._hit = is_hit

        if is_hit and True:
            dev = (by - ay) * (dx - cx) - (bx - ax) * (dy - cy)
            d1 = cy * dx - cx * dy
            d2 = ay * bx - ax * by

            x = ( d1 * (bx - ax) - d2 * (dx - cx) ) / dev
            y = ( d1 * (by - ay) - d2 * (dy - cy) ) / dev

            ball.pos[0] = int(x)
            ball.pos[1] = int(y)

            x -= self.pos[0]
            y -= self.pos[1]

            self._hit_pos = [x, y]

        return is_hit

    def get_hit_pos(self):
        if not self._hit:
            return None
        return self._hit_pos[0]/(self.length/2), -self._hit_pos[1]/(self.length/2)

    def move(self, delta):
        self.pos[1] += delta

        if self._field.is_hit_vertical(self.get_pos()[0]):
            self.set_pos_top(0)
        elif self._field.is_hit_vertical(self.get_pos()[1]):
            self.set_pos_bottom(self._field.size[1])

class Field():
    FIELD_NOT_HIT = 0
    FIELD_HIT_TOP = 1
    FIELD_HIT_BOTTOM = 2
    FIELD_HIT_RIGHT = 4
    FIELD_HIT_LEFT = 8

    def __init__(self, size):
        self.size = size
        self.field_base = np.zeros((size[1], size[0], 3), np.uint8)
        self.refresh()

    def refresh(self):
        self.field = copy.deepcopy(self.field_base)

    def get_field(self):
        return self.field

    def is_hit_vertical(self, pos):
        return not 0 < pos[1] < self.size[1]

    def is_hit_horizontal(self, pos):
        return not 0 < pos[0] < self.size[0]

    def hit_side(self, pos, direction = None):
        if direction is not None and direction == Pong.PONG_VERTICAL:
            if not self.is_hit_vertical(pos):
                return Field.FIELD_NOT_HIT
            elif pos[1] <= 0:
                return Field.FIELD_HIT_TOP
            else:
                return Field.FIELD_HIT_BOTTOM
        else:
            if not self.is_hit_horizontal(pos):
                return Field.FIELD_NOT_HIT
            elif pos[0] <= 0:
                return Field.FIELD_HIT_LEFT
            else:
                return Field.FIELD_HIT_RIGHT

class Drawer():
    def __init__(self, size):
        pass

class Agent():
    AGENT_MOVE_STOP = 0
    AGENT_MOVE_TOP = 1
    AGENT_MOVE_BOTTOM = 2

    AGENT_LEFT = 1
    AGENT_RIGHT = 2

    def __init__(self, bar):
        self._bar = bar
        self._d_mv = 5

        self._movement = 0

    def _set_move_direction(self, direction):
        if direction == Agent.AGENT_MOVE_TOP:
            self._movement = -self._d_mv
        elif direction == Agent.AGENT_MOVE_BOTTOM:
            self._movement = self._d_mv
        else:
            self._movement = 0

    def _move(self):
        self._bar.move(self._movement)

class RandomAgent(Agent):
    def __init__(self, bar):
        super().__init__(bar)

    def action(self):
        if random.random() - 0.5 < 0:
            self._set_move_direction(Agent.AGENT_MOVE_TOP)
        else:
            self._set_move_direction(Agent.AGENT_MOVE_BOTTOM)

        self._move()

class TrackingAgent(Agent):
    def __init__(self, bar):
        super().__init__(bar)

    def action(self, ball):
        if ball.pos[1] - self._bar.pos[1] > 0:
            self._set_move_direction(Agent.AGENT_MOVE_BOTTOM)
        else :
            self._set_move_direction(Agent.AGENT_MOVE_TOP)

        self._move()

class TrackingAgent2(Agent):
    def __init__(self, bar):
        super().__init__(bar)

    def action(self, ball):
        top = ball.pos[1] - self._bar.get_pos()[0][1] -10
        bottom = ball.pos[1] - self._bar.get_pos()[1][1] +10

        near_side = top if abs(top)<abs(bottom) else bottom

        if near_side > 0:
            self._set_move_direction(Agent.AGENT_MOVE_BOTTOM)
        else :
            self._set_move_direction(Agent.AGENT_MOVE_TOP)

        self._move()

class TrackingAgent3(Agent):
    def __init__(self, bar):
        super().__init__(bar)

    def action(self, ball):
        dist = ball.pos[0] - self._bar.pos[0]
        dist_pre = ball.pre_pos[0] - self._bar.pos[0]

        if abs(dist) < abs(dist_pre) :
            target_point = self._estimate_point(ball)
        else:
            target_point = [self._bar._field.size[0], self._bar._field.size[1]//2]

        if target_point[1] - self._bar.pos[1] > 0:
            self._set_move_direction(Agent.AGENT_MOVE_BOTTOM)
        else :
            self._set_move_direction(Agent.AGENT_MOVE_TOP)

        self._move()

    def _calc_intersection_point(self, line1, line2):
        a, b = line1
        c, d = line2

        dev = (b[1] - a[1]) * (d[0] - c[0]) - (b[0] - a[0]) * (d[1] - c[1])
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

    def action(self, ball):
        dist = ball.pos[0] - self._bar.pos[0]
        dist_pre = ball.pre_pos[0] - self._bar.pos[0]

        if abs(dist) < abs(dist_pre) :
            target_point = self._estimate_point(ball)
        else:
            target_point = [self._bar._field.size[0], self._bar._field.size[1]//2]

        top = target_point[1] - self._bar.get_pos()[0][1] -15
        bottom = target_point[1] - self._bar.get_pos()[1][1] +15

        near_side = top if abs(top)<abs(bottom) else bottom

        if near_side > 0:
            self._set_move_direction(Agent.AGENT_MOVE_BOTTOM)
        else :
            self._set_move_direction(Agent.AGENT_MOVE_TOP)


        self._move()

class Player(Agent):
    def __init__(self, bar):
        super().__init__(bar)
        self.movement = 0

    def action(self, key = None):
        if key is not None:
            if key == 2490368:
                self._set_move_direction(Agent.AGENT_MOVE_TOP)
            elif key == 2621440:
                self._set_move_direction(Agent.AGENT_MOVE_BOTTOM)
            elif key == 2555904 or key == 2424832 or key == 32:
                self._set_move_direction(Agent.AGENT_MOVE_STOP)

        self._move()

class Pong():
    PONG_HORIZONTAL = 1
    PONG_VERTICAL = 2

    def __init__(self, field_size):
        self.field_size = field_size # [x, y]
        self.point = [0, 0] # [left, right]

        self.bar_offset = 100

    def _get_center_pos(self):
        return [self.field_size[0]//2, self.field_size[1]//2]

    def _set_ball_param(self, ball, bar):
        hit_bar_pos = bar.get_hit_pos()
        val = abs(hit_bar_pos[1])

        ball._speed = min(max(ball._speed * val * 1.7, ball._speed * 1.2, ball._speed_range[0]), 50)
        ball._angle = max(ball._angle_range[1] * val, ball._angle_range[0])

        ball.d_sign[1] = int(-hit_bar_pos[1]/val) if val != 0 else ball.d_sign[1]
        ball.flip( Pong.PONG_HORIZONTAL )

    def draw_point(self, field):
        #font = cv2.FONT_HERSHEY_PLAIN
        font = cv2.FONT_HERSHEY_COMPLEX
        fontscale = 4
        thickness = 4
        text = str(self.point[0]) + '  ' + str(self.point[1])
        color = (255,255,255)

        ret,tsize = cv2.getTextSize(text, font, fontscale, thickness)
        cv2.putText(field, text, (self.field_size[0]//2 - ret[0]//2, ret[1] + 20), font, fontscale, color, thickness)

    def pong_start(self):
        field = Field(self.field_size)

        ball = Ball(self._get_center_pos(), field)

        bar_left = Bar([self.bar_offset, self.field_size[1]//2], field)
        bar_right = Bar([self.field_size[0] - self.bar_offset, self.field_size[1]//2], field)

        #cpu = RandomAgent(bar_left)
        cpu = TrackingAgent3(bar_left)
        #player = Player(bar_right)
        player = TrackingAgent4(bar_right)

        while True:
            key = cv2.waitKey(1)
            field.refresh()

            #if not ball.restarted or key >= 0:
            hit_side = ball.move()
            if hit_side:
                if hit_side == Field.FIELD_HIT_RIGHT:
                    self.point[0] += 1
                else:
                    self.point[1] += 1

                ball.restart()
                #print(self.point)
            
            #cpu.action()
            cpu.action(ball)
            #player.action(key)
            player.action(ball)

            if bar_left.is_hit(ball):
                #ball.flip( Pong.PONG_HORIZONTAL )
                self._set_ball_param(ball, bar_left)
            if bar_right.is_hit(ball):
                self._set_ball_param(ball, bar_right)

            bar_left.draw_bar(field.get_field())
            bar_right.draw_bar(field.get_field()) 
            ball.draw_ball(field.get_field())

            self.draw_point(field.get_field())

            cv2.imshow("field",field.get_field())

            if key == 27:
                break
            elif key == 112:
                cv2.waitKey(0)


if __name__ == "__main__":
    field_size = [1000, 500]
    pong = Pong(field_size)
    pong.pong_start()

