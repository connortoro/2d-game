import raylibpy as rl


base = None
old_base = None
water = None

src_map = None


def load_textures():
    global base, old_base, water, src_map
    base = rl.load_texture("assets/textures/Dungeon Gathering Free Version/Set 1.png")
    old_base = rl.load_texture("assets/textures/tileset_gray.png")
    water = rl.load_texture("assets/textures/Dungeon Gathering Free Version/Set 4.5.png")

    src_map = {
        'base.tsx': {
            'texture': base,
            'width': 28
        },
        'old_base.tsx': {
            'texture': old_base,
            'width': 16
        },
        'water.tsx': {
            'texture': water,
            'width': 11
        }
}
