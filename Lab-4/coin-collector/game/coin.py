"""
Coin: a static collectible circle with a type (bronze / silver / gold).
Drawn as a circle, hit-tested as a bounding square around it.
"""

import pygame

# type name -> (value, color, spawn weight)
COIN_TYPES = {
    "bronze": (1, (205, 127, 50), 60),
    "silver": (3, (200, 200, 210), 30),
    "gold":   (5, (255, 215, 0), 10),
}


class Coin:
    def __init__(self, x, y, coin_type="bronze", radius=12):
        value, color, _ = COIN_TYPES[coin_type]
        self.x = x
        self.y = y
        self.radius = radius
        self.coin_type = coin_type
        self.value = value
        self.color = color

    def get_rect(self):
        return pygame.Rect(
            int(self.x - self.radius), int(self.y - self.radius),
            self.radius * 2, self.radius * 2,
        )
