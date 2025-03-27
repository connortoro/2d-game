from raylibpy import *
from floor import Floor
from player import Player, W, H
from ui import PlayerUI
from enum import Enum
import time
import textures
from raylibpy import load_sound, play_sound, unload_sound

#Init
init_window(W, H, "My Game")
textures.load_textures()

init_audio_device()
player_texture = load_texture("assets/player_sheet/player.png")
player = Player(player_texture)
playerui = PlayerUI(player)
floor = Floor()

# Load background music
music = load_music_stream("assets/audio/rpg-city-8381.mp3") 
play_music_stream(music)
set_music_volume(music, 0.1)

# Load background music
game_music = load_music_stream("assets/audio/floor_1_music.mp3") 
play_music_stream(game_music)
main_menu_music = load_music_stream("assets/audio/main_menu_music.mp3")
play_music_stream(main_menu_music)
# Game state enum
class GameState(Enum):
    MAIN_MENU = 0
    PLAYING = 1
    EXIT = 2
    GAME_OVER = 3
    PAUSED = 4

game_state = GameState.MAIN_MENU


def main_menu():
    global game_state
    game_state = GameState.MAIN_MENU
    if main_menu_music:
        update_music_stream(main_menu_music)
        set_music_volume(main_menu_music, 0.10) #10% volume (temporary, music is too loud lol)
    playerui.draw_main_menu(start_game, quit_game)

def restart_game():
    global game_state, player, floor, playerui
    game_state = GameState.PLAYING
    player = Player(player_texture)
    floor = Floor()
    playerui = PlayerUI(player)

def start_game():
    global game_state, main_menu_music, game_music
    game_state = GameState.PLAYING

def quit_game():
    global game_state
    game_state = GameState.EXIT

def toggle_pause():
    global game_state
    if game_state == GameState.PLAYING:
        game_state = GameState.PAUSED
    elif game_state == GameState.PAUSED:
        game_state = GameState.PLAYING
    

# Main game loop

while not window_should_close():
    set_exit_key(KEY_NULL) #sets exit key to null to allow for pause menu action
    if is_key_pressed(KEY_ESCAPE): #pause button
        toggle_pause()

    # Check for player death and update game state
    if game_state == GameState.PLAYING and player.health <= 0:
        game_over_timer = time.time()
        game_state = GameState.GAME_OVER
    
    # Drawing
    begin_drawing()
    clear_background(SKYBLUE)

    if game_state == GameState.MAIN_MENU:
        main_menu()
    else:
        if game_state != GameState.PAUSED: #to prevent attacks/movement when paused
            #update elements
            player.update(floor.get_current_room())
            floor.update(player)
            playerui.update()
        #draw elements
        floor.draw()
        player.draw()
        playerui.draw(floor)
        if game_state == GameState.PLAYING:
            #start playing game music
            if game_music:
                update_music_stream(game_music)
                set_music_volume(game_music, 0.10) #10% volume (temporary, music is too loud lol)


        elif game_state == GameState.PAUSED:

            playerui.draw_pause_menu(toggle_pause, main_menu)

        # Draw game over overlay if in game over state
        elif game_state == GameState.GAME_OVER:
            playerui.draw_game_over(restart_game)
        
        #Exit if player chooses to enter exit gamestate
        elif game_state == GameState.EXIT:
            break


    end_drawing()

# Unload resources
unload_texture(player_texture)
playerui.unload()
unload_music_stream(game_music)
unload_music_stream(main_menu_music)
close_audio_device()
close_window()