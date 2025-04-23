from raylibpy import *
from utilities import center_of_rect, has_line_of_sight, vector2_subtract, vector2_length, vector2_normalize
from utilities import create_pathfinding_grid, a_star_find_path, Pathfinder
from collisions import check_obstacle_collisions
import random
from objects.gold import Gold
from objects.heart import Heart

class Enemy:
    W = 32
    H = 32
    SCALE = 4

    def __init__(self, sheet, x, y, hp, speed, dmg, animation, death_animation, world_width, world_height):
        self.sheet = sheet
        self.vel = Vector2(0.0, 0.0)
        self.dmg = dmg
        self.speed = speed
        self.rect = Rectangle(x, y, self.W * self.SCALE, self.H * self.SCALE)
        self.animation = animation
        self.death_animation = death_animation
        self.hitbox = Rectangle(self.rect.x + (self.rect.width - 90) / 2, self.rect.y + self.rect.height - 60, 90, 60)
        self.health = hp
        self.maxHealth = self.health
        self.is_alive = True
        self.is_dying = False
        self.death_timer = 1
        self.detection_radius = 450.0
        self.crumb_reached_distance = 20.0
        self.show_radius = True
        self.knockback_speed = 1100
        self.knockback_timer = 0
        self.knockback_duration = 0.3
        self.knockback_direction = None
        self.path = []
        self.current_waypoint = 0
        self.path_update_cooldown = 0
        self.path_update_interval = 0.5  # Update path every 0.5 seconds
        self.cell_size = 64  # Should match your game's scale
        self.pathfinder = Pathfinder(self.cell_size)
        self.world_width = world_width
        self.world_height = world_height

    def update_grid(self, obstacles):
        """Update the pathfinding grid when obstacles change"""
        self.pathfinder.update_grid(obstacles, self.world_width, self.world_height)

    def update(self, player, rects, room):
        if not self.is_alive:
            return

        if self.health <= 0 and not self.is_dying:
            self.is_dying = True
            self.start_death_animation()
            self.drop_item(room)

        if self.is_dying:
            self.animation.animation_update()
            self.death_timer -= get_frame_time()
            if self.death_timer <= 0:
                self.is_alive = False
                self.hitbox = Rectangle(0, 0, 0, 0)
            return

        self.animation.animation_update()
        self.update_movement(player, rects)
        check_obstacle_collisions(self, rects)
        self.update_position()

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

        # Only check distance, not line of sight
        if dist_to_player <= self.detection_radius:
            # Update path periodically
            self.path_update_cooldown -= get_frame_time()
            if self.path_update_cooldown <= 0 or not self.path:
                self.path_update_cooldown = self.path_update_interval
                self.update_grid(obstacles)
                self.path = self.pathfinder.find_path(src, tgt)
                self.current_waypoint = 0

            # Follow the path if we have one
            if self.path and self.current_waypoint < len(self.path):
                target_pos = self.path[self.current_waypoint]
                to_target = vector2_subtract(target_pos, src)
                distance = vector2_length(to_target)
            
                if distance < 10:  # Reached waypoint
                    self.current_waypoint += 1
                else:
                    dir_vec = vector2_normalize(to_target)
                    self.vel.x = dir_vec.x * self.speed
                    self.vel.y = dir_vec.y * self.speed
            else:
                # Direct movement if no path
                dir_vec = vector2_normalize(to_player)
                self.vel.x = dir_vec.x * self.speed
                self.vel.y = dir_vec.y * self.speed
        else:
            # Player not in radius - stop moving
            self.vel = Vector2(0.0, 0.0)
            self.path = []  # Clear path when player is not detected
    def update_position(self):
        self.rect.x += self.vel.x * get_frame_time()
        self.rect.y += self.vel.y * get_frame_time()
        self.hitbox.x = self.rect.x + (self.rect.width - self.hitbox.width) / 2
        self.hitbox.y = self.rect.y + self.rect.height - self.hitbox.height

    def draw(self):
        if not self.is_alive:
            return

        if not self.is_dying:
            self.draw_health_bar()

        source = self.animation.animation_frame_horizontal()
        origin = Vector2(0.0, 0.0)
        draw_texture_pro(self.sheet, source, self.rect, origin, 0.0, WHITE)

        if self.show_radius:
            center_x = int(self.rect.x + self.rect.width / 2)
            center_y = int(self.rect.y + self.rect.height / 2)
            draw_circle_lines(center_x, center_y, self.detection_radius, Color(255, 0, 0, 50))

    def draw_health_bar(self):
        draw_rectangle(self.rect.x + 25, self.rect.y + 4, 80, 5, RED)
        ratio = self.health / self.maxHealth
        draw_rectangle(self.rect.x + 25, self.rect.y + 4, 80 * ratio, 5, GREEN)

    def take_damage(self, damage, dir):
        self.health -= damage
        self.knockback_timer = self.knockback_duration
        self.knockback_direction = dir

    def start_death_animation(self):
        self.animation = self.death_animation

    def drop_item(self, room):
        x = self.rect.x + self.rect.width / 2.0
        y = self.rect.y + self.rect.height / 2.0
        roll = random.randint(0, 8)
        if roll > 4:
            if roll > 6:
                room.objects.append(Heart(x, y))
            else:
                room.objects.append(Gold(x, y))