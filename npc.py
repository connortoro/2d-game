from raylibpy import *
from animation import Animation, REPEATING
import textures

W = 1300
H = 900


class NPC:
    def __init__(self, x, y):
        sprite_width = 40 * 4
        sprite_height = 40 * 4
        self.texture = textures.trader
        self.rect = Rectangle(x, y, sprite_width, sprite_height)
        self.current_animation = Animation(0, 4, 0, 0, 40, 0.2, 0.2, REPEATING, 40, 40)
        self.interacted = 0
        self.max_interactions = 3
        self.in_range = False

    def update(self, player, room):
        self.current_animation.animation_update()
        self.player = player
        dist = vector2_distance(Vector2(player.hitbox.x, player.hitbox.y), Vector2(self.rect.x+50, self.rect.y+50))
        self.in_range = (dist < 150)
        if self.in_range:
            self.check_interaction(player)

    def draw(self):
        source = self.current_animation.animation_frame_horizontal()
        origin = Vector2(0.0, 0.0)
        draw_texture_pro(self.texture, source, self.rect, origin, 0.0, WHITE)

        if self.in_range:
            self.draw_options(self.player)

    def draw_options(self, player):
        rectangle_width = 480
        rectangle_height = 148
        x = self.rect.x + (self.rect.width / 2) - (rectangle_width / 2)
        y = self.rect.y - rectangle_height - 20
        rect = Rectangle(x, y, 480, 148)
        color = Color(50, 50, 50, 150)

        draw_rectangle_rounded(rect, .4, 0, color)

        text_x = x + 20
        text_y = y + 20

        if self.interacted >= self.max_interactions:
            draw_text("No more upgrades available", text_x, text_y, 18, WHITE)
            draw_text("Come find me somewhere else!.", text_x, text_y+25, 18, WHITE)
            return
        
        draw_text(f"Hello, hero! Choose an upgrade: ({self.max_interactions - self.interacted} purchases left)", text_x, text_y, 18, WHITE)

        health_text = "1: Increase Health (3 Gold)"
        if hasattr(player, 'absolute_health') and self.player.max_health >= self.player.absolute_health:
            health_text = "1: Maximum health reached!"
        draw_text(health_text, text_x, text_y+25, 18, WHITE)
        draw_text("2: Increase Speed (2 Gold)", text_x, text_y+50, 18, WHITE)
        draw_text("3: Increase Attack (4 Gold)", text_x, text_y+75, 18, WHITE)


    def check_interaction(self, player):
        if self.interacted >= self.max_interactions: 
            return
        
        if is_key_pressed(KEY_ONE):
            if player.gold < 3:
                return
            elif player.max_health >= player.absolute_health:
                return
            else:
                player.increase_health(20)
                player.gold -= 3
                self.interacted += 1
                self.current_animation.animation_update()
        elif is_key_pressed(KEY_TWO):
            if player.gold < 2:
                return
            else:
                player.speed += 40
                player.displayed_speed += 10
                player.gold -= 2
                self.interacted += 1
                self.current_animation.animation_update()
        elif is_key_pressed(KEY_THREE):
            if player.gold < 4:
                return
            else:
                player.increase_attack(5)
                player.gold -= 4
                self.interacted += 1
                self.current_animation.animation_update()
