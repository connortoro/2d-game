from orc import Orc, OrcType
from animation import Animation, REPEATING, ONESHOT
from raylibpy import get_frame_time, Vector2, draw_circle_lines, Color, Rectangle, check_collision_recs, draw_texture_pro, WHITE
from utilities import center_of_rect, vector2_subtract, vector2_length, vector2_normalize, direction_between_rects, vector2_scale
from collisions import check_collision_line_rec
from raylibpy import (
    get_frame_time, Vector2, draw_circle_lines, Color,
    Rectangle, check_collision_recs, draw_texture_pro,
    draw_rectangle, WHITE, RED, GREEN
)


class OrcBoss(Orc):
    def __init__(self, sheet, x, y, world_width, world_height):
        super().__init__(sheet, x, y, world_width, world_height, orc_type=OrcType.BOSS)
        self.size = 2.5
        self.speed = 150
        self.sprite_offset_y = 80
        self.sprite_offset_x = -100
        self.door = None

        self.detection_radius = 1000  

        self.animations.update({
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

            "spin":          Animation(0, 9, 0, 13, 64, 0.1, 0.1, ONESHOT, 64, 64),
            "death":         Animation(0, 8, 0, 14, 64, 0.15, 0.15, ONESHOT, 64, 64)
        })

        self.is_dashing = False
        self.dash_timer = 0
        self.dash_duration = 1
        self.dash_cooldown = 3
        self.dash_cooldown_timer = 0
        self.dash_speed = 500
        self.min_dash_range = 200
        self.max_dash_range = 800
        self.dash_vel = Vector2(0, 0)
        self.dash_completed = False
        self.dash_count = 0

        self.is_spinning = False
        self.spin_radius = 160
        self.spin_duration = 1.2
        self.spin_timer = 0
        self.spin_damage = 20
        self.spin_charge_time = 0.8
        self.spin_charge_timer = 0
        self.is_spin_charging = False
        self.spin_ready = False

        self.world_width = world_width
        self.world_height = world_height
        self.raging = False
    def update(self, player, obstacles, room):
        if self.door and check_collision_recs(self.door, player.hitbox):
            room.floor.next_floor()
        if not self.is_alive:
            return


        if self.is_dashing:
            self.dash_timer -= get_frame_time()
            delta = vector2_scale(self.dash_vel, get_frame_time())

            new_x = self.rect.x + delta.x
            new_y = self.rect.y + delta.y

            # Clamp position within world bounds
            new_x = max(0, min(self.world_width - self.rect.width, new_x))
            new_y = max(0, min(self.world_height - self.rect.height, new_y))

            self.rect.x = new_x
            self.rect.y = new_y

            if abs(self.dash_vel.x) > abs(self.dash_vel.y):
                self.facing = "right" if self.dash_vel.x > 0 else "left"
            else:
                self.facing = "down" if self.dash_vel.y > 0 else "up"

            if self.dash_timer <= 0:
                self.is_dashing = False
                self.dash_vel = Vector2(0, 0)
                self.dash_completed = True
                self.dash_count += 1
                if self.health <= self.maxHealth / 2 and self.dash_count % 3 == 0:
                    self.spin_ready = True

            self.update_position()
            self.update_animation()
            return

        self.dash_cooldown_timer -= get_frame_time()

        if self.spin_ready and not self.is_spinning and not self.is_spin_charging:
            self.is_spin_charging = True
            self.spin_charge_timer = self.spin_charge_time
            self.vel = Vector2(0, 0)

        if self.is_spin_charging:
            self.spin_charge_timer -= get_frame_time()
            if self.spin_charge_timer <= 0:
                self.start_spin()
            self.update_position()
            self.update_animation()
            return

        if self.is_spinning:
            self.update_spin(player)
            self.update_position()
            self.update_animation()
            return

        if self.in_detection_range(player):
            if self.health < self.maxHealth * 0.9 and self.dash_cooldown_timer <= 0:
                src = center_of_rect(self.rect)
                tgt = center_of_rect(player.hitbox)
                dist = vector2_length(vector2_subtract(tgt, src))
                if self.min_dash_range <= dist <= self.max_dash_range:
                    dir_vec = direction_between_rects(self.rect, player.hitbox)
                    self.dash_vel = vector2_scale(dir_vec, self.dash_speed)
                    self.is_dashing = True
                    self.dash_timer = self.dash_duration
                    self.dash_cooldown_timer = self.dash_cooldown


        super().update(player, obstacles, room)

    def in_detection_range(self, player):
        return vector2_length(vector2_subtract(center_of_rect(player.hitbox), center_of_rect(self.hitbox))) <= self.detection_radius

    def has_line_of_sight(self, player, obstacles):
        src = center_of_rect(self.hitbox)
        tgt = center_of_rect(player.hitbox)
        for rect in obstacles:
            if check_collision_line_rec(src, tgt, rect):
                return False
        return True

    def start_spin(self):
        self.is_spinning = True
        self.is_spin_charging = False
        self.spin_ready = False
        self.spin_timer = self.spin_duration
        self.vel = Vector2(0, 0)
        self.has_hit_player_this_spin = False

    def update_spin(self, player):
        self.spin_timer -= get_frame_time()

        dist = vector2_length(vector2_subtract(center_of_rect(player.hitbox), center_of_rect(self.hitbox)))
        if dist <= self.spin_radius and not self.has_hit_player_this_spin:
            player.take_damage(self.spin_damage, self.hitbox)
            self.has_hit_player_this_spin = True

        if self.spin_timer <= 0:
            self.is_spinning = False

    def update_animation(self):
        if self.is_spinning and "spin" in self.animations:
            desired = self.animations["spin"]
            if self.animation != desired:
                self.animation = desired
                self.animation.reset()
            self.animation.animation_update()
        elif self.is_dashing:
            dash_key = {
                "up": "dash_back",
                "down": "dash_front",
                "left": "dash_left",
                "right": "dash_right"
            }.get(self.facing, "dash_front")
            desired = self.animations.get(dash_key, self.animation)
            if self.animation != desired:
                self.animation = desired
                self.animation.reset()
            self.animation.animation_update()
        else:
            super().update_animation()
    def take_damage(self, amount, direction):
        self.health -= amount

        # You can still trigger rage mode if needed
        if self.health < self.maxHealth / 2 and not self.raging:
            self.raging = True
            self.attack_duration *= 0.75
            self.speed *= 1.3
            self.dmg = int(self.dmg * 1.5)

        # Door + death handling
        if self.health <= 0 and self.door is None:
            self.door = Rectangle(700, 400, 100, 100)
            self.is_alive = False

    def draw_health_bar(self):
        bar_width = 100
        bar_height = 10
        padding = 130
        ratio = self.health / self.maxHealth
        x = self.hitbox.x + (self.hitbox.width - bar_width) / 2
        y = self.hitbox.y - padding - bar_height
        draw_rectangle(int(x), int(y), bar_width, bar_height, RED)
        draw_rectangle(int(x), int(y), int(bar_width * ratio), bar_height, GREEN)

    def draw(self):
        if self.door:
            from textures import old_base  # Make sure `textures` is accessible
            draw_texture_pro(old_base, Rectangle(3*16, 2*16, 16, 16), 
                             self.door, Vector2(0, 0), 0.0, WHITE)

        super().draw()

        if self.is_alive:
            self.draw_health_bar()

        if self.is_spin_charging or self.is_spinning:
            cx, cy = center_of_rect(self.rect)
            color = Color(255, 165, 0, 150) if self.is_spinning else Color(255, 255, 0, 150)
            draw_circle_lines(int(cx), int(cy), self.spin_radius, color)
