from raylibpy import *
from animation import Animation, REPEATING, ONESHOT
from collisions import *
from utilities import *
from projectile import Projectile
import time

class Necro:
    W = 200
    H = 200
    SCALE = 4

    def __init__(self, sheet, x, y):
        self.sheet = sheet
        self.vel = Vector2(0.0, 0.0)
        self.dmg = 20
        self.speed = 100
        self.rect = Rectangle(x, y, self.W * self.SCALE, self.H * self.SCALE)
        self.idle_animation = Animation(0, 7, 0, 0, 128, 0.2, 0.2, REPEATING, 160, 160)
        self.death_animation = Animation(0, 7, 0, 6, 128, 0.15, 0.15, REPEATING, 160, 160)
        self.hit_animation = Animation(0, 4, 1, 5, 128, 0.15, 0.15, REPEATING, 160, 160)
        self.attack_animation = Animation(0, 7, 0, 2, 128, 0.2, 0.2, REPEATING, 160, 160)

        self.animation = self.idle_animation

        self.hitbox = Rectangle(self.rect.x + (self.rect.width - 90) / 2, self.rect.y + self.rect.height - 60, 90, 110)
        self.health = 100
        self.maxHealth = self.health
        self.is_alive = True
        self.is_dying = False
        self.death_timer = 1


        ### ATTACK ###
        self.projectiles = []
        self.attack_timer = 2
        self.attack_duration = 4.5

        ### KNOCKBACK ###
        self.knockback_speed = 1100
        self.knockback_timer = 0
        self.knockback_duration = 0.3
        self.knockback_direction = None

    def update(self, player, rects, room):
      if not self.is_alive:
          return

      if self.health <= 0 and not self.is_dying:
          self.is_dying = True
          self.start_death_animation()

      if self.is_dying and self.death_timer > 0:
          self.animation.animation_update()
          self.death_timer -= get_frame_time()
          if self.death_timer <= 0:
              self.is_alive = False
              self.hitbox = Rectangle(0, 0, 0, 0)
      else:
          self.attack(player)
          for projectile in self.projectiles:
              projectile.update()
          self.animation.animation_update()
          if not self.is_dying:
              check_obstacle_collisions(self, rects)
          self.move(player)
          self.update_position()

    def move(self, player):
        if self.knockback_timer > 0:
            self.knockback_timer -= get_frame_time()
            if self.knockback_timer < .1:
                self.animation = self.idle_animation
                self.hit_animation.reset(1)
            ratio = (self.knockback_timer/self.knockback_duration) ** 2
            self.vel = vector2_scale(self.knockback_direction, ratio*self.knockback_speed)
        else:
            if self.attack_timer > 2.2:
                dir = Vector2(0, 0)
                return
            dir = direction_between_rects(self.hitbox, player.hitbox)
            self.vel.x = dir.x * self.speed
            self.vel.y = dir.y * self.speed

    def update_position(self):
      self.rect.x += self.vel.x * get_frame_time()
      self.rect.y += self.vel.y * get_frame_time()
      self.hitbox.x = self.rect.x + (self.rect.width - self.hitbox.width) / 2
      self.hitbox.y = 80+self.rect.y + (self.rect.height - self.hitbox.height) / 2

    def draw(self):
        if not self.is_alive:
            return

        if not self.is_dying:
            self.draw_health_bar()
        source = self.animation.animation_frame_horizontal()
        origin = Vector2(0.0, 0.0)
        # draw_rectangle_lines_ex(self.hitbox, 2.0, RED)
        # draw_rectangle_lines_ex(self.rect, 2.0, RED)
        draw_texture_pro(self.sheet, source, self.rect, origin, 0.0, WHITE)
        for projectile in self.projectiles:
            projectile.draw()

    def draw_health_bar(self):
        draw_rectangle(self.hitbox.x+10, self.hitbox.y-130, 100, 8, RED)
        ratio = self.health/self.maxHealth
        draw_rectangle(self.hitbox.x+10, self.hitbox.y-130, 100*ratio, 8, GREEN)

    def take_damage(self, damage, dir):
        self.health -= damage
        self.knockback_timer = self.knockback_duration
        self.knockback_direction = dir
        self.animation = self.hit_animation

    def start_death_animation(self):
        self.animation = self.death_animation

    def attack(self, player):
        if self.attack_timer > 0:
            self.attack_timer -= get_frame_time()
            if self.attack_timer < 1:
                self.animation = self.idle_animation
        else:
          self.animation = self.attack_animation
          v = center_of_rect(self.hitbox)
          dir = direction_between_rects(self.hitbox, player.hitbox)
          p = Projectile(v.x, v.y, 15, dir)
          self.projectiles.append(p)
          self.attack_timer = self.attack_duration
