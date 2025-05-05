from raylibpy import *
from config import *
import textures

class PlayerUI:
    mm_offset = (50, 100)
    mm_tile_size = 15

    def __init__(self, player, music, config):
        self.player = player #player reference
        self.music = music #game music
        self.config = config
        self.music_volume = self.config["music_volume"]
        set_music_volume(self.music, self.music_volume)
        self.health_bar_texture = load_texture("assets/ui_textures/health_bar.png")
        self.inventory_bar_texture = load_texture("assets/ui_textures/inventory_bar.png")
        self.inv_selected_slot = None #currently selected slot
        self.background = load_texture("assets/textures/background.png")
    def draw(self, floor):
        self.draw_health_bar()
        self.draw_minimap(floor)
        self.draw_score()

    def draw_score(self):
        tint = Color(0, 0, 0, 140)
        opac  = Color(255, 255, 255, 130)
        width = 300
        height = 150
        x = W-(width+100)
        y = H-(height+20)

        rect = Rectangle(x, y, width, height)
        draw_rectangle_rounded(rect, .2, 50, tint)
        draw_texture_pro(textures.old_base, Rectangle(13*16, 0, 16, 16), Rectangle(x, y, 60, 60), Vector2(0, 0), 0, opac)
        draw_text(f"{self.player.gold}", x+60, y+21, 25, opac)

    def draw_minimap(self, floor):
        map = floor.map
        blk = Color(100, 100, 100, 160)
        wht = Color(230, 230, 230, 160)
        grn = Color(20, 240, 40, 240)

        draw_rectangle_lines(self.mm_offset[1], self.mm_offset[0], self.mm_tile_size*len(map[0]), self.mm_tile_size*len(map), WHITE)

        for iy, row in enumerate(map):
            for ix, tile in enumerate(row):
                y = (iy * self.mm_tile_size) + self.mm_offset[0]
                x = (ix * self.mm_tile_size) + self.mm_offset[1]
                if tile == 'x':
                    color = blk
                elif tile == 'o':
                    color = wht
                if iy == floor.pos[0] and ix == floor.pos[1]:
                    rect = Rectangle(x-1, y-1, self.mm_tile_size+2, self.mm_tile_size+2)
                    draw_rectangle_lines_ex(rect, 2, grn)
                draw_rectangle(x, y, self.mm_tile_size, self.mm_tile_size, color)

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

    def draw_main_menu(self):

        draw_texture(self.background, 0, 0, WHITE)

        #title of game
        title = "Dungeon Crawler"
        title_width = measure_text(title, 60)
        draw_text(title, W//2 - title_width//2, H//2 - 100, 60, WHITE)

        #buttons
        start_button = Rectangle(W // 2 - 100, H // 2 - 30, 200, 50)
        settings_button = Rectangle(W // 2 - 100, H // 2 + 40, 200, 50)
        quit_button = Rectangle(W // 2 - 100, H // 2 + 110, 200, 50)

        mouse_pos = get_mouse_position()
        mouse_clicked = is_mouse_button_pressed(MOUSE_LEFT_BUTTON)

        #start button
        start_hovered = check_collision_point_rec(mouse_pos, start_button)
        start_color = GRAY if start_hovered else DARKGRAY
        draw_rectangle_rec(start_button, start_color)
        if start_hovered:
            draw_rectangle_lines_ex(start_button, 3, GOLD) #outline
        start_text = "START"
        start_text_width = measure_text(start_text, 30)
        draw_text(start_text, start_button.x + start_button.width/2 - start_text_width/2, start_button.y + 10, 30, WHITE)
        
        if mouse_clicked and start_hovered:
            return "start"

        #settings button
        settings_hovered = check_collision_point_rec(mouse_pos, settings_button)
        settings_color = GRAY if settings_hovered else DARKGRAY
        draw_rectangle_rec(settings_button, settings_color)
        if settings_hovered:
            draw_rectangle_lines_ex(settings_button, 3, GOLD) #outline
        settings_text = "SETTINGS"
        settings_text_width = measure_text(settings_text, 30)
        draw_text(settings_text, settings_button.x + settings_button.width/2 - settings_text_width/2, settings_button.y + 10, 30, WHITE)

        if mouse_clicked and settings_hovered:
            return "settings"
        
        #quit button
        quit_hovered = check_collision_point_rec(mouse_pos, quit_button)
        quit_color = GRAY if quit_hovered else DARKGRAY
        draw_rectangle_rec(quit_button, quit_color)
        if quit_hovered:
            draw_rectangle_lines_ex(quit_button, 3, GOLD) #outline
        quit_text = "QUIT"
        quit_text_width = measure_text(quit_text, 30)
        draw_text(quit_text, quit_button.x + quit_button.width/2 - quit_text_width/2, quit_button.y + 10, 30, WHITE)

        if mouse_clicked and quit_hovered:
            return "quit"
        
        return None #no button clicked

    def draw_pause_menu(self):
        #transparent background
        draw_rectangle(0, 0, W, H, Color(0, 0, 0, 200))
        #title
        title = "PAUSED"
        title_width = measure_text(title, 60)
        draw_text(title, W//2 - title_width//2, H//2 - 100, 60, WHITE)
        #buttons
        resume_button = Rectangle(W // 2 - 100, H // 2 - 30, 200, 50)
        settings_button = Rectangle(W // 2 - 100, H // 2 + 40, 200, 50)
        quit_button = Rectangle(W // 2 - 100, H // 2 + 110, 200, 50)

        #mouse pos
        mouse_pos = get_mouse_position()
        mouse_clicked = is_mouse_button_pressed(MOUSE_LEFT_BUTTON)

        #resume button
        resume_hovered = check_collision_point_rec(mouse_pos, resume_button)
        resume_color = GRAY if resume_hovered else DARKGRAY
        draw_rectangle_rec(resume_button, resume_color)
        if resume_hovered:
            draw_rectangle_lines_ex(resume_button, 3, GOLD) #outline
        resume_text = "RESUME"
        resume_text_width = measure_text(resume_text, 30)
        draw_text(resume_text, resume_button.x + resume_button.width/2 - resume_text_width/2, resume_button.y + 10, 30, WHITE)
        
        if mouse_clicked and resume_hovered:
            return "resume"

        #settings button
        settings_hovered = check_collision_point_rec(mouse_pos, settings_button)
        settings_color = GRAY if settings_hovered else DARKGRAY
        draw_rectangle_rec(settings_button, settings_color)
        if settings_hovered:
            draw_rectangle_lines_ex(settings_button, 3, GOLD) #outline
        settings_text = "SETTINGS"
        settings_text_width = measure_text(settings_text, 30)
        draw_text(settings_text, settings_button.x + settings_button.width/2 - settings_text_width/2, settings_button.y + 10, 30, WHITE)

        if mouse_clicked and settings_hovered:
            return "settings"
        
        #quit button
        quit_hovered = check_collision_point_rec(mouse_pos, quit_button)
        quit_color = GRAY if quit_hovered else DARKGRAY
        draw_rectangle_rec(quit_button, quit_color)
        if quit_hovered:
            draw_rectangle_lines_ex(quit_button, 3, GOLD) #outline
        quit_text = "QUIT"
        quit_text_width = measure_text(quit_text, 30)
        draw_text(quit_text, quit_button.x + quit_button.width/2 - quit_text_width/2, quit_button.y + 10, 30, WHITE)

        if mouse_clicked and quit_hovered:
            return "quit"
        
        return None #no button clicked

    def draw_settings_menu(self, state):
        if state == state.MAIN_MENU: #0 = main menu
            draw_texture(self.background, 0, 0, WHITE) #background to match main menu

        draw_rectangle(0, 0, W, H, Color(0, 0, 0, 200)) #transparent background

        center_x = get_screen_width() // 2
        center_y = get_screen_height() // 2

        #title
        title = "SETTINGS"
        title_width = measure_text(title, 60)
        draw_text(title, center_x - title_width // 2, center_y - 180, 60, WHITE)

        music_text = "Music Volume:"
        music_width = measure_text(music_text, 20)
        draw_text(music_text, center_x - music_width // 2, center_y - 60, 20, WHITE)
        
        #slider
        slider_width = 200
        slider_height = 10
        slider_x = center_x - slider_width // 2
        slider_y = center_y - 30
        draw_rectangle(slider_x, slider_y, slider_width, slider_height, GRAY)

        #slider handle
        handle_width = 10
        handle_x = slider_x + int(self.music_volume * slider_width) - handle_width // 2
        draw_rectangle(handle_x, slider_y - 5, handle_width, slider_height + 10, DARKGRAY)

        if is_mouse_button_down(MOUSE_LEFT_BUTTON):
            mouse_x, mouse_y = get_mouse_position()
            if (slider_x <= mouse_x <= slider_x + slider_width) and (slider_y - 5 <= mouse_y <= slider_y + slider_height + 5):
                new_volume = (mouse_x - slider_x) / slider_width
                self.music_volume = clamp(new_volume, 0.0, 1.0)
                self.config["music_volume"] = self.music_volume
                save_config(self.config)
                set_music_volume(self.music, self.music_volume)

        
        mouse_pos = get_mouse_position()

        #back button
        button_width = 200
        button_height = 50
        button_x = center_x - button_width // 2
        button_y = slider_y + 60 #below slider

        back_button_rect = Rectangle(button_x, button_y, button_width, button_height)
        back_hovered = check_collision_point_rec(mouse_pos, back_button_rect)
        back_color = GRAY if back_hovered else DARKGRAY
        draw_rectangle_rec(back_button_rect, back_color)
        if back_hovered:
            draw_rectangle_lines_ex(back_button_rect, 3, GOLD) #outline

        back_text = "Back"
        back_text_width = measure_text(back_text, 20)
        draw_text(back_text, button_x + (button_width - back_text_width) // 2, button_y + 15, 20, WHITE)

        if check_collision_point_rec(mouse_pos, back_button_rect):
            if is_mouse_button_pressed(MOUSE_LEFT_BUTTON):
                return "back"
            
        return None
    
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
        self.music_volume = self.config["music_volume"]
        set_music_volume(self.music, self.music_volume)

    def unload(self):
        unload_texture(self.health_bar_texture)
        unload_texture(self.inventory_bar_texture)


    def update_health(self, new_health):
        self.player.health = clamp(new_health, 0, self.player.max_health)

    def draw_game_over(self, restart_func):
        restart_button = Rectangle(W/2 - 100, H/2 + 100, 200, 50)

        #draw semi-transparent backgorund
        draw_rectangle(0, 0, W, H, Color(0, 0, 0, 200))

        #draw game over text
        game_over_text = "GAME OVER"
        score_text = f"Total score: {self.player.get_score()}"
        game_over_text_width = measure_text(game_over_text, 60)
        score_text_width = measure_text(score_text, 40)
        draw_text(game_over_text, W/2 - game_over_text_width/2, H/2 - 100, 60, RED)
        draw_text(score_text, W/2 - score_text_width/2, H/2 - 50, 40, WHITE)  # Centered properly

        draw_rectangle_rec(restart_button, DARKGRAY)
        restart_text = "Restart"
        restart_width = measure_text(restart_text, 30)
        draw_text(restart_text, restart_button.x + (restart_button.width/2) - restart_width/2, 
                restart_button.y + 10, 30, WHITE)
        
        if is_mouse_button_pressed(MOUSE_LEFT_BUTTON):
                mouse_pos = get_mouse_position()
                if check_collision_point_rec(mouse_pos, restart_button):
                    restart_func()

    def reset(self):
        """Reset the player's UI to its initial state."""
        self.player.health = self.player.max_health
        self.inv_selected_slot = None
        self.draw_health_bar()
        self.draw_inventory_bar()

    def draw_instructions(self):
        instructions_text = [
            "Controls:",
            "W, A, S, D: Move",
            "Arrow Up, Down, Left, Right: Attack Direction",
            "E: Interact",
            "X: Exit Dialog",
            "Kill as many enemies as you can before dying!"
        ]
        instructions_background_height = 140
        draw_rectangle(20, H - instructions_background_height - 10, 500, instructions_background_height, Color(0, 0, 0, 180))
        #draws instructions
        for i, line in enumerate(instructions_text):
            draw_text(line, 25, H - 140 + (i * 20), 20, WHITE)