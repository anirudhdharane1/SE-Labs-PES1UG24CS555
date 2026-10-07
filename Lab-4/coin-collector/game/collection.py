"""
collection: figures out which coins the player has collected this frame,
and whether the player is touching an obstacle.
"""


def check_collection(player, coins):
    """
    Returns the list of coins the player is currently overlapping.
    (The caller is responsible for removing them so each is collected once.)
    """
    player_rect = player.get_rect()
    return [coin for coin in coins if player_rect.colliderect(coin.get_rect())]


def check_obstacle_hit(player, obstacles):
    """Returns True if the player overlaps any obstacle."""
    player_rect = player.get_rect()
    return any(player_rect.colliderect(o.get_rect()) for o in obstacles)
