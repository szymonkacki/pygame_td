# game/map_builder.py

import pygame
from config import TILE_SIZE, MAP_DATA, DECORATIONS_DATA
from game.assets import load_assets

class MapBuilder:
    """Klasa odpowiedzialna za budowe i renderowanie mapy gry"""
    def __init__(self):
        self.tile_images, self.decor_images = load_assets()
        self.anim_timer = 0
        self.anim_frame = 0

    def update_animation(self, dt):
        """Aktualizuje stan animacji dla dekoracji"""
        self.anim_timer += dt
        if self.anim_timer >= 0.15:
            self.anim_timer = 0
            self.anim_frame = (self.anim_frame + 1) % 6  # 6 klatek

    def draw_map(self, screen, draw_grid = False):
        """Odpowiada za rysowanie mapy"""

        # Rysuje kafelki mapy
        for row_idx, row in enumerate(MAP_DATA):
            for col_idx, tile_id in enumerate(row):
                x = col_idx * TILE_SIZE
                y = row_idx * TILE_SIZE
                tile_img = self.tile_images.get(tile_id)
                if tile_img:
                    screen.blit(tile_img, (x, y))
                # if draw_grid:
                #     pygame.draw.rect(screen, (0, 0, 0, 50), (x, y, TILE_SIZE, TILE_SIZE), 1)  # czarna siatka


        # Rysuje dekoracje mapy
        for row_idx, row in enumerate(DECORATIONS_DATA):
            for col_idx, decor_ids in enumerate(row):
                if decor_ids:
                    x = col_idx * TILE_SIZE
                    y = row_idx * TILE_SIZE
                    for decor_id in decor_ids:
                        image = self.decor_images.get(decor_id)
                        if isinstance(image, list):
                            screen.blit(image[self.anim_frame], (x, y))
                        elif isinstance(image, pygame.Surface):
                            screen.blit(image, (x, y))

