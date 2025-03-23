from raylibpy import *


#animation types
REPEATING = 0
ONESHOT = 1

class Animation:
    def __init__(self, fst, lst, cur, offset, offset_distance, spd, rem, animation_type, frame_width, frame_height):
        self.fst = fst #first frame
        self.lst = lst #last frame
        self.cur = cur #current frame
        self.offset = offset #offset of imge
        self.offset_distance = offset_distance #distance between each sprite
        self.spd = spd #speed of animation
        self.rem = rem #remaining time on frame
        self.animation_type = animation_type
        self.frame_width = frame_width
        self.frame_height = frame_height 

    def animation_frame_vertical(self): #for vertical sprite sheets
        y = (self.cur % (self.lst + 1)) * self.frame_height
        x = self.offset * self.offset_distance
        return Rectangle (float(x), float(y), float(self.frame_width), float(self.frame_height))
    
    def animation_frame_horizontal(self): #for horizontal sprite sheets
        x = (self.cur % (self.lst + 1)) * self.frame_height
        y = self.offset * self.offset_distance
        return Rectangle (float(x), float(y), float(self.frame_width), float(self.frame_height))
    
    def animation_update(self):
        dt = get_frame_time()
        self.rem -= dt
        if(self.rem <= 0):
            self.rem = self.spd
            self.cur += 1
            if(self.cur > self.lst): #last frame
                if self.animation_type == REPEATING:
                    self.cur = self.fst #loop back to beginning
                elif self.animation_type == ONESHOT:
                    self.cur = self.lst #stay at last frame

    def is_complete(self):
        if self.animation_type == ONESHOT and self.cur >= self.lst:
            return True
        return False
        
    def reset(self):
        self.cur = self.fst
        self.rem = self.spd