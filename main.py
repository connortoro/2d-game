from raylibpy import *
from room import Room
from floor import Floor

#Init
init_window(1300, 800, "My Game")
floor = Floor()


while not window_should_close():

    #Updates

    #Drawing
    begin_drawing()
    clear_background(WHITE)

    floor.rooms[0].draw()
    
    end_drawing()
close_window()


