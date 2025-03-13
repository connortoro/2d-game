from raylibpy import *
from enum import Enum
from animation import Animation, REPEATING, ONESHOT
from room import Room  # Import the Room class
import time
import math
from collisions import check_collision_recs, Vector2Normalize  # Import the custom collision function

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
        self.knockback_vel = Vector2(0.0, 0.0)  # Add knockback velocity
        self.sprite = texture
        self.dir = RIGHT  # right
        self.death = load_texture("assets/player_sheet/dead.png")

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
        self.reticle_angle = 0  # Angle of the reticle (in radians)
        self.attack_range = 150  # Range of the attack
        self.attack_angle = 90  # Angle of the attack arc (in degrees)
        self.reticle_distance = 60  # Distance of the reticle from the player
        self.reticle_color = Color(255, 0, 0, 150)  # Semi-transparent red

    def take_damage(self, damage_amount, damage_direction: Vector2):
        """Apply damage and knockback to the player."""
        self.health = max(0, self.health - damage_amount)  # Take damage
        self.damage_timer = time.time()  # Start timer

        # Apply knockback in the opposite direction of the damage source
        knockback_strength = 2000.0  # Adjust this value to control the distance of knockback
        self.knockback_vel = Vector2(-damage_direction.x * knockback_strength, -damage_direction.y * knockback_strength)

        if self.health == 0:  # Player died
            self.state = playerState.DEAD  # Set player state to dead

    def update(self, room: Room):
        if self.state == playerState.DEAD:
            self.update_animation()  # Run death animation
            return  # Stop updating, player dead
        self.move()
        self.check_collisions(room)
        self.update_position()
        self.update_animation()
        self.update_reticle()

        # Check for attack input (left mouse button)
        if is_mouse_button_pressed(MOUSE_LEFT_BUTTON):
            self.perform_attack(room.enemies)

    def draw(self):
        # Checks if player is dead
        if self.state == playerState.DEAD:
            death_rect = Rectangle(self.rect.x, self.rect.y, 64.0 * 2, 64.0 * 2)
            source = self.current_animation.animation_frame_horizontal()
            origin = Vector2(0.0, 0.0)

            draw_texture_pro(self.death, source, death_rect, origin, 0.0, WHITE)

        else:  # Not dead
            source = self.current_animation.animation_frame_vertical()  # Get current frame
            origin = Vector2(0.0, 0.0)

            # Check if player is damaged
            if time.time() - self.damage_timer < self.highlight_duration:
                draw_texture_pro(self.sprite, source, self.rect, origin, 0.0, GRAY)
            else:
                draw_texture_pro(self.sprite, source, self.rect, origin, 0.0, WHITE)

            # DEBUG
            #draw_rectangle_lines_ex(self.hitbox, 1, RED)

        # Draw reticle
        self.draw_reticle()

        # Draw attack arc
        #self.draw_attack_arc()

    def move(self):
        if self.state == playerState.DEAD:
            return  # Prevent movement when dead

        self.vel.x = 0.0
        self.vel.y = 0.0

        speed = 300.0 if is_key_down(KEY_LEFT_SHIFT) else 200.0  # Defines speed, increases if shift is pressed

        movement_keys = {  # Dictionary of movements
            (KEY_A, KEY_W): (Vector2(-speed, -speed), playerState.WALKING_UP_LEFT, LEFT),  # Top left
            (KEY_A, KEY_S): (Vector2(-speed, speed), playerState.WALKING_DOWN_LEFT, LEFT),  # Bottom left
            (KEY_D, KEY_W): (Vector2(speed, -speed), playerState.WALKING_UP_RIGHT, RIGHT),  # Top right
            (KEY_D, KEY_S): (Vector2(speed, speed), playerState.WALKING_DOWN_RIGHT, RIGHT),  # Bottom right
            (KEY_A,): (Vector2(-speed, 0), playerState.WALKING_LEFT, LEFT),  # Left
            (KEY_D,): (Vector2(speed, 0), playerState.WALKING_RIGHT, RIGHT),  # Right
            (KEY_W,): (Vector2(0, -speed), playerState.WALKING_UP, UP),  # Up
            (KEY_S,): (Vector2(0, speed), playerState.WALKING_DOWN, DOWN),  # Down
        }

        for keys, (vel, state, direction) in movement_keys.items():  # For each key in movement keys
            if all(is_key_down(k) for k in keys):  # If all keys in a specific movement key are pressed, define the players velocity, state, and direction
                self.vel = vel
                self.state = state
                self.dir = direction
                break  # If condition is met break loop
        else:  # If condition wasn't met, player is idle (no key's pressed)
            self.state = playerState.IDLE

    def update_position(self):
        """Update player position, including knockback."""
        # Combine movement and knockback velocities
        total_vel = Vector2(self.vel.x + self.knockback_vel.x, self.vel.y + self.knockback_vel.y)

        # Update position based on total velocity
        self.rect.x += total_vel.x * get_frame_time()
        self.rect.y += total_vel.y * get_frame_time()

        # Gradually reduce knockback velocity (simulate decay)
        self.knockback_vel.x *= 0.9  # Adjust this value to control how quickly the knockback decays
        self.knockback_vel.y *= 0.9

        # Stop knockback if it becomes too small
        if abs(self.knockback_vel.x) < 1.0:
            self.knockback_vel.x = 0.0
        if abs(self.knockback_vel.y) < 1.0:
            self.knockback_vel.y = 0.0

        # Update hitbox position
        self.hitbox.x = self.rect.x + (self.rect.width - self.hitbox.width) / 2
        self.hitbox.y = self.rect.y + self.rect.height - self.hitbox.height

    def update_animation(self):
        self.current_animation = self.animations[self.state]
        self.current_animation.animation_update()

    def check_collisions(self, room: Room):
        """Check collisions with obstacles and enemies."""
        # Check collisions with obstacles (terrain)
        for obstacle in room.rectangles:
            if check_collision_recs(self.hitbox, obstacle):
                # Calculate centers
                player_center = Vector2(self.hitbox.x + self.hitbox.width / 2, self.hitbox.y + self.hitbox.height / 2)
                obstacle_center = Vector2(obstacle.x + obstacle.width / 2, obstacle.y + obstacle.height / 2)

                # Vector from obstacle center to player center
                direction = Vector2(player_center.x - obstacle_center.x, player_center.y - obstacle_center.y)

                # Half sizes of each rectangle
                player_half_size = Vector2(self.hitbox.width / 2, self.hitbox.height / 2)
                obstacle_half_size = Vector2(obstacle.width / 2, obstacle.height / 2)

                # Calculate overlap on each axis
                overlap_x = player_half_size.x + obstacle_half_size.x - abs(direction.x)
                overlap_y = player_half_size.y + obstacle_half_size.y - abs(direction.y)

                # Add a small buffer to prevent getting stuck
                buffer = 1.0

                # Resolve collision based on smallest overlap
                if overlap_x < overlap_y:
                    if direction.x > 0:  # player to right of obstacle
                        self.rect.x += overlap_x + buffer
                    else:  # player to left of obstacle
                        self.rect.x -= overlap_x + buffer
                    self.vel.x = 0  # Stop horizontal movement
                else:
                    if direction.y > 0:  # player above obstacle
                        self.rect.y += overlap_y + buffer
                    else:  # player below obstacle
                        self.rect.y -= overlap_y + buffer
                    self.vel.y = 0  # Stop vertical movement

                # Update hitbox position immediately
                self.hitbox.x = self.rect.x + (self.rect.width - self.hitbox.width) / 2
                self.hitbox.y = self.rect.y + self.rect.height - self.hitbox.height

        # Check collisions with enemies (if not recently damaged)
        if not time.time() - self.damage_timer < self.highlight_duration:
            for enemy in room.enemies:
                if check_collision_recs(self.hitbox, enemy.hitbox):
                    # Calculate damage direction (from enemy to player)
                    damage_direction = Vector2(self.rect.x - enemy.rect.x, self.rect.y - enemy.rect.y)
                    damage_direction = Vector2Normalize(-damage_direction)  # Knockback direction when hit

                    # Apply damage to the player
                    self.take_damage(10, damage_direction)  # Pass both damage_amount and damage_direction
    """================================= ATTACK MECHANIC ================================="""

    def update_reticle(self):
        # Update reticle angle based on mouse position
        mouse_pos = get_mouse_position()
        dx = mouse_pos.x - (self.rect.x + self.rect.width / 2)
        dy = mouse_pos.y - (self.rect.y + self.rect.height / 2)
        self.reticle_angle = math.atan2(dy, dx)

    def draw_reticle(self):
        # Calculate the position of the reticle
        reticle_pos = Vector2(
            self.rect.x + self.rect.width / 2 + math.cos(self.reticle_angle) * self.reticle_distance,
            self.rect.y + self.rect.height / 2 + math.sin(self.reticle_angle) * self.reticle_distance
        )

        # Define the triangle points (relative to the reticle position)
        size = 10  # Size of the triangle
        point1 = Vector2(size, 0)  # Tip of the triangle
        point2 = Vector2(-size, -size)  # Bottom-left corner
        point3 = Vector2(-size, size)  # Bottom-right corner

        # Rotate the triangle points around the reticle position
        angle = self.reticle_angle  # Angle in radians
        rotated_point1 = Vector2(
            reticle_pos.x + point1.x * math.cos(angle) - point1.y * math.sin(angle),
            reticle_pos.y + point1.x * math.sin(angle) + point1.y * math.cos(angle)
        )
        rotated_point2 = Vector2(
            reticle_pos.x + point2.x * math.cos(angle) - point2.y * math.sin(angle),
            reticle_pos.y + point2.x * math.sin(angle) + point2.y * math.cos(angle)
        )
        rotated_point3 = Vector2(
            reticle_pos.x + point3.x * math.cos(angle) - point3.y * math.sin(angle),
            reticle_pos.y + point3.x * math.sin(angle) + point3.y * math.cos(angle)
        )

        # Draw the rotated triangle
        draw_triangle(rotated_point1, rotated_point2, rotated_point3, self.reticle_color)

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