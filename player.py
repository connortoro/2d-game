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

        feet_width = 10.0 * 4  # Make collision box narrower than visual sprite
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
            playerState.ATTACK_UP: Animation(1, 5, 1, 6, 96, 0.1, 0.1, ONESHOT, 96, 96),
            playerState.ATTACK_DOWN: Animation(1, 5, 1, 4, 96, 0.1, 0.1, ONESHOT, 96, 96),
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
            self.handle_death()
        # Handle attack first
        self.handle_attack(room.enemies)
        
        # Only handle movement if not in an attack animation
        if not hasattr(self, 'is_attacking') or not self.is_attacking:
            self.handle_movement()
        else:
            # We're in an attack animation but can still move
            # Keep the attack state but apply movement
            self.vel.x = 0.0
            self.vel.y = 0.0
            
            speed = 300.0 if is_key_down(KEY_LEFT_SHIFT) else 200.0
            
            # Apply velocity without changing state
            if is_key_down(KEY_A):
                self.vel.x = -speed
                self.dir = LEFT
            if is_key_down(KEY_D):
                self.vel.x = speed
                self.dir = RIGHT
            if is_key_down(KEY_W):
                self.vel.y = -speed
            if is_key_down(KEY_S):
                self.vel.y = speed
                
            # Normalize diagonal movement
            if self.vel.x != 0 and self.vel.y != 0:
                # Normalize to maintain consistent speed in diagonal movement
                length = math.sqrt(self.vel.x * self.vel.x + self.vel.y * self.vel.y)
                self.vel.x = (self.vel.x / length) * speed
                self.vel.y = (self.vel.y / length) * speed

        # update player's position based on velocity
        self.position += self.vel * get_frame_time()

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
            if time.time() - self.damage_timer < self.highlight_duration:
                draw_texture_pro(self.sprite, source, self.rect, origin, 0.0, RED)
            else:
                #draw animations if going left
                if self.dir == LEFT:
                    source.width = source.width * self.dir
                    draw_texture_pro(self.sprite, source, self.rect, origin, 0.0, WHITE)
                else:
                    draw_texture_pro(self.sprite, source, self.rect, origin, 0.0, WHITE)

            # If attacking, draw the attack animation on top
            if hasattr(self, 'attacking') and self.attacking and self.attack_animation:
                attack_source = self.attack_animation.animation_frame_horizontal()
                
                # Flip attack animation if facing left
                if self.dir == LEFT:
                    attack_source.width = attack_source.width * self.dir
                
                draw_texture_pro(self.sprite, attack_source, self.rect, origin, 0.0, WHITE)

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
        self.hitbox.y = self.rect.y + self.rect.height - self.hitbox.height - self.hitbox_offset

    def update_animation(self):
        self.current_animation = self.animations[self.state]
        self.current_animation.animation_update()

    def check_collisions(self, room: Room):
        check_obstacle_collisions(self, room.rectangles)
        if not time.time() - self.damage_timer < self.highlight_duration:
            check_enemy_collisions(self, room.enemies)

    def handle_death(self):
        # prevent movement
        self.vel.x, self.vel.y = 0.0, 0.0  # Stop movement

        #change state to dead
        self.state = playerState.DEAD
        self.current_animation = self.animations[self.state]

    """================================= ATTACK MECHANIC ================================="""

    def handle_attack(self, enemies):
        # Do not allow attack if the current state is dead
        if self.state == playerState.DEAD:
            return

        # Check if we're currently in an attack animation
        if hasattr(self, 'is_attacking') and self.is_attacking:
            # Check if the attack animation has completed
            if self.current_animation.is_complete():
                self.is_attacking = False

        # Handle attack initiation
        if self.attack_timer > 0:
            self.attack_timer -= get_frame_time()
        elif is_mouse_button_pressed(MOUSE_LEFT_BUTTON) and self.attack_timer <= 0:
            self.perform_attack(enemies)

            # Set the attack state and animation, but remember the previous state
            self.previous_state = self.state

            # Get the mouse position
            mouse_pos = get_mouse_position()
            
            # Calculate the angle from the player to the mouse
            player_center_x = self.rect.x + self.rect.width / 2
            player_center_y = self.rect.y + self.rect.height / 2
            dx = mouse_pos.x - player_center_x
            dy = mouse_pos.y - player_center_y
            angle = math.degrees(math.atan2(dy, dx))  # Angle between player and mouse in degrees

            # Normalize the angle to a range [0, 360]
            if angle < 0:
                angle += 360

            # Determine attack direction based on the angle
            if 45 <= angle < 135:
                self.state = playerState.ATTACK_DOWN
                self.dir = DOWN
            elif 135 <= angle < 225:
                self.state = playerState.ATTACK_RIGHT
                self.dir = LEFT
            elif 225 <= angle < 315:
                self.state = playerState.ATTACK_UP
                self.dir = UP
            else:
                self.state = playerState.ATTACK_RIGHT
                self.dir = RIGHT

            # Update the animation and reset it
            self.current_animation = self.animations[self.state]
            self.current_animation.reset()

            # Mark that we're in an attack animation
            self.is_attacking = True
            self.attack_timer = self.attack_cooldown


    def perform_attack(self, enemies):
        # Get player's center position
        player_center_x = self.rect.x + self.rect.width / 2
        player_center_y = self.rect.y + self.rect.height / 2
        
        # Define the attack direction based on player's current direction
        direction_angles = {
            RIGHT: 0,      # Right = 0 degrees
            LEFT: 180,     # Left = 180 degrees
            UP: 270,       # Up = 270 degrees
            DOWN: 90       # Down = 90 degrees
        }
        
        # Get the center angle for the attack based on player direction
        facing_angle = direction_angles.get(self.dir, 0)
        
        # Define the attack arc (half of the total angle)
        attack_arc = self.attack_angle / 2
        
        # Check which enemies are within the attack arc
        for enemy in enemies:
            # Calculate the center position of the enemy
            enemy_center_x = enemy.rect.x + enemy.rect.width / 2
            enemy_center_y = enemy.rect.y + enemy.rect.height / 2
            
            # Calculate the vector from the player to the enemy
            dx = enemy_center_x - player_center_x
            dy = enemy_center_y - player_center_y
            distance = math.hypot(dx, dy)
            
            # If enemy is within attack range
            if distance <= self.attack_range:
                # Calculate angle between player and enemy (in degrees)
                angle_to_enemy = math.degrees(math.atan2(dy, dx))
                if angle_to_enemy < 0:
                    angle_to_enemy += 360  # Convert negative angles to 0-360 range
                
                # Check if the enemy is within the attack arc
                angle_diff = abs((angle_to_enemy - facing_angle + 180) % 360 - 180)
                if angle_diff <= attack_arc:
                    # Enemy is within the attack arc and range
                    self.damage_enemy(enemy)

            
    def damage_enemy(self, enemy):
        # Enemy is within the attack arc and range
        if hasattr(enemy, 'health'):  # Check if the enemy has a health attribute
            enemy.health -= 10  # Apply damage (you can adjust the damage value later)