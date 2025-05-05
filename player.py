from raylibpy import *
from enum import Enum
from animation import Animation, REPEATING, ONESHOT
from sounds import SoundManager
from room import Room  # Import the Room class
import time
from collisions import *
from config import *
from utilities import *
# Dimensions of space

LEFT = -1
RIGHT = 1
UP = -2
DOWN = 2

class GameState(Enum):
    RUNNING = "RUNNING"
    PAUSED = "PAUSED"

class playerState(Enum):
    """PLAYER STATES"""
    IDLE = "IDLE"
    HURT = "HURT"
    DEAD = "DEAD"
    MOVE = "MOVE"
    ATTACK = "ATTACK"

    """WALKING STATES"""
    WALKING_UP = "WALKING_UP"
    WALKING_DOWN = "WALKING_DOWN"
    WALKING_LEFT = "WALKING_LEFT"
    WALKING_RIGHT = "WALKING_RIGHT"
    WALKING_UP_LEFT = "WALKING_UP_LEFT"
    WALKING_UP_RIGHT = "WALKING_UP_RIGHT"
    WALKING_DOWN_LEFT = "WALKING_DOWN_LEFT"
    WALKING_DOWN_RIGHT = "WALKING_DOWN_RIGHT"

    """ATTACKING STATES"""
    ATTACK_RIGHT = "ATTACK_RIGHT"
    ATTACK_UP = "ATTACK_UP"
    ATTACK_DOWN = "ATTACK_DOWN"
    ATTACK_LEFT = "ATTACK_LEFT"

