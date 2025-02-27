from raylibpy import *
from enum import Enum
from animation import Animation, REPEATING, ONESHOT
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
        self.rect = Rectangle(W / 2.0, H / 2.0, 16.0 * 4, 24.0 * 4) # * 3 to increase size of sprite
        self.vel = Vector2(0.0, 0.0)
        self.sprite = texture
        self.dir = RIGHT #right

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

    def draw(self):
        source = self.current_animation.animation_frame() #get current frame

        origin = Vector2(0.0, 0.0)
        draw_texture_pro(self.sprite, source, self.rect, origin, 0.0, WHITE)

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

    def update_animation(self):
        self.current_animation = self.animations[self.state]
        self.current_animation.animation_update() #updates current animation
