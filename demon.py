from raylibpy import *
from animation import Animation, REPEATING, ONESHOT
from collisions import *
from utilities import *
from utilities import distance_between_rects
import textures

class Demon:
    W = 288
    H = 160
    SCALE = 3

    def __init__(self, sheet, x, y, room, sound_manager):
        self.room = room
        self.sound_manager = sound_manager 
        self.sheet = sheet
        self.vel = Vector2(0.0, 0.0)
        self.dmg = 50
        self.speed = 250
        self.rect = Rectangle(x, y, self.W * self.SCALE, self.H * self.SCALE)
        self.door = None

        self.idle_animation = Animation(0, 5, 0, 0, self.H, 0.1, 0.1, REPEATING, self.W , self.H)
        self.walk_animation = Animation(0, 11, 0, 1, self.H, 0.1, 0.1, REPEATING, self.W , self.H)
        self.attack_animation = Animation(0, 14, 0, 2, self.H, 0.1, 0.1, ONESHOT, self.W , self.H)
        self.hit_animation = Animation(0, 4, 0, 3, self.H, 0.1, 0.1, ONESHOT, self.W , self.H)
        self.death_animation = Animation(0, 21, 0, 4, self.H, 0.1, 0.1, ONESHOT, self.W , self.H)

        self.state = 'walk'
        self.animation_state = {
            'idle': self.idle_animation,
            'walk': self.walk_animation,
            'attack': self.attack_animation,
            'hit': self.hit_animation,
            'death': self.death_animation
        }

        self.animation = self.idle_animation
        self.facing_left = True
        self.hitbox = Rectangle(self.rect.x + (self.rect.width - 200) / 2, self.rect.y + self.rect.height - 180, 200, 180)
        self.health = 300
        self.max_health = self.health
        self.is_alive = True
        self.is_dying = False
        self.death_timer = 1

        self.attack_timer = 2
        self.attack_duration = 1.5
        self.attack_range = 200
        self.attack_triggered = False
        self.attack_hitbox = Rectangle(0, 0, 220, 220)

        self.raging = False
        self.knockback_speed = 1000
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
            self.animation_state[self.state].animation_update()
            return

        self.update_attack(player)
        self.animation_state[self.state].animation_update()
        
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
            if self.state == 'attack':
                self.vel = Vector2(0, 0)
                return
            dir = direction_between_rects(self.hitbox, player.hitbox)
            self.vel.x = dir.x * self.speed
            self.vel.y = dir.y * self.speed
            self.facing_left = dir.x < 0

    def update_position(self):
        self.rect.x += self.vel.x * get_frame_time()
        self.rect.y += self.vel.y * get_frame_time()
        self.hitbox.x = self.rect.x + (self.rect.width - self.hitbox.width) / 2
        self.hitbox.y = 80 + self.rect.y + (self.rect.height - self.hitbox.height) / 2

    def update_attack(self, player):
        distance = distance_between_rects(self.hitbox, player.hitbox)
        
        if self.state == 'attack':
            self.attack_timer -= get_frame_time()
            
            if 9 <= self.attack_animation.cur <= 11:
                self.attack_hitbox.width = 250
                self.attack_hitbox.height = 250
                
                dir = direction_between_rects(self.hitbox, player.hitbox)
                if not hasattr(self, 'attack_direction'):
                    self.attack_direction = dir

                self.attack_hitbox.x = self.hitbox.x + self.attack_direction.x * 150
                self.attack_hitbox.y = self.hitbox.y + self.attack_direction.y * 150
                
                if not self.attack_triggered:
                    if check_collision_recs(self.attack_hitbox, player.hitbox):
                        player.take_damage(self.dmg, self.attack_hitbox)
                        dir = direction_between_rects(self.hitbox, player.hitbox)
                        player.knockback_direction = dir
                        player.knockback_timer = player.knockback_duration
                    self.attack_triggered = True
            else:
                self.attack_hitbox.width = 0
                self.attack_hitbox.height = 0
                
            if self.attack_timer <= 0:
                self.state = 'walk'
                self.attack_triggered = False
                self.attack_timer = self.attack_duration
                if hasattr(self, 'attack_direction'):
                    delattr(self, 'attack_direction')
        else:
            if distance < self.attack_range:
                self.state = 'attack'
                self.attack_animation.reset()

    def draw(self):
        if self.door:
            draw_texture_pro(textures.old_base, Rectangle(3*16, 2*16, 16, 16), 
                        self.door, Vector2(0, 0), 0.0, WHITE)
        
        if self.state != 'death':
            self.draw_health_bar()
            
        source = self.animation_state[self.state].animation_frame_horizontal()
        if self.knockback_timer > .1:
            source = self.hit_animation.animation_frame_horizontal()

        if not self.facing_left:
            source.width = -source.width
            dest_rect = Rectangle(self.rect.x, self.rect.y, self.rect.width, self.rect.height)
        else:
            dest_rect = Rectangle(self.rect.x, self.rect.y, self.rect.width, self.rect.height)

        color = RED if self.health < self.max_health/2 else WHITE
        draw_texture_pro(self.sheet, source, dest_rect, Vector2(0.0, 0.0), 0.0, color)
        #draw_rectangle_lines_ex(self.hitbox, 2, GREEN)


    def draw_health_bar(self):
        draw_rectangle(self.hitbox.x+10, self.hitbox.y-130, 100, 8, RED)
        ratio = self.health/self.max_health
        draw_rectangle(self.hitbox.x+10, self.hitbox.y-130, 100*ratio, 8, GREEN)

    def take_damage(self, damage, dir):
        self.health -= damage
        self.knockback_timer = self.knockback_duration
        self.knockback_direction = dir

        if self.health < self.max_health/2 and not self.raging:
            self.raging = True
            self.attack_duration *= 0.75
            self.speed *= 1.3
            self.dmg = int(self.dmg * 1.5)

        if self.health <= 0:
            self.door = Rectangle(700, 400, 100, 100)
            self.hitbox = Rectangle(0, 0, 0, 0)