class Player:
    def __init__(self, texture, sound_manager):
        """================================= BASICS ================================="""
        self.config = load_config()
        self.sound_manager = sound_manager
        sprite_width = 64.0 * 4
        sprite_height = 64.0 * 4
        self.rect = Rectangle(W / 2.0 - sprite_width / 2.0 , H / 2.0 - sprite_height / 2.0, sprite_width, sprite_height)
        self.vel = Vector2(0.0, 0.0)
        self.sprite = texture
        self.dir = RIGHT  # right
        self.death = load_texture("assets/player_sheet/player_spritesheet.png")
        feet_width = 10.0 * 4

        feet_width = 10.0 * 4
        feet_height = 8.0 * 6  # Make collision box shorter, just for feet
        self.hitbox_offset = 50
        self.hitbox = Rectangle(
            self.rect.x + (self.rect.width - feet_width) / 2,  # Center horizontally
            self.rect.y + self.rect.height - feet_height - self.hitbox_offset,  # Position at bottom of sprite
            feet_width,
            feet_height
        )

        self.in_dialog= False
        self.dialog_npc = None
        """================================= ANIMATIONS ================================="""
        self.animations = {
            playerState.IDLE: Animation(1, 11, 1, 0, 64, 0.1, 0.1, REPEATING, 64, 64),
            playerState.HURT: Animation(1, 4, 1, 11, 64, 0.1, 0.1, REPEATING, 64, 64),
            playerState.WALKING_UP: Animation(1, 5, 1, 8, 64, 0.1, 0.1, REPEATING, 64, 64),
            playerState.WALKING_DOWN: Animation(1, 5, 1, 7, 64, 0.1, 0.1, REPEATING, 64, 64),
            playerState.WALKING_RIGHT: Animation(1, 5, 1, 9, 64, 0.1, 0.1, REPEATING, 64, 64),
            playerState.WALKING_LEFT: Animation(1, 5, 1, 10, 64, 0.1, 0.1, REPEATING, 64, 64),
            playerState.WALKING_UP_LEFT: Animation(1, 5, 1, 8, 64, 0.1, 0.1, REPEATING, 64, 64),
            playerState.WALKING_UP_RIGHT: Animation(1, 5, 1, 8, 64, 0.1, 0.1, REPEATING, 64, 64),
            playerState.WALKING_DOWN_LEFT: Animation(1, 5, 1, 7, 64, 0.1, 0.1, REPEATING, 64, 64),
            playerState.WALKING_DOWN_RIGHT: Animation(1, 5, 1, 7, 64, 0.1, 0.1, REPEATING, 64, 64),
            playerState.DEAD: Animation(1, 5, 1, 12, 64, 0.1, 0.1, ONESHOT, 64, 64),
            playerState.ATTACK_RIGHT: Animation(1, 7, 1, 5, 64, 0.075, 0.075, ONESHOT, 64, 64),
            playerState.ATTACK_LEFT: Animation(1, 7, 1, 6, 64, 0.075, 0.075, ONESHOT, 64, 64),
            playerState.ATTACK_UP: Animation(1, 7, 1, 3, 64, 0.075, 0.075, ONESHOT, 64, 64),
            playerState.ATTACK_DOWN: Animation(1, 7, 1, 4, 64, 0.075, 0.075, ONESHOT, 64, 64),
        }

        self.state = playerState.IDLE  # default state
        self.attack_state = playerState.ATTACK_RIGHT
        self.current_animation = self.animations[self.state]  # default animation
        self.game_state = GameState.RUNNING
        self.is_hurt = False
        self.hurt_duration = 0.4
        """================================= PLAYER STATS ================================="""
        self.health = 100
        self.max_health = 100
        self.absolute_health = 160
        self.inventory = []
        self.position = (0, 0)
        self.score = 0
        self.gold = 0
        self.speed = 300
        self.displayed_speed = 100
        """================================= DAMAGE EFFECTS ================================="""
        self.damage_timer = 0
        self.highlight_duration = 0.7  # duration of red highlight over player
        self.knockback_speed = 1100
        self.knockback_timer = 0
        self.knockback_duration = 0.3
        self.knockback_direction = None
        """================================= ATTACK MECHANIC ================================="""
        self.dmg = 10
        self.attack_timer = 0
        self.attack_cooldown = 0.6
        self.attack_range = 120  # Range of the attack
        self.attack_angle = 90  # Angle of the attack arc (in degrees)

        """===================================== SOUNDS ======================================"""
        self.attack = self.sound_manager.sounds["attack"]

        self.footstep_sound = self.sound_manager.sounds["footstep_sound"]
        self.footstep_threshold = 64
        self.distance_moved = 0

        self.hit_sound = self.sound_manager.sounds["hit_sound"]

    def take_damage(self, damage_amount, enemy_hitbox):
        self.health = max(0, self.health - damage_amount)  # take damage
        self.damage_timer = time.time()  # start damage timer timer
        self.knockback_timer = self.knockback_duration
        #knockback direction
        if enemy_hitbox:
            self.knockback_direction = direction_between_rects(enemy_hitbox, self.hitbox)
        else:
            self.knockback_direction = Vector2(0, 0) #fallback

        self.is_hurt = True
        if self.health == 0:  
            self.state = playerState.DEAD  

    def heal(self, n):
        self.health = min(self.max_health, self.health + n)

    def update(self, room: Room):

        if self.state == playerState.DEAD:
            self.handle_death()

        if self.is_hurt:
            if time.time() - self.damage_timer > self.hurt_duration:
                self.is_hurt = False

        self.handle_attack(room.enemies)
        self.handle_movement()
        self.check_collisions(room)
        self.update_position()
        self.update_animation()

    def draw(self):
        
        source = self.current_animation.animation_frame_horizontal()
        origin = Vector2(0.0, 0.0)

        if self.state == playerState.DEAD:
            self.is_hurt = False #no longer "hurt"
            draw_texture_pro(self.death, source, self.rect, origin, 0.0, WHITE)
            return #player dead, exit
        else:
            # draw hurt animation
            color = WHITE
            if time.time() - self.damage_timer < self.highlight_duration:
                color = WHITE
            if self.attack_timer > 0:
                attack_source = self.animations[self.attack_state].animation_frame_horizontal()
                draw_texture_pro(self.sprite, attack_source, self.rect, origin, 0.0, WHITE)
            else:
                #draw sprite
                draw_texture_pro(self.sprite, source, self.rect, origin, 0.0, color)

            if hasattr(self, 'attacking') and self.attacking and self.attack_animation:
                attack_source = self.attack_animation.animation_frame_horizontal()



            # Draw hitboxes for debugging
            #draw_rectangle_lines_ex(self.hitbox, 1, RED)
            #draw_rectangle_lines_ex(self.rect, 1, RED)

    def handle_movement(self):
        if self.state == playerState.DEAD:
            return
        if self.state == playerState.HURT:
            return
        if self.knockback_timer > 0: #knockback logic (same as Enemy class)
            self.knockback_timer -= get_frame_time()
            ratio = (self.knockback_timer/self.knockback_duration) ** 2
            self.vel = vector2_scale(self.knockback_direction, ratio*self.knockback_speed)
            return #prevent normal movement when being knocked back
        self.vel.x = 0.0
        self.vel.y = 0.0
        diag_speed = self.speed * .707

        movement_keys = {  # dictionary of movements
            (KEY_A, KEY_W): (Vector2(-diag_speed, -diag_speed), playerState.WALKING_UP_LEFT, LEFT),  # top left
            (KEY_A, KEY_S): (Vector2(-diag_speed, diag_speed), playerState.WALKING_DOWN_LEFT, LEFT),  # bottom left
            (KEY_D, KEY_W): (Vector2(diag_speed, -diag_speed), playerState.WALKING_UP_RIGHT, RIGHT),  # top right
            (KEY_D, KEY_S): (Vector2(diag_speed, diag_speed), playerState.WALKING_DOWN_RIGHT, RIGHT),  # bottom right
            (KEY_A,): (Vector2(-self.speed, 0), playerState.WALKING_LEFT, LEFT),  # left
            (KEY_D,): (Vector2(self.speed, 0), playerState.WALKING_RIGHT, RIGHT),  # right
            (KEY_W,): (Vector2(0, -self.speed), playerState.WALKING_UP, UP),  # up
            (KEY_S,): (Vector2(0, self.speed), playerState.WALKING_DOWN, DOWN),  # down
        }

        for keys, (vel, state, direction) in movement_keys.items():  # for each key in movement keys
            if all(is_key_down(k) for k in keys):  # if all keys in a specific movement key are pressed, define the players velocity, state, and direction
                self.vel = vel
                self.state = state
                self.dir = direction
                break  # if condition is met break loop
        else:  # if condition wasn't met, player is idle (no key's pressed)
            self.state = playerState.IDLE
            self.distance_moved = self.footstep_threshold * .9

    def update_position(self):
        dx = self.vel.x * get_frame_time()
        dy = self.vel.y * get_frame_time()

        self.rect.x += dx
        self.rect.y += dy
        self.hitbox.x = self.rect.x + (self.rect.width - self.hitbox.width) / 2
        self.hitbox.y = self.rect.y + self.rect.height - self.hitbox.height - self.hitbox_offset

        self.distance_moved += vector2_length(Vector2(dx, dy))
        if self.distance_moved >= self.footstep_threshold:
            self.distance_moved = 0
            self.sound_manager.play_sound("footstep_sound")

    def update_animation(self):
        if self.is_hurt:
            self.current_animation = self.animations[playerState.HURT]
        else:
            self.current_animation = self.animations[self.state]
        self.current_animation.animation_update()

    def check_collisions(self, room: Room):
        check_obstacle_collisions(self, room.rectangles)
        if not time.time() - self.damage_timer < self.highlight_duration:
            check_enemy_collisions(self, room)

    def handle_death(self):
        # prevent movement
        self.vel.x, self.vel.y = 0.0, 0.0 

        self.state = playerState.DEAD
        self.current_animation = self.animations[self.state]

    """================================= ATTACK MECHANIC ================================="""

    def handle_attack(self, enemies):
        if self.state == playerState.DEAD:
            return

        if self.attack_timer > 0:
            self.animations[self.attack_state].animation_update()
            self.attack_timer -= get_frame_time()
            if self.attack_timer <= 0:
                self.animations[self.attack_state].reset()
            return


        if self.attack_timer >= 0:
            self.attack_timer -= get_frame_time()
        elif is_key_down(KEY_LEFT):
            self.attack_timer = self.attack_cooldown
            self.attack_state = playerState.ATTACK_LEFT
            self.perform_attack(enemies, 'W')
        elif is_key_down(KEY_RIGHT):
            self.attack_timer = self.attack_cooldown
            self.attack_state = playerState.ATTACK_RIGHT
            self.perform_attack(enemies, 'E')
        elif is_key_down(KEY_UP):
            self.attack_timer = self.attack_cooldown
            self.attack_state = playerState.ATTACK_UP
            self.perform_attack(enemies, 'N')
        elif is_key_down(KEY_DOWN):
            self.attack_timer = self.attack_cooldown
            self.attack_state = playerState.ATTACK_DOWN
            self.perform_attack(enemies, 'S')


    def perform_attack(self, enemies, dir):
        attack_rect = None

        
        if dir == 'N': 
            attack_rect = Rectangle(
                self.hitbox.x - self.attack_range/2 + self.hitbox.width/2,  
                self.hitbox.y - self.attack_range,  
                self.hitbox.width + self.attack_range,  
                self.attack_range  
            )
        elif dir == 'E':  
            attack_rect = Rectangle(
                self.hitbox.x + self.hitbox.width,  
                self.hitbox.y - self.attack_range/2 + self.hitbox.height/2,  
                self.attack_range,  
                self.hitbox.height + self.attack_range  
            )
        elif dir == 'S':  
            attack_rect = Rectangle(
                self.hitbox.x - self.attack_range/2 + self.hitbox.width/2,  
                self.hitbox.y + self.hitbox.height,  
                self.hitbox.width + self.attack_range,  
                self.attack_range  
            )
        elif dir == 'W': 
            attack_rect = Rectangle(
                self.hitbox.x - self.attack_range,  
                self.hitbox.y - self.attack_range/2 + self.hitbox.height/2,  
                self.attack_range,  
                self.hitbox.height + self.attack_range  
            )

        for enemy in enemies:
            if check_collision_recs(attack_rect, enemy.hitbox):
                self.sound_manager.play_sound("hit_sound")
                dir = direction_between_rects(self.hitbox, enemy.hitbox)
                enemy.take_damage(self.dmg, dir)

    def increase_health(self, amount):
        if self.max_health + amount <= self.absolute_health:
            self.max_health += amount
            self.health = min(self.health + 20, self.max_health)
            return True
        return False

    def increase_speed(self, amount):
        self.vel.x += amount
        self.vel.y += amount

    def increase_attack(self, amount):
        self.dmg += amount

    def get_score(self):
        return self.score
