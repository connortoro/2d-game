from raylibpy import *
import textures

class Gold:
    def __init__(self, x, y):
        self.rect = Rectangle(x-25, y-25, 50, 50)
        self.pickup_sound = load_sound("assets/audio/retro-coin-1-236677.mp3")
        set_sound_pitch(self.pickup_sound, .8)
        set_sound_volume(self.pickup_sound, .7)

    def update(self, player, room):
        if check_collision_recs(self.rect, player.hitbox):
            play_sound(self.pickup_sound)
            player.gold = player.gold + 1
            room.objects.remove(self)

    def draw(self):
        draw_texture_pro(textures.old_base, Rectangle(13*16, 0, 16, 16), self.rect, Vector2(0, 0), 0, WHITE)
