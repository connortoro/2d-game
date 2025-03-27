import raylibpy as rl


room_texture = None
old_room_texture = None
water_texture = None

def load_textures():
    global room_texture, old_room_texture, water_texture
    room_texture = rl.load_texture("assets/textures/Dungeon Gathering Free Version/Set 1.1.png")
    old_room_texture = rl.load_texture("assets/textures/tileset_gray.png")
    water_texture = rl.load_texture("assets/textures/Dungeon Gathering Free Version/Set 4.5.png")
