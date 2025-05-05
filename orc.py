from raylibpy import *
from animation import Animation, REPEATING, ONESHOT
from enemy import Enemy
from enum import Enum

class OrcState(Enum):
    IDLE = "idle_front"
    WALKING_LEFT = "run_left"
    WALKING_RIGHT = "run_right"
    WALKING_UP = "run_back"
    WALKING_DOWN = "run_front"
    ATTACK_LEFT = "attack_left"
    ATTACK_RIGHT = "attack_right"
    ATTACK_UP = "attack_back"
    ATTACK_DOWN = "attack_front"
    DEAD = "death"

class OrcType(Enum):
    NORMAL = 0
    ELITE = 1
    BOSS = 2

class Orc(Enemy):  # ✅ Inherit from Enemy
    def __init__(self, sheet, x, y, world_width, world_height, orc_type=OrcType.NORMAL):
        # === Stats ===
        if orc_type == OrcType.NORMAL:
            hp, speed, dmg = 100, 100, 20
        elif orc_type == OrcType.ELITE:
            hp, speed, dmg = 200, 110, 30
        elif orc_type == OrcType.BOSS:
            hp, speed, dmg = 500, 90, 50

        self.speed = 150
        # === Animations ===
        animations = {
            "idle_front":    Animation(0, 3, 0, 0, 64, 0.2, 0.2, REPEATING, 64, 64),
            "run_left":      Animation(0, 7, 0, 1, 64, 0.15, 0.15, REPEATING, 64, 64),
            "run_right":     Animation(0, 7, 0, 2, 64, 0.15, 0.15, REPEATING, 64, 64),
            "run_back":      Animation(0, 7, 0, 2, 64, 0.15, 0.15, REPEATING, 64, 64),  # reuse run_right
            "run_front":     Animation(0, 7, 0, 2, 64, 0.15, 0.15, REPEATING, 64, 64),  # reuse run_right
            "attack_left":   Animation(0, 7, 0, 3, 64, 0.1, 0.1, ONESHOT, 64, 64),
            "attack_right":  Animation(0, 7, 0, 4, 64, 0.1, 0.1, ONESHOT, 64, 64),
            "attack_back":   Animation(0, 6, 0, 5, 64, 0.1, 0.1, ONESHOT, 64, 64),
            "attack_front":  Animation(0, 6, 0, 6, 64, 0.1, 0.1, ONESHOT, 64, 64),
            "death":         Animation(0, 7, 0, 7, 64, 0.15, 0.15, ONESHOT, 64, 64),
        }

        death_anim = animations["death"]

        # ✅ Call Enemy constructor
        super().__init__(sheet, x, y, hp, speed, dmg, animations, death_anim, world_width, world_height)

        # Extra properties
        self.orc_type = orc_type
        self.size = 1.5
        self.sprite_offset_x = -30
        self.sprite_offset_y = 25

    def update(self, player, rects, room):
        super().update(player, rects, room)

        if self.orc_type == OrcType.BOSS:
            self.do_special_boss_abilities(player)

    def do_special_boss_abilities(self, player):
        pass  # Add boss logic here
