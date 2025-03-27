from raylibpy import *
import textures

class Heart:
    def __init__(self, x, y):
        self.rect = Rectangle(x-25, y-25, 50, 50)
        self.pickup_sound = load_sound("assets/audio/bubble-pop-2-293341.wav")

    def update(self, player, room):
        if check_collision_recs(self.rect, player.hitbox):
            play_sound(self.pickup_sound)
            player.heal(10)
            room.objects.remove(self)

    def draw(self):
        draw_texture_pro(textures.old_base, Rectangle(13*16, 1*16, 16, 16), self.rect, Vector2(0, 0), 0, WHITE)
