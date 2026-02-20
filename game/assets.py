#game/assets.py

import pygame, os

def load_animation_frames(path, frame_width, frame_height, frame_count):
        """Ładuje klatki animacji z podanego pliku."""
        sheet = pygame.image.load(path).convert_alpha()
        return [sheet.subsurface(pygame.Rect(i * frame_width, 0, frame_width, frame_height)) for i in range(frame_count)]


def load_assets():
    """Ładuje grafiki mapy"""

    # Grafiki dla kafelków mapy
    TILE_IMAGES = \
    {
    0: pygame.image.load("images/tiles/FieldsTile_38.png").convert_alpha(), #plain
    1: pygame.image.load("images/tiles/FieldsTile_01.png").convert_alpha(), #plain_path
    2: pygame.image.load("images/tiles/FieldsTile_10.png").convert_alpha(), #left_up_cor
    3: pygame.image.load("images/tiles/FieldsTile_12.png").convert_alpha(), #right_up_cor
    4: pygame.image.load("images/tiles/FieldsTile_22.png").convert_alpha(), #left_down_cor
    5: pygame.image.load("images/tiles/FieldsTile_28.png").convert_alpha(), #right_down_cor
    6: pygame.image.load("images/tiles/FieldsTile_47.png").convert_alpha(), #gr_covered (*)
    7: pygame.image.load("images/tiles/FieldsTile_55.png").convert_alpha(), #grass_up
    8: pygame.image.load("images/tiles/FieldsTile_24.png").convert_alpha(), #grass_down
    9: pygame.image.load("images/tiles/FieldsTile_50.png").convert_alpha(), #grass_left
    10: pygame.image.load("images/tiles/FieldsTile_53.png").convert_alpha(), #gr_right
    11: pygame.image.load("images/tiles/FieldsTile_44.png").convert_alpha(), #gr_all_but_top
    12: pygame.image.load("images/tiles/FieldsTile_43.png").convert_alpha(), #gr_all_but_bottom
    13: pygame.image.load("images/tiles/FieldsTile_26.png").convert_alpha(), #gr_left_bottom
    14: pygame.image.load("images/tiles/FieldsTile_06.png").convert_alpha(), #gr_left_up
    15: pygame.image.load("images/tiles/FieldsTile_40.png").convert_alpha(), #gr_left_right_1
    16: pygame.image.load("images/tiles/FieldsTile_32.png").convert_alpha(), #gr_left_right_2
    17: pygame.image.load("images/tiles/FieldsTile_48.png").convert_alpha(), #gr_left_right_3
    18: pygame.image.load("images/tiles/FieldsTile_30.png").convert_alpha(), #gr_down_up_1
    19: pygame.image.load("images/tiles/FieldsTile_31.png").convert_alpha(), #gr_down_up_2
    20: pygame.image.load("images/tiles/FieldsTile_39.png").convert_alpha(), #gr_down_up_3
    }

    # Grafiki dekoracji
    DECOR_IMAGES = \
    {
    1: pygame.image.load("images/decor/bush/4.png").convert_alpha(),
    2: pygame.image.load("images/decor/stones/11.png").convert_alpha(),
    3: pygame.image.load("images/decor/stones/5.png").convert_alpha(),
    4: pygame.image.load("images/decor/grass/3.png").convert_alpha(),
    5: load_animation_frames("images/decor/campfire/2.png", 32, 32, 6), #szer, wys, frames
    6: pygame.image.load("images/decor/PlaceForTower2.png").convert_alpha(), #tower_placement
    7: load_animation_frames("images/decor/campfire/1.png", 32, 64, 6),
    # 8: pygame.image.load("images/decor//.png").convert_alpha(),               # FREE SLOT
    9: pygame.image.load("images/decor/fences/Tile2_11.png").convert_alpha(), #fen_right_down
    10: pygame.image.load("images/decor/fences/Tile2_03.png").convert_alpha(), #fen_right_up
    11: pygame.image.load("images/decor/fences/Tile2_13.png").convert_alpha(), #fen_mid_down
    12: pygame.image.load("images/decor/fences/Tile2_05.png").convert_alpha(), #fen_mid_up
    13: pygame.image.load("images/decor/fences/Tile2_12.png").convert_alpha(), #fen_left_down
    14: pygame.image.load("images/decor/fences/Tile2_04.png").convert_alpha(), #fen_left_up
    15: pygame.image.load("images/decor/fences/Tile2_41.png").convert_alpha(), #fen_left_cor_down
    16: pygame.image.load("images/decor/fences/Tile2_33.png").convert_alpha(), #fen_left_cor_up
    17: pygame.image.load("images/decor/fences/Tile2_25.png").convert_alpha(), #fen_left_left_1
    18: pygame.image.load("images/decor/fences/Tile2_17.png").convert_alpha(), #fen_left_left_2

    #flowers
    19: pygame.image.load("images/decor/flowers/7.png").convert_alpha(),
    20: pygame.image.load("images/decor/flowers/8.png").convert_alpha(),
    21: pygame.image.load("images/decor/flowers/9.png").convert_alpha(),
    22: pygame.image.load("images/decor/flowers/10.png").convert_alpha(),
    23: pygame.image.load("images/decor/flowers/11.png").convert_alpha(),

    #grass
    24: pygame.image.load("images/decor/grass/1.png").convert_alpha(),
    25: pygame.image.load("images/decor/grass/2.png").convert_alpha(),
    26: pygame.image.load("images/decor/grass/3.png").convert_alpha(),
    27: pygame.image.load("images/decor/grass/4.png").convert_alpha(),
    28: pygame.image.load("images/decor/grass/5.png").convert_alpha(),
    29: pygame.image.load("images/decor/grass/6.png").convert_alpha(),

    #shadows
    30: pygame.image.load("images/decor/shadows/4.png").convert_alpha(), #mid_low
    31: pygame.image.load("images/decor/shadows/6.png").convert_alpha(), #big
    32: pygame.image.load("images/decor/shadows/5.png").convert_alpha(), #mid_high

    #tree
    33: pygame.image.load("images/decor/tree/tree_1.png").convert_alpha(), #normal
    34: pygame.image.load("images/decor/tree/tree_2.png").convert_alpha(), #cut(trunk)

    #tents
    35: pygame.image.load("images/decor/tents/1.png").convert_alpha(), # right
    36: pygame.image.load("images/decor/tents/2.png").convert_alpha(), # top
    37: pygame.transform.flip(pygame.image.load("images/decor/tents/1.png").convert_alpha(), True, False), #left
    37.5 : pygame.image.load("images/decor/tents/6.png").convert_alpha(), 
    
    38: pygame.image.load("images/decor/boxes/1.png").convert_alpha(), #barrel
    39: pygame.image.load("images/decor/boxes/3.png").convert_alpha(), # box

    #fences
    40: pygame.image.load("images/decor/fences2/1.png").convert_alpha(), #horizontally
    41: pygame.image.load("images/decor/fences2/7.png").convert_alpha(), #vertically
    42: pygame.image.load("images/decor/fences2/pointers/3.png").convert_alpha(), # point_top_left
    43: pygame.image.load("images/decor/fences2/pointers/4.png").convert_alpha(), # point_right

    44: load_animation_frames("images/decor/flag/2.png", 32, 64, 6),
    }

    return TILE_IMAGES, DECOR_IMAGES

# pygame.transform.flip(frame, True, False)
pygame.mixer.init()

def load_sound(name):
    """Ładuje dźwięk z pliku."""
    return pygame.mixer.Sound(os.path.join(name))

# Dźwięki używane w grze
SOUNDS = {
    "arrow": load_sound("sounds/arrow_fired.mp3"),
    "enemy_death": load_sound("sounds/enemy_dead.mp3"),
    "wave_start": load_sound("sounds/wave_start.mp3"),
    "wave_cleared": load_sound("sounds/wave_cleared.mp3")
}

# Domyślne wartości głośności
VOLUMES = \
{
     "arrow": 0.05,
     "enemy_death": 0.1,
     "wave_start": 0.2,
     "wave_cleared": 0.2
}

# Ustawianie początkowych głośności
for key, sound in SOUNDS.items():
    sound.set_volume(VOLUMES[key])

def mute_sounds():
    """Wycisza wszystkie dźwięki."""
    for sound in SOUNDS.values():
        sound.set_volume(0)

def unmute_sounds():
    """Przywraca głośność dźwięków."""
    for key, sound in SOUNDS.items():
        sound.set_volume(VOLUMES[key])
