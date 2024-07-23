import math
import random

import pygame


class Point:
    def __init__(self, screen, position, prev_position, locked=False):
        self.x, self.y = position
        self.old_x, self.old_y = prev_position
        self.locked = locked

        self.rect = None
        # draw initially to define rect:
        self.draw(screen)

    def update(self):
        if self.locked:
            return
        vx = (self.x - self.old_x) * FRICTION
        vy = (self.y - self.old_y) * FRICTION

        # update old position
        self.old_x = self.x
        self.old_y = self.y
        self.x += vx
        self.y += vy
        self.y += GRAVITY

        if self.x > WIDTH:
            self.x = WIDTH
            self.old_x = self.x + vx * BOUNCE

        elif self.x < 0:
            self.x = 0
            self.old_x = self.x + vx * BOUNCE

        if self.y > HEIGHT:
            self.y = HEIGHT
            self.old_y = self.y + vy * BOUNCE

        elif self.y < 0:
            self.y = 0
            self.old_y = self.y + vy * BOUNCE

    def draw(self, screen):
        if self.locked:
            self.rect = pygame.draw.circle(screen, LOCKED_COLOR, (self.x, self.y), CIRCLE_RADIUS)
        else:
            self.rect = pygame.draw.circle(screen, CIRCLE_COLOR, (self.x, self.y), CIRCLE_RADIUS)


class Stick:
    def __init__(self, point_a, point_b):
        self.point_a = point_a
        self.point_b = point_b
        self.length = self.calc_distance()

    def calc_distance(self):
        dx = self.point_b.x - self.point_a.x
        dy = self.point_b.y - self.point_a.y
        return math.sqrt(dx * dx + dy * dy)  # pythagorean theorem to get distance between 2 points

    def update(self):
        dx = self.point_b.x - self.point_a.x
        dy = self.point_b.y - self.point_a.y
        distance = math.sqrt(dx * dx + dy * dy)  # pythagorean theorem to get distance between 2 points
        distance = max(distance, 0.01)          # distance cant be 0.
        difference = self.length - distance
        percent = difference / distance / 2
        offset_x = dx * percent
        offset_y = dy * percent

        if self.point_a.locked and not self.point_b.locked:
            self.point_b.x += offset_x * 2
            self.point_b.y += offset_y * 2

        elif not self.point_a.locked and self.point_b.locked:
            self.point_a.x -= offset_x * 2
            self.point_a.y -= offset_y * 2

        else:
            self.point_a.x -= offset_x
            self.point_a.y -= offset_y

            self.point_b.x += offset_x
            self.point_b.y += offset_y

    def draw(self, screen):
        pygame.draw.line(screen, LINE_COLOR, (self.point_a.x, self.point_a.y), (self.point_b.x, self.point_b.y))


class Game:
    def __init__(self, screen):
        self.screen = screen
        self.points = []
        self.sticks = []
        self.run = False
        self.selected_point = None

    def select_point(self, point):
        if point is self.selected_point:
            self.selected_point = None

        elif self.selected_point is not None:
            # create a stick
            self.sticks.append(Stick(self.selected_point, point))
            self.selected_point = None

        else:
            self.selected_point = point

    def mark_point(self, point):
        pygame.draw.circle(screen, SELECT_COLOR, (point.x, point.y), CIRCLE_RADIUS)

    def delete_point(self, point):
        if point is self.selected_point:
            self.selected_point = None  # deselect point

        self.points.remove(point)
        for i in range(len(self.sticks) -1, -1, -1):
            stick = self.sticks[i]
            if point is stick.point_a or point is stick.point_b:
                self.sticks.pop(i)

    def update_points(self):
        for point in self.points:
            point.update()

    def update_sticks(self):
        for stick in self.sticks:
            stick.update()

    def draw_points(self):
        for point in self.points:
            point.draw(self.screen)

    def draw_sticks(self):
        for stick in self.sticks:
            stick.draw(self.screen)

    def update(self):
        self.screen.fill(AQUA)

        if self.run:
            random.shuffle(self.points)
            self.update_points()
            random.shuffle(self.sticks)
            self.update_sticks()

        self.draw_sticks()
        self.draw_points()

        if self.selected_point:
            self.mark_point(self.selected_point)


# CONSTANTS
WIDTH, HEIGHT = 1200, 900

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
AQUA = (0, 255, 255)
LOCKED_COLOR = (0, 100, 255)
CIRCLE_COLOR = BLACK
LINE_COLOR = BLACK
SELECT_COLOR = WHITE

LEFT_CLICK = 1
RIGHT_CLICK = 3

CIRCLE_RADIUS = 15
FPS = 60

BOUNCE = 0.8  # how much speed dot will lose after each bounce
GRAVITY = 0.2
FRICTION = 0.999

screen = pygame.display.set_mode((WIDTH, HEIGHT))


def main():
    pygame.init()
    pygame.display.set_caption('Ropes')
    clock = pygame.time.Clock()
    run = True

    can_select_point = None
    delete_points = False

    game = Game(screen)

    DRAW_ARRAY = False
    if DRAW_ARRAY:
        offset_width = 100  # array start from left
        offset_hor = 70  # array start from up
        offset = 70  # points offset between one another

        array_width = 10  # dots in Y
        array_length = 15  # dots in X

        for y in range(array_width):
            for x in range(array_length):
                game.points.append(
                    Point(screen, (offset_width + x * offset, offset_hor + y * offset), pygame.mouse.get_pos(),
                          locked=False))
                point = game.points[-1]
                if can_select_point:
                    game.select_point(point)

                game.select_point(can_select_point)
                can_select_point = point
            can_select_point = None

        for x in range(array_length):
            for y in range(array_width):
                point = game.points[y * array_length + x]
                if can_select_point:
                    game.select_point(point)

                game.select_point(can_select_point)
                can_select_point = point
            can_select_point = None

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.run = not game.run

                if event.key == pygame.K_l:
                    if can_select_point:
                        can_select_point.locked = not can_select_point.locked

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == LEFT_CLICK:
                    if can_select_point:
                        game.select_point(can_select_point)
                    else:
                        game.points.append(Point(screen, pygame.mouse.get_pos(), pygame.mouse.get_pos(), locked=False))

                elif event.button == RIGHT_CLICK:
                    delete_points = True

            if event.type == pygame.MOUSEBUTTONUP:
                delete_points = False

        mouse_pos = pygame.mouse.get_pos()
        can_select_point = False
        for point in game.points:
            if point.rect.collidepoint(mouse_pos):
                can_select_point = point
                break

        if delete_points:
            if can_select_point:
                game.delete_point(can_select_point)
                can_select_point = None

        game.update()
        pygame.display.update()
        clock.tick(FPS)
    pygame.quit()


if __name__ == '__main__':
    main()

