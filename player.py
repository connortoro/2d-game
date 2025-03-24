from raylibpy import *
from enum import Enum
from animation import Animation, REPEATING, ONESHOT
from room import Room  # Import the Room class
import time
import math
from collisions import *

# Dimensions of space
W = 1300
H = 900

LEFT = -1
RIGHT = 1
UP = -2
DOWN = 2

class playerState(Enum):
    """PLAYER STATES"""
    IDLE = "IDLE"
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
    def __init__(self, texture):
        """================================= BASICS ================================="""
        sprite_width = 96.0 * 2.5
        sprite_height = 96.0 * 2.5
        self.rect = Rectangle(W / 2.0 - sprite_width / 2.0, H / 2.0 - sprite_height / 2.0, sprite_width, sprite_height)
        self.vel = Vector2(0.0, 0.0)
        self.sprite = texture
        self.dir = RIGHT  # right
        self.death = load_texture("assets/player_sheet/dead.png")
        self.sword = load_texture("assets/textures/sword.png")

        feet_width = 10.0 * 4  
        feet_height = 8.0 * 6  # Make collision box shorter, just for feet
        self.hitbox_offset = 50
        self.hitbox = Rectangle(
            self.rect.x + (self.rect.width - feet_width) / 2,  # Center horizontally
            self.rect.y + self.rect.height - feet_height - self.hitbox_offset,  # Position at bottom of sprite
            feet_width,
            feet_height
        )

        """================================= ANIMATIONS ================================="""
        self.animations = {
            playerState.IDLE: Animation(1, 5, 1, 0, 96, 0.1, 0.1, REPEATING, 96, 96),
            playerState.WALKING_UP: Animation(1, 5, 1, 1, 96, 0.1, 0.1, REPEATING, 96, 96),
            playerState.WALKING_DOWN: Animation(1, 5, 1, 1, 96, 0.1, 0.1, REPEATING, 96, 96),
            playerState.WALKING_RIGHT: Animation(1, 5, 1, 1, 96, 0.1, 0.1, REPEATING, 96, 96),
            playerState.WALKING_LEFT: Animation(1, 5, 1, 1, 96, 0.1, 0.1, REPEATING, 96, 96),
            playerState.WALKING_UP_LEFT: Animation(1, 5, 1, 1, 96, 0.1, 0.1, REPEATING, 96, 96),
            playerState.WALKING_UP_RIGHT: Animation(1, 5, 1, 1, 96, 0.1, 0.1, REPEATING, 96, 96),
            playerState.WALKING_DOWN_LEFT: Animation(1, 5, 1, 1, 96, 0.1, 0.1, REPEATING, 96, 96),
            playerState.WALKING_DOWN_RIGHT: Animation(1, 5, 1, 1, 96, 0.1, 0.1, REPEATING, 96, 96),
            playerState.DEAD: Animation(0, 6, 0, 0, 16, 0.1, 0.1, ONESHOT, 64, 64),
            playerState.ATTACK_RIGHT: Animation(1, 5, 1, 2, 96, 0.1, 0.1, ONESHOT, 96, 96),
            playerState.ATTACK_LEFT: Animation(1, 5, 1, 2, 96, 0.1, 0.1, ONESHOT, 96, 96, True),
            playerState.ATTACK_UP: Animation(1, 5, 1, 6, 96, 0.1, 0.1, ONESHOT, 96, 96),
            playerState.ATTACK_DOWN: Animation(1, 5, 1, 4, 96, 0.1, 0.1, ONESHOT, 96, 96),
        }

        self.state = playerState.IDLE  # default state
        self.attack_state = playerState.ATTACK_RIGHT
        self.current_animation = self.animations[self.state]  # default animation

        """================================= PLAYER STATS ================================="""
        self.health = 100
        self.max_health = 100
        self.coins = 0
        self.inventory = []
        self.position = (0, 0)

        """================================= DAMAGE EFFECTS ================================="""
        self.damage_timer = 0
        self.highlight_duration = 0.7  # duration of red highlight over player

        """================================= ATTACK MECHANIC ================================="""
        self.dmg = 10
        self.attack_timer = 0
        self.attack_cooldown = 0.6
        self.attack_range = 150  # Range of the attack
        self.attack_angle = 90  # Angle of the attack arc (in degrees)

    def take_damage(self, damage_amount):
        self.health = max(0, self.health - damage_amount)  # take damage
        self.damage_timer = time.time()  # start timer
        if self.health == 0:  # player died
            self.state = playerState.DEAD  # set player state to dead

    def update(self, room: Room):

        if self.state == playerState.DEAD:
            self.handle_death()

        self.handle_attack(room.enemies)
        self.handle_movement()
        self.check_collisions(room)
        self.update_position()
        self.update_animation()

    def draw(self):
        # Get the movement animation source
        source = self.current_animation.animation_frame_horizontal()
        origin = Vector2(0.0, 0.0)

        if self.state == playerState.DEAD:
            death_rect = Rectangle(self.rect.x, self.rect.y, 64.0 * 2, 64.0 * 2)
            draw_texture_pro(self.death, source, death_rect, origin, 0.0, WHITE)
            return #player dead, exit
        else:
            # draw hurt animation
            color = WHITE
            if time.time() - self.damage_timer < self.highlight_duration:
                color = RED
            if self.attack_timer > 0:
                attack_source = self.animations[self.attack_state].animation_frame_horizontal()
                draw_texture_pro(self.sprite, attack_source, self.rect, origin, 0.0, color)
            else:
                #draw animations if going left
                if self.dir == LEFT:
                    source.width = source.width * self.dir
                    draw_texture_pro(self.sprite, source, self.rect, origin, 0.0, color)
                else:
                    draw_texture_pro(self.sprite, source, self.rect, origin, 0.0, color)

            # If attacking, draw the attack animation on top
            if hasattr(self, 'attacking') and self.attacking and self.attack_animation:
                attack_source = self.attack_animation.animation_frame_horizontal()
                
                # Flip attack animation if facing left
                

            # Draw hitboxes for debugging
            draw_rectangle_lines_ex(self.hitbox, 1, RED)
            #draw_rectangle_lines_ex(self.rect, 1, RED)

    def handle_movement(self):
        if self.state == playerState.DEAD:
            return
        self.vel.x = 0.0
        self.vel.y = 0.0
        speed = 300.0 if is_key_down(KEY_LEFT_SHIFT) else 200.0  # defines speed, increases if shift is pressed

        movement_keys = {  # dictionary of movements
            (KEY_A, KEY_W): (Vector2(-speed, -speed), playerState.WALKING_UP_LEFT, LEFT),  # top left
            (KEY_A, KEY_S): (Vector2(-speed, speed), playerState.WALKING_DOWN_LEFT, LEFT),  # bottom left
            (KEY_D, KEY_W): (Vector2(speed, -speed), playerState.WALKING_UP_RIGHT, RIGHT),  # top right
            (KEY_D, KEY_S): (Vector2(speed, speed), playerState.WALKING_DOWN_RIGHT, RIGHT),  # bottom right
            (KEY_A,): (Vector2(-speed, 0), playerState.WALKING_LEFT, LEFT),  # left
            (KEY_D,): (Vector2(speed, 0), playerState.WALKING_RIGHT, RIGHT),  # right
            (KEY_W,): (Vector2(0, -speed), playerState.WALKING_UP, UP),  # up
            (KEY_S,): (Vector2(0, speed), playerState.WALKING_DOWN, DOWN),  # down
        }

        for keys, (vel, state, direction) in movement_keys.items():  # for each key in movement keys
            if all(is_key_down(k) for k in keys):  # if all keys in a specific movement key are pressed, define the players velocity, state, and direction
                self.vel = vel
                self.state = state
                self.dir = direction
                break  # if condition is met break loop
        else:  # if condition wasn't met, player is idle (no key's pressed)
            self.state = playerState.IDLE

    def update_position(self):
        self.rect.x += self.vel.x * get_frame_time()
        self.rect.y += self.vel.y * get_frame_time()
        self.hitbox.x = self.rect.x + (self.rect.width - self.hitbox.width) / 2
        self.hitbox.y = self.rect.y + self.rect.height - self.hitbox.height - self.hitbox_offset - 30

    def update_animation(self):
        self.current_animation = self.animations[self.state]
        self.current_animation.animation_update()

    def check_collisions(self, room: Room):
        check_obstacle_collisions(self, room.rectangles)
        if not time.time() - self.damage_timer < self.highlight_duration:
            check_enemy_collisions(self, room)

    def handle_death(self):
        # prevent movement
        self.vel.x, self.vel.y = 0.0, 0.0  # Stop movement

        #change state to dead
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

        # Handle attack initiation
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
        
        # Create attack rectangle based on direction
        if dir == 'N':  # North/Up
            attack_rect = Rectangle(
                self.hitbox.x - self.attack_range/2 + self.hitbox.width/2,  # Centered horizontally
                self.hitbox.y - self.attack_range,  # Above the player
                self.hitbox.width + self.attack_range,  # Wider than player
                self.attack_range  # Height = attack range
            )
        elif dir == 'E':  # East/Right
            attack_rect = Rectangle(
                self.hitbox.x + self.hitbox.width,  # Right of player
                self.hitbox.y - self.attack_range/2 + self.hitbox.height/2,  # Centered vertically
                self.attack_range,  # Width = attack range
                self.hitbox.height + self.attack_range  # Taller than player
            )
        elif dir == 'S':  # South/Down
            attack_rect = Rectangle(
                self.hitbox.x - self.attack_range/2 + self.hitbox.width/2,  # Centered horizontally
                self.hitbox.y + self.hitbox.height,  # Below the player
                self.hitbox.width + self.attack_range,  # Wider than player
                self.attack_range  # Height = attack range
            )
        elif dir == 'W':  # West/Left
            attack_rect = Rectangle(
                self.hitbox.x - self.attack_range,  # Left of player
                self.hitbox.y - self.attack_range/2 + self.hitbox.height/2,  # Centered vertically 
                self.attack_range,  # Width = attack range
                self.hitbox.height + self.attack_range  # Taller than player
            )
        
        # Debug: Uncomment to see attack hitbox
        draw_rectangle_lines_ex(attack_rect, 1, BLUE)
        
        # Check for collisions with enemies and apply damage
        if attack_rect:
            for enemy in enemies:
                if check_collision_recs(attack_rect, enemy.hitbox):
                    enemy.health -= self.dmg
                    # Optional: Add hit effect or animation
                    enemy.damage_timer = time.time()  # If enemy has a damage timer like player