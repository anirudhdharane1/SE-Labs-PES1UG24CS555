"""
GameEngine: owns the player, coins and obstacles, plus lives and the timer.
"""

import math
import random
import pygame

from game.player import Player
from game.coin import Coin, COIN_TYPES
from game.obstacle import Obstacle
from game.collection import check_collection, check_obstacle_hit
from game.renderer import WIDTH, HEIGHT

NUM_COINS = 6
NUM_OBSTACLES = 3
STARTING_LIVES = 3
ROUND_SECONDS = 30
INVULNERABLE_MS = 1500   # grace period after an obstacle hit


class GameEngine:
    def __init__(self):
        self.reset()

    # ---------- setup / reset ----------
    def reset(self):
        self.player = Player(x=WIDTH / 2, y=HEIGHT / 2)
        self.score = 0
        self.lives = STARTING_LIVES
        self.game_over = False
        self.round_start = pygame.time.get_ticks()
        self.invulnerable_until = 0
        self.obstacles = [self._random_obstacle() for _ in range(NUM_OBSTACLES)]
        self.coins = [self._random_coin() for _ in range(NUM_COINS)]

    def _random_coin(self):
        names = list(COIN_TYPES)
        weights = [COIN_TYPES[n][2] for n in names]
        coin_type = random.choices(names, weights=weights)[0]
        x = random.randint(30, WIDTH - 30)
        y = random.randint(30, HEIGHT - 30)
        return Coin(x=x, y=y, coin_type=coin_type, radius=12)

    def _random_obstacle(self):
        # Spawn away from the player's start position so the round
        # doesn't open with an instant hit.
        while True:
            x = random.randint(40, WIDTH - 40)
            y = random.randint(40, HEIGHT - 40)
            if math.hypot(x - WIDTH / 2, y - HEIGHT / 2) > 120:
                break
        vx = random.choice([-1, 1]) * random.uniform(1.5, 3)
        vy = random.choice([-1, 1]) * random.uniform(1.5, 3)
        return Obstacle(x, y, vx, vy)

    # ---------- time ----------
    @property
    def time_left(self):
        elapsed = (pygame.time.get_ticks() - self.round_start) / 1000
        return max(0.0, ROUND_SECONDS - elapsed)

    # ---------- per frame ----------
    def handle_input(self, keys_pressed):
        if self.game_over:
            if keys_pressed[pygame.K_r]:
                self.reset()
            return
        dx = dy = 0
        if keys_pressed[pygame.K_UP]:
            dy -= self.player.speed
        if keys_pressed[pygame.K_DOWN]:
            dy += self.player.speed
        if keys_pressed[pygame.K_LEFT]:
            dx -= self.player.speed
        if keys_pressed[pygame.K_RIGHT]:
            dx += self.player.speed
        self.player.move(dx, dy, WIDTH, HEIGHT)

    def update(self):
        if self.game_over:
            return

        for obstacle in self.obstacles:
            obstacle.update(WIDTH, HEIGHT)

        # Task 1 fix: remove each collected coin (and spawn a replacement)
        # so it can only ever be scored once.
        for coin in check_collection(self.player, self.coins):
            self.score += coin.value
            self.coins.remove(coin)
            self.coins.append(self._random_coin())

        # Obstacle hit: lose one life, then a grace period so a single
        # touch doesn't drain a life every frame.
        now = pygame.time.get_ticks()
        if now >= self.invulnerable_until and check_obstacle_hit(self.player, self.obstacles):
            self.lives -= 1
            self.invulnerable_until = now + INVULNERABLE_MS

        if self.lives <= 0 or self.time_left <= 0:
            self.game_over = True

    def draw(self, surface, font):
        from game import renderer
        flash = pygame.time.get_ticks() < self.invulnerable_until
        renderer.draw_scene(surface, self.player, self.coins, self.obstacles, flash)
        renderer.draw_text(surface, font, f"Score: {self.score}", (10, 10))
        renderer.draw_text(surface, font, f"Lives: {self.lives}", (10, 36))
        renderer.draw_text(surface, font, f"Time: {math.ceil(self.time_left)}", (WIDTH - 110, 10))
        if self.game_over:
            renderer.draw_game_over(surface, font, self.score)
