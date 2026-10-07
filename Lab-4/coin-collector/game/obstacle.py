"""
Obstacle: a red square that bounces around the play area.
It is clamped to the play area, so it can never leave the screen.
"""

import pygame


class Obstacle:
    def __init__(self, x, y, vx, vy, size=34):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.size = size
        self.color = (220, 60, 60)

    def update(self, bounds_width, bounds_height):
        half = self.size / 2
        self.x += self.vx
        self.y += self.vy
        if self.x < half:
            self.x = half
            self.vx = abs(self.vx)
        elif self.x > bounds_width - half:
            self.x = bounds_width - half
            self.vx = -abs(self.vx)
        if self.y < half:
            self.y = half
            self.vy = abs(self.vy)
        elif self.y > bounds_height - half:
            self.y = bounds_height - half
            self.vy = -abs(self.vy)

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.size / 2), int(self.y - self.size / 2),
            self.size, self.size,
        )
