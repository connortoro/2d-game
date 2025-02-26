from pyray import *
from enum import Enum
from animation import Animation, REPEATING, ONESHOT
import time

#dimensions of space
W = 1300
H = 700

LEFT = 0
RIGHT = 1

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
        self.rect = Rectangle(W / 2.0, H / 2.0, 16.0 * 3, 24.0 * 3) # * 3 to increase size of sprite
        self.vel = Vector2(0.0, 0.0)
        self.sprite = texture
        self.dir = RIGHT #right

        """================================= ANIMATIONS ================================="""
        self.animations = {
            playerState.IDLE: Animation(2, 2, 2, 4, 0.1, 0.1, REPEATING),
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

        if is_key_down(KEY_LEFT_SHIFT):  #running
            #check for diagonal running (shift + movement keys)
            if is_key_down(KEY_A) and is_key_down(KEY_W):  #up left
                self.vel.x = -300.0
                self.vel.y = -300.0
                self.dir = LEFT
                self.state = playerState.WALKING_UP_LEFT

            elif is_key_down(KEY_A) and is_key_down(KEY_S):  #down left
                self.vel.x = -300.0
                self.vel.y = 300.0
                self.dir = LEFT
                self.state = playerState.WALKING_DOWN_LEFT

            elif is_key_down(KEY_D) and is_key_down(KEY_W):  #up right
                self.vel.x = 300.0
                self.vel.y = -300.0
                self.dir = RIGHT
                self.state = playerState.WALKING_UP_RIGHT 

            elif is_key_down(KEY_D) and is_key_down(KEY_S):  #down right
                self.vel.x = 300.0
                self.vel.y = 300.0
                self.dir = RIGHT
                self.state = playerState.WALKING_DOWN_RIGHT 

            #regular horizontal/vertical running
            elif is_key_down(KEY_A):  #left
                self.vel.x = -300.0
                self.dir = LEFT
                self.state = playerState.WALKING_LEFT 
            elif is_key_down(KEY_D):  #right
                self.vel.x = 300.0
                self.dir = RIGHT
                self.state = playerState.WALKING_RIGHT 

            elif is_key_down(KEY_W): #up
                self.vel.y = -300.0
                self.state = playerState.WALKING_UP
            elif is_key_down(KEY_S): #down
                self.vel.y = 300.0
                self.state = playerState.WALKING_DOWN
            else:
                self.state = playerState.IDLE  #idle state when no keys pressed

        else:  #walking
            #check for diagonal walking
            if is_key_down(KEY_A) and is_key_down(KEY_W):  #up left
                self.vel.x = -200.0
                self.vel.y = -200.0
                self.dir = LEFT
                self.state = playerState.WALKING_UP_LEFT
            elif is_key_down(KEY_A) and is_key_down(KEY_S):  # down left
                self.vel.x = -200.0
                self.vel.y = 200.0
                self.dir = LEFT
                self.state = playerState.WALKING_DOWN_LEFT
            elif is_key_down(KEY_D) and is_key_down(KEY_W):  # up right
                self.vel.x = 200.0
                self.vel.y = -200.0
                self.dir = RIGHT
                self.state = playerState.WALKING_UP_RIGHT
            elif is_key_down(KEY_D) and is_key_down(KEY_S):  # down right
                self.vel.x = 200.0
                self.vel.y = 200.0
                self.dir = RIGHT
                self.state = playerState.WALKING_DOWN_RIGHT
            #check for horizontal walking
            elif is_key_down(KEY_A):  #left
                self.vel.x = -200.0
                self.dir = LEFT
                self.state = playerState.WALKING_LEFT
            elif is_key_down(KEY_D):  #right
                self.vel.x = 200.0
                self.dir = RIGHT
                self.state = playerState.WALKING_RIGHT
            #up and down walking
            elif is_key_down(KEY_W):  #up
                self.vel.y = -200.0
                self.state = playerState.WALKING_UP 
            elif is_key_down(KEY_S):  #down
                self.vel.y = 200.0
                self.state = playerState.WALKING_DOWN
            else:
                self.state = playerState.IDLE 


    def update_position(self):
        self.rect.x += self.vel.x * get_frame_time()
        self.rect.y += self.vel.y * get_frame_time()

    def update_animation(self):
        self.current_animation = self.animations[self.state]
        self.current_animation.animation_update() #updates current animation
