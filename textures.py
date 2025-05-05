import raylibpy as rl

#MAP
base = None
old_base = None
water = None
src_map = None

#ITEMS
gold = None

#ENTITIES
trader = None
zombie = None
mummy = None
minion = None
bat = None
necro = None
spark = None
orc1 = None
orc2 = None
orc3 = None



def load_textures():
    global base, old_base, water, src_map, zombie, mummy, minion, bat, trader, necro, spark, speed_icon, demon, orc1, orc2, orc3 
    base = rl.load_texture("assets/textures/Dungeon Gathering Free Version/Set 1.png")
    old_base = rl.load_texture("assets/textures/tileset_gray.png")
    water = rl.load_texture("assets/textures/Dungeon Gathering Free Version/Set 4.5.png")
    speed_icon = rl.load_texture("assets/textures/speed_icon.png")
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

    trader = rl.load_texture("assets/player_sheet/trader2.png")
    zombie = rl.load_texture("assets/enemy_sheets/LV1_BOSS.png")
    minion = rl.load_texture("assets/enemy_sheets/MINION_1.png")
    mummy = rl.load_texture("assets/enemy_sheets/MINION_3.png")
    bat = rl.load_texture("assets/enemy_sheets/MINION_4.png")
    necro = rl.load_texture("assets/enemy_sheets/necromancer.png")
    demon = rl.load_texture("assets/enemy_sheets/demon.png")
    spark = rl.load_texture("assets/enemy_sheets/spark.png")
    orc1 = rl.load_texture("assets/enemy_sheets/orc1_full_spritesheet.png")
    orc2 = rl.load_texture("assets/enemy_sheets/orc2_sheet.png")
    orc3 = rl.load_texture("assets/enemy_sheets/orc3_sheet.png")
