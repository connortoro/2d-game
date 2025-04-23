from raylibpy import *
from animation import Animation, REPEATING, ONESHOT
from enum import Enum
from sounds import SoundManager
from config import *

class heartState(Enum):
    IDLE = "IDLE"
    PICKUP = "PICKUP"

class Heart:
    def __init__(self, x, y):
        self.config = load_config()
        self.sound_manager = SoundManager(self.config)
        self.rect = Rectangle(x-25, y-25, 50, 50)
        self.pickup_sound = self.sound_manager.sounds["heart"]
        self.animations = {
            heartState.IDLE: Animation(0, 5, 0, 0, 16, 0.1, 0.1, REPEATING, 16, 16),
            heartState.PICKUP: Animation(0, 5, 0, 1, 16, 0.1, 0.1, ONESHOT, 16, 16)
        }
        self.state = heartState.IDLE
        self.current_animation = self.animations[self.state]
        self.pickup_played = False
        self.texture = load_texture("assets/textures/heart_item.png")


    def update(self, player, room):
        if self.state == heartState.IDLE and check_collision_recs(self.rect, player.hitbox):
            self.state = heartState.PICKUP
            self.current_animation = self.animations[self.state]
            if not self.pickup_played:
                self.sound_manager.play_sound("heart")
                player.heal(10)
                self.pickup_played = True
        if self.state == heartState.PICKUP and self.current_animation.is_complete():
            room.objects.remove(self)
        else:
            self.current_animation = self.animations[self.state]
        self.current_animation.animation_update()

    def draw(self):
        src = self.current_animation.animation_frame_horizontal()
        draw_texture_pro(self.texture, src, self.rect, Vector2(0, 0), 0, WHITE)
