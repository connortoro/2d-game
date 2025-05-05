from raylibpy import *
from animation import Animation, REPEATING, ONESHOT
from orc import Orc, OrcType
from utilities import direction_between_rects, vector2_scale, center_of_rect, vector2_subtract, vector2_length
from collisions import check_obstacle_collisions

class OrcDasher(Orc):
    def __init__(self, sheet, x, y, world_width, world_height):
        super().__init__(sheet, x, y, world_width, world_height, orc_type=OrcType.ELITE)
        self.speed = 125

        self.animations = {
            "idle_front":    Animation(0, 3, 0, 0, 64, 0.2, 0.2, REPEATING, 64, 64),
            "run_back":      Animation(0, 7, 0, 1, 64, 0.15, 0.15, REPEATING, 64, 64),
            "run_front":     Animation(0, 7, 0, 2, 64, 0.15, 0.15, REPEATING, 64, 64),
            "run_left":      Animation(0, 7, 0, 3, 64, 0.15, 0.15, REPEATING, 64, 64),
            "run_right":     Animation(0, 7, 0, 4, 64, 0.15, 0.15, REPEATING, 64, 64),

            "attack_back":   Animation(0, 7, 0, 5, 64, 0.1, 0.1, ONESHOT, 64, 64),
            "attack_front":  Animation(0, 7, 0, 6, 64, 0.1, 0.1, ONESHOT, 64, 64),
            "attack_left":   Animation(0, 7, 0, 7, 64, 0.1, 0.1, ONESHOT, 64, 64),
            "attack_right":  Animation(0, 7, 0, 8, 64, 0.1, 0.1, ONESHOT, 64, 64),

            "dash_back":     Animation(0, 7, 0, 9, 64, 0.2, 0.08, ONESHOT, 64, 64),
            "dash_front":    Animation(0, 7, 0, 10, 64, 0.2, 0.08, ONESHOT, 64, 64),
            "dash_left":     Animation(0, 7, 0, 11, 64, 0.2, 0.08, ONESHOT, 64, 64),
            "dash_right":    Animation(0, 7, 0, 12, 64, 0.2, 0.08, ONESHOT, 64, 64),

            "death":         Animation(0, 7, 0, 13, 64, 0.15, 0.15, ONESHOT, 64, 64),
        }

        self.animation = self.animations["idle_front"]

        # Dash state
        self.is_dashing = False
        self.dash_timer = 0
        self.dash_duration = 1.0
        self.dash_cooldown = 1.5
        self.dash_cooldown_timer = 0
        self.dash_speed = 300
        self.min_dash_range = 200
        self.max_dash_range = 800

    def update(self, player, rects, room):
        if not self.is_alive:
            return

        if self.is_dashing:
            self.dash_timer -= get_frame_time()

            # Apply dash movement manually
            delta = vector2_scale(self.vel, get_frame_time())
            self.rect.x += delta.x
            self.rect.y += delta.y

            # Handle collision
            check_obstacle_collisions(self, rects)

            # Set facing direction
            if abs(self.vel.x) > abs(self.vel.y):
                self.facing = "right" if self.vel.x > 0 else "left"
            else:
                self.facing = "down" if self.vel.y > 0 else "up"

            if self.dash_timer <= 0:
                self.is_dashing = False
                self.vel = Vector2(0, 0)

            self.update_position()
            self.update_animation()
            return  # Skip rest of update during dash

        # Check for dash trigger
        self.dash_cooldown_timer -= get_frame_time()
        if self.dash_cooldown_timer <= 0:
            player_center = center_of_rect(player.hitbox)
            orc_center = center_of_rect(self.rect)
            distance = vector2_length(vector2_subtract(player_center, orc_center))
            if self.min_dash_range <= distance <= self.max_dash_range:
                self.start_dash(player)

        # Fall back to base behavior if not dashing
        if not self.is_dashing:
            super().update(player, rects, room)

    def start_dash(self, player):
        dir_vec = direction_between_rects(self.rect, player.hitbox)
        self.vel = vector2_scale(dir_vec, self.dash_speed)
        self.is_dashing = True
        self.dash_timer = self.dash_duration
        self.dash_cooldown_timer = self.dash_cooldown
        print(f"[OrcDasher] Dashing toward player with vel={self.vel}")  # Debug print

    def update_animation(self):
        if self.is_dashing:
            direction_key = {
                "up": "back",
                "down": "front",
                "left": "left",
                "right": "right"
            }.get(self.facing, "front")

            dash_key = f"dash_{direction_key}"
            desired = self.animations.get(dash_key, self.animation)

        elif self.is_attacking:
            direction_key = {
                "up": "back",
                "down": "front",
                "left": "left",
                "right": "right"
            }.get(self.facing, "front")

            attack_key = f"attack_{direction_key}"
            desired = self.animations.get(attack_key, self.animation)

        else:
            return super().update_animation()

        if self.animation != desired:
            self.animation = desired
            self.animation.reset()

        self.animation.animation_update()
