from raylibpy import *
from animation import Animation, REPEATING, ONESHOT
from collisions import *
from utilities import *
from projectile import Projectile
import random
from enemy import Enemy
import textures

class Necro:
    W = 200
    H = 200
    SCALE = 4

    def __init__(self, sheet, x, y, room):
        self.room = room
        self.sheet = sheet
        self.vel = Vector2(0.0, 0.0)
        self.dmg = 40
        self.speed = 200
        self.rect = Rectangle(x, y, self.W * self.SCALE, self.H * self.SCALE)
        self.door = None

        self.idle_animation = Animation(0, 7, 0, 0, 128, 0.2, 0.2, REPEATING, 160, 160)
        self.death_animation = Animation(0, 10, 0, 6, 128, 0.15, 0.15, ONESHOT, 160, 160)
        self.attack_animation = Animation(0, 12, 0, 2, 128, 0.075, 0.075, ONESHOT, 160, 160)

        self.hit = Animation(0, 7, 1, 5, 128, 0.12, 0.12, ONESHOT, 160, 160)

        self.state = 'idle'
        self.anim_map = {
            'idle': self.idle_animation,
            'death': self.death_animation,
            'attack': self.attack_animation
        }

        self.animation = self.idle_animation

        self.hitbox = Rectangle(self.rect.x + (self.rect.width - 90) / 2, self.rect.y + self.rect.height - 60, 90, 110)
        self.health = 30
        self.maxHealth = self.health
        self.is_alive = True
        self.is_dying = False
        self.death_timer = 1


        ### ATTACK ###
        self.projectiles = []
        self.attack_timer = 2
        self.attack_duration = 4.8
        self.attack_triggered = False
        self.second_attack_triggered = False
        self.cascade_timer = 0
        self.cascade_num = 20

        ### KNOCKBACK ###
        self.raging = False
        self.knockback_speed = 1100
        self.knockback_timer = 0
        self.knockback_duration = 0.3
        self.knockback_direction = None

    def update(self, player, rects, room):
        if self.door:
            if check_collision_recs(self.door, player.hitbox):
                self.room.floor.next_floor()
        if self.health <= 0:
            self.knockback_timer = 0
            self.state = 'death'
            self.anim_map[self.state].animation_update()
            return

        self.update_attack(player)
        for projectile in self.projectiles:
            projectile.update()
        self.anim_map[self.state].animation_update()
        if not self.is_dying:
            check_obstacle_collisions(self, rects)
        self.move(player)
        self.update_position()

    def move(self, player):
        if self.knockback_timer > 0:
            self.knockback_timer -= get_frame_time()
            ratio = (self.knockback_timer/self.knockback_duration) ** 2
            self.vel = vector2_scale(self.knockback_direction, ratio*self.knockback_speed)
        else:
            if self.attack_timer > 3.2:
                self.vel = Vector2(0, 0)
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
        if self.door:
            draw_texture_pro(textures.old_base, Rectangle(3*16, 2*16, 16, 16), self.door, Vector2(0, 0), 0.0, WHITE)
        if self.state != 'death':
            self.draw_health_bar()
        source = self.anim_map[self.state].animation_frame_horizontal()
        if self.knockback_timer > .1:
            source = self.hit.animation_frame_horizontal()

        color = RED if self.health < 150 else WHITE
        draw_texture_pro(self.sheet, source, self.rect, Vector2(0.0, 0.0), 0.0, color)

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

        if self.health < 150 and not self.raging:
            self.raging = True
            self.attack_duration *= 0.75
            self.speed *= 1.2

        if self.health <= 0:
            self.door = Rectangle(700, 400, 100, 100)
            self.hitbox = Rectangle(0, 0, 0, 0)
            self.projectiles = []

    def update_attack(self, player):
        self.attack_timer -= get_frame_time()
        self.cascade()
        if self.attack_timer <= 0:
            self.attack_animation.reset()
            self.state = 'attack'
            self.attack_triggered = self.second_attack_triggered = False
            self.attack_timer = self.attack_duration

        elif self.attack_animation.cur == 8 and not self.attack_triggered:
            self.fire_projectiles(player)
            self.attack_triggered = True

        elif self.attack_animation.cur == 11 and self.health < 150 and not self.second_attack_triggered:
            self.fire_projectiles(player)
            self.second_attack_triggered = True

        elif self.attack_animation.cur == 12 and self.cascade_num >= 9:
            self.state = 'idle'

    def fire_projectiles(self, player):
        c = center_of_rect(self.hitbox)
        c.x += 90
        c.y -= 270

        roll = random.randint(1, 5)
        if roll == 1:
            reroll = random.randint(1, 2)
            if reroll == 1:
                #cross
                dirs = [Vector2(0, 1), Vector2(0, -1), Vector2(1, 0), Vector2(-1, 0)]
                for dir in dirs:
                    self.projectiles.append(Projectile(c.x, c.y, 15, dir))
            else:
                #diag
                dirs = [Vector2(0.707, 0.707), Vector2(-0.707, 0.707), Vector2(0.707, -0.707), Vector2(-0.707, -0.707)]
                for dir in dirs:
                    self.projectiles.append(Projectile(c.x, c.y, 15, dir))
        elif roll == 2:
            #necromance
            self.room.enemies.append(Enemy(textures.minion, 100, 100, 30, 140, 10, Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32), Animation(0, 4, 1, 10, 16, .2, .2, ONESHOT, 32, 32)))
            self.room.enemies.append(Enemy(textures.minion, 1200, 650, 30, 140, 10, Animation(0, 3, 1, 0, 16, 0.2, 0.2, REPEATING, 32, 32), Animation(0, 4, 1, 10, 16, .2, .2, ONESHOT, 32, 32)))
        elif roll == 3:
            #shotgun
            dir = direction_between_rects(Rectangle(c.x, c.y, 1, 1), player.hitbox)
            dirs = [dir, vector2_rotate(dir, 0.3), vector2_rotate(dir, -0.3)]
            for d in dirs:
                self.projectiles.append(Projectile(c.x, c.y, 15, d))
            return
        elif roll == 4:
            #multi
            dirs = [Vector2(0, 1), Vector2(0, -1), Vector2(1, 0), Vector2(-1, 0), Vector2(0.707, 0.707), Vector2(-0.707, 0.707), Vector2(0.707, -0.707), Vector2(-0.707, -0.707)]
            for dir in dirs:
                self.projectiles.append(Projectile(c.x, c.y, 15, dir))
        elif roll == 5:
            #spin
            self.cascade_timer = 0
            self.cascade_num = 0

    def cascade(self):
        c = center_of_rect(self.hitbox)
        c.x += 90
        c.y -= 270
        if self.cascade_num >= 18: return
        self.cascade_timer -= get_frame_time()
        if self.cascade_timer < 0:
            self.cascade_timer = .04
            dir = vector2_rotate(Vector2(1, 0), 6*(self.cascade_num/10))
            self.projectiles.append(Projectile(c.x, c.y, 15, dir))
            self.cascade_num += 1

