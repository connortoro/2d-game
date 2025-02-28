from raylibpy import *
from enum import Enum
from animation import Animation, REPEATING, ONESHOT
from room import Room
import time

#dimensions of space
W = 1300
H = 800

LEFT = 0
RIGHT = 1
UP = 2
DOWN = 3

class playerState(Enum):
    IDLE = "IDLE"
    WALKING_UP = "WALKING_UP"
    WALKING_DOWN = "WALKING_DOWN"
    WALKING_LEFT = "WALKING_LEFT"
    WALKING_RIGHT = "WALKING_RIGHT"
    WALKING_UP_LEFT = "WALKING_UP_LEFT"
    WALKING_UP_RIGHT = "WALKING_UP_RIGHT"
    WALKING_DOWN_LEFT = "WALKING_DOWN_LEFT"
    WALKING_DOWN_RIGHT = "WALKING_DOWN_RIGHT"

#CURRENT PIXEL SIZE FOR 8D_CHARACTER 16X24

class Player:
    def __init__(self, texture):
        self.rect = Rectangle(W / 2.0, H / 2.0, 16.0 * 4.5, 24.0 * 4.5) # * 3 to increase size of sprite
        self.vel = Vector2(0.0, 0.0)
        self.sprite = texture
        self.dir = RIGHT #right

        feet_width = 10.0 * 3  # Make collision box narrower than visual sprite
        feet_height = 8.0 * 3  # Make collision box shorter, just for feet
        self.hitbox = Rectangle(
            self.rect.x + (self.rect.width - feet_width) / 2,  # Center horizontally
            self.rect.y + self.rect.height - feet_height,      # Position at bottom of sprite
            feet_width,
            feet_height
        )

        """================================= ANIMATIONS ================================="""
        self.animations = {
            playerState.IDLE: Animation(1, 3, 1, 8, 0.2, 0.2, REPEATING),
            playerState.WALKING_UP: Animation(1, 3, 1, 0, 0.1, 0.1, REPEATING),
            playerState.WALKING_DOWN: Animation(1, 3, 1, 4, 0.1, 0.1, REPEATING),
            playerState.WALKING_RIGHT: Animation(1, 3, 1, 2, 0.1, 0.1, REPEATING),
            playerState.WALKING_LEFT: Animation(1, 3, 1, 6, 0.1, 0.1, REPEATING),
            playerState.WALKING_UP_LEFT: Animation(1, 3, 1, 7, 0.1, 0.1, REPEATING),
            playerState.WALKING_UP_RIGHT: Animation(1, 3, 1, 1, 0.1, 0.1, REPEATING),
            playerState.WALKING_DOWN_LEFT: Animation(1, 3, 1, 5, 0.1, 0.1, REPEATING),
            playerState.WALKING_DOWN_RIGHT: Animation(1, 3, 1, 3, 0.1, 0.1, REPEATING),
        }
        
        self.state = playerState.IDLE #default state
        self.current_animation = self.animations[self.state] #default animation
    
    def update(self, room: Room):
        self.move()
        self.check_collisions(room)
        self.update_position()
        self.update_animation()
    
    def draw(self):
        source = self.current_animation.animation_frame() #get current frame
        origin = Vector2(0.0, 0.0)
        draw_texture_pro(self.sprite, source, self.rect, origin, 0.0, WHITE)

        #DEBUG
        # draw_rectangle_lines_ex(self.hitbox, 1, RED) 

    def move(self):
        self.vel.x = 0.0
        self.vel.y = 0.0

        speed = 300.0 if is_key_down(KEY_LEFT_SHIFT) else 200.0 #defines speed, increases if shift is pressed

        movement_keys = { #dictionary of movements
            (KEY_A, KEY_W): (Vector2(-speed, -speed), playerState.WALKING_UP_LEFT, LEFT), #top left
            (KEY_A, KEY_S): (Vector2(-speed, speed), playerState.WALKING_DOWN_LEFT, LEFT), #bottom left
            (KEY_D, KEY_W): (Vector2(speed, -speed), playerState.WALKING_UP_RIGHT, RIGHT), #top right
            (KEY_D, KEY_S): (Vector2(speed, speed), playerState.WALKING_DOWN_RIGHT, RIGHT), #bottom right
            (KEY_A,): (Vector2(-speed, 0), playerState.WALKING_LEFT, LEFT),  #left
            (KEY_D,): (Vector2(speed, 0), playerState.WALKING_RIGHT, RIGHT), #right
            (KEY_W,): (Vector2(0, -speed), playerState.WALKING_UP, UP),  #up
            (KEY_S,): (Vector2(0, speed), playerState.WALKING_DOWN, DOWN), #down
        }

        for keys, (vel, state, direction) in movement_keys.items(): #for each key in movement keys
            if all(is_key_down(k) for k in keys): #if all keys in a specific movement key are pressed, define the players velocity, state, and direction
                self.vel = vel
                self.state = state
                self.dir = direction
                break #if condition is met break loop
        else: #if condition wasn't met, player is idle (no key's pressed)
            self.state = playerState.IDLE



    def update_position(self):
        self.rect.x += self.vel.x * get_frame_time()
        self.rect.y += self.vel.y * get_frame_time()
        self.hitbox.x = self.rect.x + (self.rect.width - self.hitbox.width) / 2
        self.hitbox.y = self.rect.y + self.rect.height - self.hitbox.height

    def update_animation(self):
        self.current_animation = self.animations[self.state]
        self.current_animation.animation_update() 


    ######## COLLISION CHECKING #########
    def check_collisions(self, room):
        self.check_obstacle_collisions(room)

    def check_obstacle_collisions(self, room: Room):
        for obstacle in room.rectangles:
            if check_collision_recs(self.hitbox, obstacle):

                # Get overlap x and y
                #TODO: understand this
                player_center = Vector2(self.hitbox.x + self.hitbox.width/2, self.hitbox.y + self.hitbox.height/2)
                obstacle_center = Vector2(obstacle.x + obstacle.width/2, obstacle.y + obstacle.height/2)
                direction = vector2_subtract(player_center, obstacle_center)
                player_half_size = Vector2(self.hitbox.width/2, self.hitbox.height/2)
                obstacle_half_size = Vector2(obstacle.width/2, obstacle.height/2)
                overlap_x = player_half_size.x + obstacle_half_size.x - abs(direction.x)
                overlap_y = player_half_size.y + obstacle_half_size.y - abs(direction.y)

                # x-axis collision
                if overlap_x < overlap_y:
                    if direction.x > 0: 
                        self.rect.x += overlap_x # player to right
                    else:
                        self.rect.x -= overlap_x # player to left
                    self.vel.x = 0
                # y-axis collision
                else:
                    if direction.y > 0:
                        self.rect.y += overlap_y # player above
                    else:
                        self.rect.y -= overlap_y # player below
                    self.vel.y = 0
