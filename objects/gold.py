from raylibpy import *
from animation import Animation, REPEATING, ONESHOT
from enum import Enum

class coinState(Enum):
    IDLE = "IDLE"
    PICKUP = "PICKUP"

class Gold:
    def __init__(self, x, y):
        self.rect = Rectangle(x-25, y-25, 50, 50)
        self.pickup_sound = load_sound("assets/audio/retro-coin-1-236677.mp3")
        set_sound_pitch(self.pickup_sound, .8)
        set_sound_volume(self.pickup_sound, .7)
        self.coin = load_texture("assets/textures/Dungeon Gathering Free Version/Coin Sheet.png")
        self.animations = {
            coinState.IDLE: Animation(0, 7, 0, 0, 16, 0.1, 0.1, REPEATING, 16, 16),
            coinState.PICKUP: Animation(0, 7, 0, 1, 16, 0.1, 0.1, ONESHOT, 16, 16)
        }
        self.state = coinState.IDLE
        self.current_animation = self.animations[self.state]
        self.pickup_played = False

    def update(self, player, room):
        if self.state == coinState.IDLE and check_collision_recs(self.rect, player.hitbox):
            self.state = coinState.PICKUP
            self.current_animation = self.animations[self.state]
            if not self.pickup_played: #if player has picked up coin, play sound and increase gold
                play_sound(self.pickup_sound)
                player.gold = player.gold + 1
                self.pickup_played = True
        if self.state == coinState.PICKUP and self.current_animation.is_complete(): #makes sure pickup animation plays before removing coin
            room.objects.remove(self)
        else:
            self.current_animation = self.animations[self.state]
        self.current_animation.animation_update()
        
    def draw(self):
        src = self.current_animation.animation_frame_horizontal()
        draw_texture_pro(self.coin, src, self.rect, Vector2(0, 0), 0, WHITE)

