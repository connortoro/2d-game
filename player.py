from pyray import *
from animation import Animation, REPEATING, ONESHOT
import time

#dimensions of space
W = 1300
H = 700

#animations
IDLE = 0
WALKING = 1
RUNNING = 2
ATTACKING = 3
#directions
LEFT = -1
RIGHT = 1

class Player:
    def __init__(self, texture):
        self.rect = Rectangle(W / 2.0, H / 2.0, 32.0 * 3, 32.0 * 3) # * 3 to increase size of sprite
        self.vel = Vector2(0.0, 0.0)
        self.sprite = texture
        self.dir = RIGHT #right

        """================================= ANIMATIONS ================================="""
        self.animations = {
            IDLE: Animation(0, 1, 0, 0, 0.2, 0.2, REPEATING),
            WALKING: Animation(0, 3, 0, 2, 0.2, 0.2, REPEATING),
            RUNNING: Animation(0, 7, 0, 3, 0.1, 0.1, REPEATING),
            ATTACKING: Animation(0, 7, 0, 8, 0.1, 0.1, ONESHOT)
        }
        self.state = IDLE #default state
        self.current_animation = self.animations[self.state] #default animation

    def draw(self):
        source = self.current_animation.animation_frame() #get current frame
        if self.dir == LEFT: #pointing opposite direction
            source.width = -source.width #flip frame
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
                self.state = RUNNING 
            elif is_key_down(KEY_A) and is_key_down(KEY_S):  #down left
                self.vel.x = -300.0
                self.vel.y = 300.0
                self.dir = LEFT
                self.state = RUNNING 
            elif is_key_down(KEY_D) and is_key_down(KEY_W):  #up right
                self.vel.x = 300.0
                self.vel.y = -300.0
                self.dir = RIGHT
                self.state = RUNNING 
            elif is_key_down(KEY_D) and is_key_down(KEY_S):  #down right
                self.vel.x = 300.0
                self.vel.y = 300.0
                self.dir = RIGHT
                self.state = RUNNING 
            #regular horizontal running
            elif is_key_down(KEY_A):  #left
                self.vel.x = -300.0
                self.dir = LEFT
                self.state = RUNNING  
            elif is_key_down(KEY_D):  #right
                self.vel.x = 300.0
                self.dir = RIGHT
                self.state = RUNNING 
            else:
                self.state = IDLE  #idle state when no keys pressed

        else:  #walking
            #check for diagonal walking
            if is_key_down(KEY_A) and is_key_down(KEY_W):  #up left
                self.vel.x = -200.0
                self.vel.y = -200.0
                self.dir = LEFT
                self.state = WALKING
            elif is_key_down(KEY_A) and is_key_down(KEY_S):  # down left
                self.vel.x = -200.0
                self.vel.y = 200.0
                self.dir = LEFT
                self.state = WALKING
            elif is_key_down(KEY_D) and is_key_down(KEY_W):  # up right
                self.vel.x = 200.0
                self.vel.y = -200.0
                self.dir = RIGHT
                self.state = WALKING
            elif is_key_down(KEY_D) and is_key_down(KEY_S):  # down right
                self.vel.x = 200.0
                self.vel.y = 200.0
                self.dir = RIGHT
                self.state = WALKING
            #check for horizontal walking
            elif is_key_down(KEY_A):  #left
                self.vel.x = -200.0
                self.dir = LEFT
                self.state = WALKING 
            elif is_key_down(KEY_D):  #right
                self.vel.x = 200.0
                self.dir = RIGHT
                self.state = WALKING 
            #up and down walking
            elif is_key_down(KEY_W):  #up
                self.vel.y = -200.0
                self.state = WALKING 
            elif is_key_down(KEY_S):  #down
                self.vel.y = 200.0
                self.state = WALKING 
            else:
                self.state = IDLE 


    def update_position(self):
        self.rect.x += self.vel.x * get_frame_time()
        self.rect.y += self.vel.y * get_frame_time()

    def update_animation(self):
        self.current_animation = self.animations[self.state]
        self.current_animation.animation_update() #updates current animation
