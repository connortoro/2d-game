from pyray import *


#animation types
REPEATING = 0
ONESHOT = 1

class Animation:
    def __init__(self, fst, lst, cur, offset, spd, rem, animation_type):
        self.fst = fst #first frame
        self.lst = lst #last frame
        self.cur = cur #current frame
        self.offset = offset #offset of imge
        self.spd = spd #speed of animation
        self.rem = rem #remaining time on frame
        self.animation_type = animation_type

    def animation_frame(self):
        x = (self.cur % (self.lst + 1)) * 32.0
        y = self.offset * 32.0
        return Rectangle (float(x), float(y), 32.0, 32.0)
    
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