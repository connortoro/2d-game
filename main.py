from raylibpy import *
from room import Room
from floor import Floor
from player import Player, W, H

#Init
init_window(W, H, "My Game")
player_texture = load_texture("assets/player_sheet/8d-character.png")
player = Player(player_texture)
floor = Floor()


while not window_should_close():

    #Updates
    player.move()
    player.update_position()
    player.update_animation()
    #Drawing
    begin_drawing()
    clear_background(SKYBLUE)
    player.draw()
    end_drawing()
    floor.rooms[0].draw()
    
    #end_drawing()
unload_texture(player_texture)
close_window()


