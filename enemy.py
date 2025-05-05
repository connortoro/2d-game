from raylibpy import *
from utilities import (
    center_of_rect, vector2_subtract, vector2_length, vector2_normalize,
    Pathfinder, vector2_scale
)
from collisions import check_obstacle_collisions, check_collision_line_rec, check_collision_recs
from objects.gold import Gold
from objects.heart import Heart
import random

class Enemy:
    W = 32
    H = 32
    SCALE = 4

    def __init__(self, sheet, x, y, hp, speed, dmg, animations, death_animation, world_width, world_height, sound_manager=None, attack_range=125, attack_width=150, show_radius=True, use_melee_attack=True):
        self.sheet = sheet
        self.vel = Vector2(0.0, 0.0)
        self.dmg = dmg
        self.speed = speed
        self.rect = Rectangle(x, y, self.W * self.SCALE, self.H * self.SCALE)
        self.animations = animations
        self.animation = self.animations.get("idle_front")
        self.death_animation = death_animation
        self.hitbox = Rectangle(self.rect.x + (self.rect.width - 90) / 2, self.rect.y + self.rect.height - 60, 90, 60)
        self.health = hp
        self.maxHealth = self.health
        self.sound_manager = sound_manager
        self.size = 1.0
        self.sprite_offset_x = 0
        self.sprite_offset_y = 0
        self.last_reachable_pos = None
        self.los_chase_grace = 0.3
        self.los_chase_timer = 0.0

        self.use_melee_attack = use_melee_attack
        self.is_attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_cooldown_time = 1.0
        self.attack_range = attack_range
        self.attack_width = attack_width
        self.attack_duration = 0.4
        self.facing = "right"

        self.is_alive = True
        self.is_dying = False
        self.show_radius = show_radius
        self.death_timer = 1
        self.detection_radius = 450.0
        self.knockback_speed = 1100
        self.knockback_timer = 0
        self.knockback_duration = 0.3
        self.knockback_direction = None

        self.path = []
        self.current_waypoint = 0
        self.path_update_cooldown = 0
        self.path_update_interval = 0.5
        self.cell_size = 64
        self.pathfinder = Pathfinder(self.cell_size)
        self.world_width = world_width
        self.world_height = world_height

    def update_grid(self, obstacles):
        self.pathfinder.update_grid(obstacles, self.world_width, self.world_height)

    def update(self, player, rects, room):
        if not self.is_alive:
            return

        if self.health <= 0 and not self.is_dying:
            self.is_dying = True
            self.start_death_animation()
            self.drop_item(room)

        if self.is_dying:
            self.death_animation.animation_update()
            self.death_timer -= get_frame_time()
            if self.death_timer <= 0:
                self.is_alive = False
                self.hitbox = Rectangle(0, 0, 0, 0)
            return

        self.update_movement(player, rects)
        if self.use_melee_attack:
            self.update_attack(player)
        check_obstacle_collisions(self, rects)
        self.update_position()
        self.update_animation()

    def update_movement(self, player, obstacles):
        if self.knockback_timer > 0:
            self.knockback_timer -= get_frame_time()
            ratio = (self.knockback_timer / self.knockback_duration) ** 2
            self.vel = vector2_scale(self.knockback_direction, ratio * self.knockback_speed)
            return

        src = center_of_rect(self.hitbox)
        tgt = center_of_rect(player.hitbox)
        to_player = vector2_subtract(tgt, src)
        dist_to_player = vector2_length(to_player)

        if abs(to_player.x) > abs(to_player.y):
            self.facing = "right" if to_player.x > 0 else "left"
        else:
            self.facing = "down" if to_player.y > 0 else "up"

        if dist_to_player <= self.detection_radius:
            if self.has_line_of_sight(player, obstacles):
                self.los_chase_timer = self.los_chase_grace
            else:
                self.los_chase_timer -= get_frame_time()

            if self.los_chase_timer > 0:
                self.path = []
                dir_vec = vector2_normalize(to_player)
                self.vel = Vector2(dir_vec.x * self.speed, dir_vec.y * self.speed)
                self.last_reachable_pos = None
                return

            self.path_update_cooldown -= get_frame_time()
            if self.path_update_cooldown <= 0 or not self.path:
                self.path_update_cooldown = self.path_update_interval
                self.update_grid(obstacles)
                new_path = self.pathfinder.find_path(src, tgt)
                if new_path:
                    self.path = new_path
                    self.current_waypoint = 0
                    self.last_reachable_pos = new_path[-1]

            if self.path and self.current_waypoint < len(self.path):
                target_pos = self.path[self.current_waypoint]
                to_target = vector2_subtract(target_pos, src)
                if vector2_length(to_target) < 10:
                    self.current_waypoint += 1
                else:
                    dir_vec = vector2_normalize(to_target)
                    self.vel = Vector2(dir_vec.x * self.speed, dir_vec.y * self.speed)
            elif self.last_reachable_pos:
                to_last = vector2_subtract(self.last_reachable_pos, src)
                if vector2_length(to_last) > 5:
                    dir_vec = vector2_normalize(to_last)
                    self.vel = Vector2(dir_vec.x * self.speed, dir_vec.y * self.speed)
                else:
                    self.vel = Vector2(0.0, 0.0)
            else:
                self.vel = Vector2(0.0, 0.0)

        else:
            self.vel = Vector2(0.0, 0.0)
            self.path = []
            self.los_chase_timer = 0

    def update_position(self):
        self.rect.x += self.vel.x * get_frame_time()
        self.rect.y += self.vel.y * get_frame_time()
        self.hitbox.x = self.rect.x + (self.rect.width - self.hitbox.width) / 2
        self.hitbox.y = self.rect.y + self.rect.height - self.hitbox.height

    def update_animation(self):
        def safe_get(key, fallback="idle_front"):
            return self.animations.get(key, self.animations.get(fallback, None))

        if not self.is_alive:
            desired = safe_get("death")
        elif self.is_attacking:
            facing_map = {
                "up": "back",
                "down": "front",
                "left": "left",
                "right": "right"
            }
            desired = safe_get(f"attack_" + facing_map.get(self.facing, "front"))
        elif self.vel.x != 0 or self.vel.y != 0:
            desired = safe_get(f"run_" + self.facing)
        else:
            desired = safe_get("idle_front")

        if desired and self.animation != desired:
            self.animation = desired
            self.animation.reset()

        if self.animation:
            self.animation.animation_update()

    def update_attack(self, player):
        if self.is_attacking:
            self.attack_timer -= get_frame_time()
            if self.attack_timer <= 0:
                self.is_attacking = False
        elif self.attack_cooldown <= 0 and self.in_attack_range(player):
            self.start_attack(player)
        else:
            self.attack_cooldown -= get_frame_time()

    def start_attack(self, player):
        self.is_attacking = True
        self.attack_timer = self.attack_duration
        self.attack_cooldown = self.attack_cooldown_time
        if self.check_attack_collision(player):
            player.take_damage(self.dmg, self.hitbox)

    def in_attack_range(self, player):
        return vector2_length(vector2_subtract(center_of_rect(player.hitbox), center_of_rect(self.hitbox))) <= self.attack_range

    def check_attack_collision(self, player):
        return check_collision_recs(self.get_attack_hitbox(), player.hitbox)

    def get_attack_hitbox(self):
        offset = self.attack_range
        height = 60
        if self.facing == "left":
            return Rectangle(self.hitbox.x - offset, self.hitbox.y + self.hitbox.height / 2 - height / 2, offset, height)
        elif self.facing == "right":
            return Rectangle(self.hitbox.x + self.hitbox.width, self.hitbox.y + self.hitbox.height / 2 - height / 2, offset, height)
        elif self.facing == "up":
            return Rectangle(self.hitbox.x + self.hitbox.width / 2 - self.attack_width / 2, self.hitbox.y - offset, self.attack_width, offset)
        else:
            return Rectangle(self.hitbox.x + self.hitbox.width / 2 - self.attack_width / 2, self.hitbox.y + self.hitbox.height, self.attack_width, offset)

    def has_line_of_sight(self, player, obstacles):
        src = center_of_rect(self.hitbox)
        tgt = center_of_rect(player.hitbox)
        for rect in obstacles:
            if check_collision_line_rec(src, tgt, rect):
                return False
        return True

    def draw(self):
        if not self.is_alive:
            return
        if self.is_attacking:
            draw_rectangle_lines_ex(self.get_attack_hitbox(), 2, YELLOW)
        draw_rectangle_lines_ex(self.hitbox, 2, RED)
        if self.animation:
            src = self.animation.animation_frame_horizontal()
            scaled = Rectangle(self.rect.x + self.sprite_offset_x, self.rect.y + (self.rect.height - self.rect.height * self.size) + self.sprite_offset_y, self.rect.width * self.size, self.rect.height * self.size)
            draw_texture_pro(self.sheet, src, scaled, Vector2(0.0, 0.0), 0.0, WHITE)
        if self.show_radius:
            draw_circle_lines(int(self.rect.x + self.rect.width / 2), int(self.rect.y + self.rect.height / 2), self.detection_radius, Color(255, 0, 0, 50))

    def draw_health_bar(self):
        bar_width = 80
        bar_height = 6
        x = self.rect.x + (self.rect.width - bar_width) / 2
        y = self.rect.y - 12
        draw_rectangle(int(x), int(y), bar_width, bar_height, RED)
        draw_rectangle(int(x), int(y), int(bar_width * (self.health / self.maxHealth)), bar_height, GREEN)

    def take_damage(self, damage, direction):
        self.health -= damage
        self.knockback_timer = self.knockback_duration
        self.knockback_direction = direction

    def start_death_animation(self):
        self.animation = self.death_animation

    def drop_item(self, room):
        if not self.sound_manager:
            return  

        x = self.rect.x + self.rect.width / 2.0
        y = self.rect.y + self.rect.height / 2.0
        roll = random.randint(0, 8)

        if roll > 4:
            if roll > 6:
                room.objects.append(Heart(x, y, self.sound_manager))
            else:
                room.objects.append(Gold(x, y, self.sound_manager))

