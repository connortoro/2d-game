from raylibpy import *
from animation import Animation, REPEATING, ONESHOT
from collisions import *
from objects.heart import Heart
from objects.gold import Gold
import random

class Enemy:
    W = 32
    H = 32
    SCALE = 4

    def __init__(self, sheet, x, y, hp, speed, dmg, animation, death_animation):
        self.sheet = load_texture(sheet)
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

    def update(self, player, rects, room):

        if not self.is_alive:
            return
        
        if self.health <= 0 and not self.is_dying:
            self.is_dying = True  
            self.start_death_animation()
            self.drop_item(room) 

        if self.is_dying and self.death_timer > 0:
            self.animation.animation_update()
            self.death_timer -= get_frame_time()
            if self.death_timer <= 0: 
                self.is_alive = False
                self.hitbox = Rectangle(0, 0, 0, 0)
        else:
            self.animation.animation_update()
            if not self.is_dying:
                check_obstacle_collisions(self, rects)
            self.move(player.rect)
            self.update_position()

    def move(self, player):
        # Calculate dir
        enemy_center = Vector2(self.hitbox.x + self.hitbox.width/2, self.hitbox.y + self.hitbox.height/2)
        player_center = Vector2(player.x + player.width/2, player.y + player.height/2)
        dir = vector2_normalize(vector2_subtract(player_center, enemy_center))
        self.vel.x = dir.x * self.speed
        self.vel.y = dir.y * self.speed
        

    def update_position(self):
        self.rect.x += self.vel.x * get_frame_time()
        self.rect.y += self.vel.y * get_frame_time()
        self.hitbox.x = self.rect.x + (self.rect.width - self.hitbox.width) / 2
        self.hitbox.y = self.rect.y + self.rect.height - self.hitbox.height

    def draw(self):
        if not self.is_alive:
            return  # Don't draw if the enemy is dead

        # Draw normal animation
        if not self.is_dying:
            self.draw_health_bar()
        source = self.animation.animation_frame_horizontal()
        origin = Vector2(0.0, 0.0)
        draw_texture_pro(self.sheet, source, self.rect, origin, 0.0, WHITE)
    
    def draw_health_bar(self):
        draw_rectangle(self.rect.x+25, self.rect.y+4, 80, 5, RED)
        ratio = self.health/self.maxHealth
        draw_rectangle(self.rect.x+25, self.rect.y+4, 80*ratio, 5, GREEN)


    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.is_dying = True  # Start death process

    def start_death_animation(self):
        self.animation = self.death_animation

    def drop_item(self, room):
        roll = random.randint(0, 8)
        if roll > 4:
            x = self.rect.x + (self.rect.width / 2.0)
            y = self.rect.y + (self.rect.height / 2.0)
            if roll > 6:
                room.objects.append(Heart(x, y))
            else:
                room.objects.append(Gold(x, y))
        
