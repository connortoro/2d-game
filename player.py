from raylibpy import *
from enum import Enum
from animation import Animation, REPEATING, ONESHOT
from room import Room  # Import the Room class
import time
import math
from collisions import *

# Dimensions of space
W = 1300
H = 800

LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3

class playerState(Enum):
    """PLAYER STATES"""
    IDLE = "IDLE"
    DEAD = "DEAD"

    """WALKING STATES"""
    WALKING_UP = "WALKING_UP"
    WALKING_DOWN = "WALKING_DOWN"
    WALKING_LEFT = "WALKING_LEFT"
    WALKING_RIGHT = "WALKING_RIGHT"
    WALKING_UP_LEFT = "WALKING_UP_LEFT"
    WALKING_UP_RIGHT = "WALKING_UP_RIGHT"
    WALKING_DOWN_LEFT = "WALKING_DOWN_LEFT"
    WALKING_DOWN_RIGHT = "WALKING_DOWN_RIGHT"

class Player:
    def __init__(self, texture):
        """================================= BASICS ================================="""
        self.rect = Rectangle(W / 2.0, H / 2.0, 16.0 * 4, 24.0 * 4)  # * 4 to increase size of sprite
        self.vel = Vector2(0.0, 0.0)
        self.sprite = texture
        self.dir = RIGHT  # right
        self.death = load_texture("assets/player_sheet/dead.png")
        self.sword = load_texture("assets/textures/sword.png")

        feet_width = 10.0 * 3  # Make collision box narrower than visual sprite
        feet_height = 8.0 * 3  # Make collision box shorter, just for feet
        self.hitbox = Rectangle(
            self.rect.x + (self.rect.width - feet_width) / 2,  # Center horizontally
            self.rect.y + self.rect.height - feet_height,  # Position at bottom of sprite
            feet_width,
            feet_height
        )

        """================================= ANIMATIONS ================================="""
        self.animations = {
            playerState.IDLE: Animation(1, 3, 1, 8, 0.2, 0.2, REPEATING, 16, 24),
            playerState.WALKING_UP: Animation(1, 3, 1, 0, 0.1, 0.1, REPEATING, 16, 24),
            playerState.WALKING_DOWN: Animation(1, 3, 1, 4, 0.1, 0.1, REPEATING, 16, 24),
            playerState.WALKING_RIGHT: Animation(1, 3, 1, 2, 0.1, 0.1, REPEATING, 16, 24),
            playerState.WALKING_LEFT: Animation(1, 3, 1, 6, 0.1, 0.1, REPEATING, 16, 24),
            playerState.WALKING_UP_LEFT: Animation(1, 3, 1, 7, 0.1, 0.1, REPEATING, 16, 24),
            playerState.WALKING_UP_RIGHT: Animation(1, 3, 1, 1, 0.1, 0.1, REPEATING, 16, 24),
            playerState.WALKING_DOWN_LEFT: Animation(1, 3, 1, 5, 0.1, 0.1, REPEATING, 16, 24),
            playerState.WALKING_DOWN_RIGHT: Animation(1, 3, 1, 3, 0.1, 0.1, REPEATING, 16, 24),
            playerState.DEAD: Animation(0, 6, 0, 0, 0.1, 0.1, ONESHOT, 64, 64),
        }

        self.state = playerState.IDLE  # default state
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
        self.attack_timer = 0
        self.attack_cooldown = 0.6
        self.reticle_angle = 0  # Angle of the reticle (in radians)
        self.attack_range = 150  # Range of the attack
        self.attack_angle = 90  # Angle of the attack arc (in degrees)
        self.reticle_distance = 60  # Distance of the reticle from the player
        self.reticle_color = Color(255, 0, 0, 150)  # Semi-transparent red

    def take_damage(self, damage_amount):
        self.health = max(0, self.health - damage_amount)  # take damage
        self.damage_timer = time.time()  # start timer
        if self.health == 0:  # player died
            self.state = playerState.DEAD  # set player state to dead

    def update(self, room: Room):
        if self.state == playerState.DEAD:
            self.update_animation()  # run death animation
            return  # stop updating, player dead
        self.move()
        self.check_collisions(room)
        self.update_position()
        self.update_animation()
        self.update_reticle()

        # Check for attack input (left mouse button)
        if self.attack_timer > 0:
            self.attack_timer -= get_frame_time()
        elif is_mouse_button_pressed(MOUSE_LEFT_BUTTON):
            self.perform_attack(room.enemies)
            self.attack_timer = self.attack_cooldown

    def draw(self):
        # checks if player is dead
        if self.state == playerState.DEAD:
            death_rect = Rectangle(self.rect.x, self.rect.y, 64.0 * 2, 64.0 * 2)
            source = self.current_animation.animation_frame_horizontal()
            origin = Vector2(0.0, 0.0)
            draw_texture_pro(self.death, source, death_rect, origin, 0.0, WHITE)

        else:  # not dead
            source = self.current_animation.animation_frame_vertical() 
            origin = Vector2(0.0, 0.0)
            # check if player is damaged
            if time.time() - self.damage_timer < self.highlight_duration:
                draw_texture_pro(self.sprite, source, self.rect, origin, 0.0, GRAY)
            else:
                draw_texture_pro(self.sprite, source, self.rect, origin, 0.0, WHITE)
            #draw_rectangle_lines_ex(self.hitbox, 1, RED)
        self.draw_reticle()
        #self.draw_attack_arc()
        if self.attack_timer > .3:
            self.draw_sword()

    def move(self):
        if self.state == playerState.DEAD:
            return  # prevent movement when dead

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
        self.hitbox.y = self.rect.y + self.rect.height - self.hitbox.height

    def update_animation(self):
        self.current_animation = self.animations[self.state]
        self.current_animation.animation_update()

    def check_collisions(self, room: Room):
        check_obstacle_collisions(self, room.rectangles)
        if not time.time() - self.damage_timer < self.highlight_duration:
            check_enemy_collisions(self, room.enemies)

    """================================= ATTACK MECHANIC ================================="""

    def draw_sword(self):
        mouse_pos = get_mouse_position()
        dx = mouse_pos.x - (self.rect.x + self.rect.width / 2)
        dy = mouse_pos.y - (self.rect.y + self.rect.height / 2)
        vec = (vector2_scale(vector2_normalize(Vector2(dx, dy)), 20))
        
        source = Rectangle(0, 0, 160, 160)
        dest = Rectangle(vec.x + self.rect.x + 32, vec.y + self.rect.y + 48, 50, 50)
        
        origin = Vector2(10, 40)
        angle = math.atan2(dy, dx) * 180 / math.pi + 160
        dt = ((.7 - self.attack_timer) / .4) * 160
        angle -= dt

        draw_texture_pro(self.sword, source, dest, origin, angle, WHITE)

    def update_reticle(self):
        # Update reticle angle based on mouse position
        mouse_pos = get_mouse_position()
        dx = mouse_pos.x - (self.rect.x + self.rect.width / 2)
        dy = mouse_pos.y - (self.rect.y + self.rect.height / 2)
        self.reticle_angle = math.atan2(dy, dx)

    def draw_reticle(self):
        # Draw reticle (triangle) at the calculated position
        reticle_pos = Vector2(
            self.rect.x + self.rect.width / 2 + math.cos(self.reticle_angle) * self.reticle_distance,
            self.rect.y + self.rect.height / 2 + math.sin(self.reticle_angle) * self.reticle_distance
        )
        draw_triangle(
            Vector2(reticle_pos.x + 10, reticle_pos.y),
            Vector2(reticle_pos.x - 10, reticle_pos.y - 10),
            Vector2(reticle_pos.x - 10, reticle_pos.y + 10),
            self.reticle_color  # Use semi-transparent color
        )

    def draw_attack_arc(self):
        # Define the arc's start and end angles
        start_angle = self.reticle_angle - math.radians(self.attack_angle / 2)
        end_angle = self.reticle_angle + math.radians(self.attack_angle / 2)

        # Draw a rectangle to represent the attack range
        draw_rectangle(
            int(self.rect.x + self.rect.width / 2 - self.attack_range),  # Top-left x
            int(self.rect.y + self.rect.height / 2 - self.attack_range),  # Top-left y
            int(self.attack_range * 2),  # Width
            int(self.attack_range * 2),  # Height
            Color(255, 0, 0, 50)  # Semi-transparent red
        )

        # Draw lines to represent the attack arc
        center = Vector2(self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height / 2)
        start_pos = Vector2(
            center.x + math.cos(start_angle) * self.attack_range,
            center.y + math.sin(start_angle) * self.attack_range
        )
        end_pos = Vector2(
            center.x + math.cos(end_angle) * self.attack_range,
            center.y + math.sin(end_angle) * self.attack_range
        )

        # Draw the lines
        draw_line_v(center, start_pos, RED)
        draw_line_v(center, end_pos, RED)

    def perform_attack(self, enemies):
        # Check which enemies are within the attack arc
        for enemy in enemies:
            # Calculate the center position of the enemy
            enemy_center = Vector2(
                enemy.rect.x + enemy.rect.width / 2,
                enemy.rect.y + enemy.rect.height / 2
            )

            # Calculate the vector from the player to the enemy
            dx = enemy_center.x - (self.rect.x + self.rect.width / 2)
            dy = enemy_center.y - (self.rect.y + self.rect.height / 2)
            distance = math.hypot(dx, dy)

            if distance > self.attack_range:
                continue  # Enemy is out of range

            # Calculate angle between player and enemy
            enemy_angle = math.degrees(math.atan2(dy, dx))
            reticle_angle_deg = math.degrees(self.reticle_angle)

            # Normalize angles to handle wrapping around 360 degrees
            angle_diff = abs((enemy_angle - reticle_angle_deg + 180) % 360 - 180)
            if angle_diff <= self.attack_angle / 2:
                # Enemy is within the attack arc and range
                if hasattr(enemy, 'health'):  # Check if the enemy has a health attribute
                    enemy.health -= 10  # Apply damage (you can adjust the damage value later)