from raylibpy import *
from player import Player, W, H
from animation import Animation, REPEATING

class PlayerUI:
    def __init__(self, player):
        self.player = player #player reference
        self.health_bar_texture = load_texture("assets/ui_textures/health_bar.png")
        self.inventory_bar_texture = load_texture("assets/ui_textures/inventory_bar.png")
        self.inv_selected_slot = None #currently selected slot
    #draw health bar to screen
    def draw_health_bar(self):
        health_percentage = self.player.health / self.player.max_health
        total_hearts = 5 #5 total hearts (100 health)
        #define heart logic
        full_hearts = int(health_percentage * total_hearts)
        half_hearts= int((health_percentage * total_hearts - full_hearts) * 2)
        empty_hearts = total_hearts - full_hearts - half_hearts

        #top right on screen
        start_x = 1000
        start_y = 20
        heart_spacing = 45 #space between hearts
        
        #full heart drawing
        for i in range(full_hearts):
            heart_src = Rectangle(0, 0, 16, 16) #full heart on sheet
            draw_texture_pro(self.health_bar_texture, heart_src, Rectangle(start_x + i * heart_spacing, start_y, 48, 48), Vector2(0,0), 0, WHITE)
        
        #half heart drawing
        for i in range(half_hearts):
            heart_src = Rectangle(16, 0, 16, 16)  #half heart on sheet
            draw_texture_pro(self.health_bar_texture, heart_src, Rectangle(start_x + (full_hearts + i) * heart_spacing, start_y, 48, 48), Vector2(0, 0), 0, WHITE)
        
        #empty heart drawing
        for i in range(empty_hearts):
            heart_src = Rectangle(32, 0, 16, 16)  #empty heart on sheet
            draw_texture_pro(self.health_bar_texture, heart_src, Rectangle(start_x + (full_hearts + half_hearts + i) * heart_spacing, start_y, 48, 48), Vector2(0, 0), 0, WHITE)
        
    def draw_inventory_bar(self):
        
        #inventory bar details
        slot_size = 16
        slot_gap = 2
        inv_width = 75
        inv_height = 24
        border_thickness = 4
        scale = 3 #scale of inventory


        scaled_width = inv_width * scale
        scaled_height = inv_height * scale
    
        inventory_x = (W - scaled_width) // 2 #center horizontally
        inventory_y = H - scaled_height - 10 #slightly above the bottom of screen
        #draw texture to screen
        draw_texture_pro(self.inventory_bar_texture, 
                         Rectangle(0, 0, self.inventory_bar_texture.width, self.inventory_bar_texture.height), 
                         Rectangle(inventory_x, inventory_y, scaled_width, scaled_height), Vector2(0, 0), 0, WHITE)

        #logic to detect which slot player is hovering over
        if self.inv_selected_slot is not None:
            selected_slot_x = inventory_x + (self.inv_selected_slot * (slot_size + slot_gap) + border_thickness) * scale
            selected_slot_y = inventory_y + border_thickness * scale

            
            draw_rectangle_lines(selected_slot_x, selected_slot_y, slot_size * scale, slot_size * scale, RED)

    def inventory_key_input(self):
        if is_key_pressed(KEY_ONE):
            self.inv_selected_slot = 0
        if is_key_pressed(KEY_TWO):
            self.inv_selected_slot = 1
        if is_key_pressed(KEY_THREE):
            self.inv_selected_slot = 2
        if is_key_pressed(KEY_FOUR):
            self.inv_selected_slot = 3


    def update(self):
        self.inventory_key_input()

    def unload(self):
        unload_texture(self.health_bar_texture)
        unload_texture(self.inventory_bar_texture)


    def update_health(self, new_health):
        self.player.health = clamp(new_health, 0, self.player.max_health)