from raylibpy import *
from animation import Animation, REPEATING
import textures

W = 1300
H = 900


class NPC:
    def __init__(self, x, y):
        sprite_width = 16 * 4
        sprite_height = 16 * 4
        self.texture = textures.trader
        self.rect = Rectangle(x, y, sprite_width, sprite_height)
        self.current_animation = Animation(0, 4, 0, 0, 16, 0.2, 0.2, REPEATING, 16, 16)
        self.interacted = False
        self.in_range = False
        self.dialog_options = {
            1: "Increase Health",
            2: "Increase Speed",
            3: "Increase Attack"
        }

    def update(self, player, room):
        self.current_animation.animation_update()
        dist = vector2_distance(Vector2(player.hitbox.x, player.hitbox.y), Vector2(self.rect.x+50, self.rect.y+50))
        self.in_range = (dist < 150)
        if self.in_range:
            self.check_interaction(player)

    def draw(self):
        source = self.current_animation.animation_frame_horizontal()
        origin = Vector2(0.0, 0.0)
        draw_texture_pro(self.texture, source, self.rect, origin, 0.0, WHITE)

        if self.in_range and not self.interacted:
            self.draw_options()

    def draw_options(self):
        x = self.rect.x - 110
        y = self.rect.y+120

        rect = Rectangle(x, y, 320, 128)
        color = Color(50, 50, 50, 150)

        draw_rectangle_rounded(rect, .4, 0, color)

        x += 20
        y += 20
        draw_text("Hello, hero! Choose an upgrade:", x, y, 18, WHITE)
        draw_text("1: Increase Health (3 Gold)", x, y+25, 18, WHITE)
        draw_text("2: Increase Speed (2 Gold)", x, y+50, 18, WHITE)
        draw_text("3: Increase Attack (4 Gold)", x, y+75, 18, WHITE)

    def check_interaction(self, player):
        if self.interacted: 
            return
        if is_key_pressed(KEY_ONE):
            if player.gold < 3:
                return
            else:
                player.increase_health(10)
                player.gold -= 3
                self.interacted = True
                self.current_animation.animation_update()
        elif is_key_pressed(KEY_TWO):
            if player.gold < 2:
                return
            else:
                player.speed += 40
                player.displayed_speed += 10
                player.gold -= 2
                self.interacted = True
                self.current_animation.animation_update()
        elif is_key_pressed(KEY_THREE):
            if player.gold < 4:
                return
            else:
                player.increase_attack(5)
                player.gold -= 4
                self.interacted = True
                self.current_animation.animation_update()
