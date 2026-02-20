# game/game_manager.py

import pygame, random, math

from config import START_GOLD, START_HP, WHITE, WIDTH, TOWER_SLOTS, TOWER_BASE_COST, \
TOTAL_TOWER_NUMBER, ENEMY_PATH
from game.enemy import Enemy, FastEnemy, TankEnemy
from game.tower import Tower, EvolutionMenu
from game.map_builder import MapBuilder
from game.assets import SOUNDS

def interface_images():
    """Ładuje i przygotowuje grafiki interfejsu."""
    #Ikona dla waluty w grze
    coin_img = pygame.image.load("images/interface/coin.png").convert_alpha()
    coin_icon = coin_img.subsurface((7 * 80, 0, 80, 80))  # ostatnia klatka (8. klatka) coin.png
    coin_icon = pygame.transform.scale(coin_icon, (24, 24))

    # Ikonka dla hp, 2 warianty
    heart_img = pygame.image.load("images/interface/heart.png").convert_alpha()
    heart_full = heart_img.subsurface((0, 0, 16, 16))
    heart_full = pygame.transform.scale(heart_full, (24, 24))
    heart_half = heart_img.subsurface((16, 0, 16, 16))
    heart_half = pygame.transform.scale(heart_half, (24, 24))

    # Tło dla punktacji i numeru fali
    sign_img = pygame.image.load("images/interface/interface.png").convert_alpha()
    sign_img = pygame.transform.scale(sign_img, (100, 40))

    #Tło dla tekstów w oknach menu (do importowania), nie używane w obecnym pliku
    menus_bg_img = pygame.image.load("images/interface/menus.png").convert_alpha()
    menus_bg_img = pygame.transform.smoothscale(menus_bg_img, (400, 150))

    return coin_icon, heart_full, heart_half, sign_img, menus_bg_img


class GameManager:
    """Główna klasa zarządzająca grą."""
    def __init__(self, screen, difficulty = "Normal"):
        self.screen = screen
        self.difficulty = difficulty
        self.gold = START_GOLD
        self.hp = START_HP
        self.score = 0
        self.wave_number = 1

        self.enemies = []  # lista przeciwników
        self.towers = []   # lista wież
        self.bullets = []  # lista pocisków
        self.spawn_queue = []

        self.spawn_cooldown = 0
        self.spawn_delay = 1  # sekundy między kolejnymi przeciwnikami
        self.wave_timer = 1  # czas do kolejnej fali
        self.wave_delay = 10 # domyślny czas między falami (edit)
        self.waiting_for_wave = False

        self.max_towers = TOTAL_TOWER_NUMBER #Liczba wież do postawienia
        self.used_slots = []
        self.evolution_menu = None

        self.font = pygame.font.SysFont("arial", 20)
        self.big_font = pygame.font.SysFont("arial", 40)
        self.map_builder = MapBuilder() # Budowa mapy

        # Wczytanie grafik interfejsu
        self.coin_icon, self.heart_full, self.heart_half, self.sign_img, _ = interface_images()

        self.spawn_wave() # Rozpoczęcie fali

    def handle_event(self, event):
        """Obsługuje zdarzenia w grze."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.evolution_menu:
                chosen = self.evolution_menu.handle_click(event.pos)
                if chosen:
                    # Ewolucja wybranej wieży
                    for i, tower in enumerate(self.towers):
                        if tower is self.evolution_menu.tower:
                            evolved = tower.evolve(chosen)
                            evolved.level = 4
                            self.gold -= tower.upgrade_cost + 50
                            self.towers[i] = evolved
                            break
                    self.evolution_menu = None
                else:
                    self.evolution_menu = None
                return

            x, y = event.pos

            # Budowa wieży
            if event.button == 1:  # LPM
                closest_slot = min(TOWER_SLOTS, key=lambda pos: math.hypot(pos[0] - x, pos[1] - y))
                if closest_slot not in self.used_slots \
                    and math.hypot(closest_slot[0] - x, closest_slot[1] - y) < 40 \
                    and self.gold >= TOWER_BASE_COST \
                    and len(self.towers) < self.max_towers:

                    self.gold -= TOWER_BASE_COST
                    self.towers.append(Tower(*closest_slot))
                    self.used_slots.append(closest_slot)
            
            # Sprzedaż wieży
            elif event.button == 2: #scroll
                for i, tower in enumerate(self.towers):
                    if math.hypot(tower.x - x, tower.y - y) <= tower.radius:
                        self.gold += tower.sell_value() # dodanie wartości sprzedaży do posiadanych środków
                        slot_pos = (tower.x, tower.y)
                        if slot_pos in self.used_slots:
                            self.used_slots.remove(slot_pos) # zwolnienie slota
                        self.towers.pop(i) # usunięcie wieży
                        break
            
            # Ulepszanie/ewolucja wieży
            elif event.button == 3:  # PPM
                for i, tower in enumerate(self.towers):
                    if math.hypot(tower.x - x, tower.y - y) <= tower.radius: # czy kliknięto w wieże
                        
                        # Ulepszanie wieży 
                        if tower.level < 3 and self.gold >= tower.upgrade_cost:
                            self.gold -= tower.upgrade_cost
                            tower.upgrade()

                        # Ewolucja wieży
                        elif tower.level == 3 and self.gold >= tower.upgrade_cost + 50:
                            self.evolution_menu = EvolutionMenu(tower) # Otwarcie menu ewolucji
                            break

    def update(self, dt):
        """Aktualizuje stan gry."""
        self.update_enemies(dt)

        for tower in self.towers:
            tower.update(dt, self.enemies, self.bullets)

        self.update_wave_timers(dt)
        self.update_spawn_queue(dt)

        for bullet in self.bullets:
            bullet.update(dt)

        # Usuwanie pocisków, które trafiły
        self.bullets = [b for b in self.bullets if not b.hit]

        # Aktualizacja animacji mapy
        self.map_builder.update_animation(dt)

    def update_enemies(self, dt):
        """Aktualizuje wrogów, usuwa zabitych i nalicza nagrody."""
        survivors = []

        # Obrażenia zadawane przez moby
        enemy_dmg = \
        {
            "normal" : 15,
            "fast" : 10,
            "tank" : 25
        }

        # Nagrody za pokonanie moba (gold, punkty)
        enemy_drop = \
        {
            "normal" : (20, 25),
            "fast" : (30, 50),
            "tank" : (40, 100)
        }

        for enemy in self.enemies:
            enemy.update(dt)

            # przeciwnik dotarł do końca - zadaj dmg
            if enemy.reached_end:
                self.hp -= enemy_dmg.get(enemy.name, 0)
                continue

            # Pokonanie przeciwnika - dodaj nagrody
            if enemy.is_dead():
                gold_reward, score_reward = enemy_drop.get(enemy.name, (0,0))
                self.gold += gold_reward
                self.score += score_reward
            else:
                survivors.append(enemy)
        self.enemies = survivors

    def update_wave_timers(self, dt):
        """Obsługuje licznik fali i uruchamianie nowej fali."""

        if not self.enemies and not self.waiting_for_wave and not self.spawn_queue:
            SOUNDS["wave_cleared"].play()
            self.waiting_for_wave = True
            self.wave_timer = self.wave_delay          

        if self.waiting_for_wave:
            self.wave_timer -= dt
            if self.wave_timer <= 0:
                self.wave_number += 1
                self.spawn_wave()
                self.waiting_for_wave = False

    def update_spawn_queue(self, dt):
        """Stopniowo wypuszcza przeciwników z kolejki."""
        if self.spawn_queue:
            self.spawn_cooldown -= dt
            if self.spawn_cooldown <= 0:
                self.enemies.append(self.spawn_queue.pop(0))
                self.spawn_cooldown = self.spawn_delay

    def draw(self):
        """Rysuje scenę gry."""
        self.screen.fill(WHITE) #wypełnienie tła
        self.map_builder.draw_map(self.screen,True) # rysowanie mapy

        # Rysowanie ścieżki mobów
        # for i in range(len(ENEMY_PATH)-1):
        #     pygame.draw.line(self.screen, (150,150,150), ENEMY_PATH[i], ENEMY_PATH[i+1], 10)

        # Rysowanie wież
        for tower in self.towers:
            tower.draw(self.screen)

        # Rysowanie mobów
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Rysowanie strzał
        for bullet in self.bullets:
            bullet.draw(self.screen)

        self.draw_interface() # rysowanie interfejsu

    def draw_interface(self):
        """Rysuje interfejs: złoto, HP, punktacja, fala."""
        # GOLD
        self.screen.blit(self.coin_icon, (10, 10))
        gold_text = self.font.render(str(self.gold), True, (0, 0, 0))
        self.screen.blit(gold_text, (40, 12))

        # HP
        if self.hp > START_HP / 2:
            heart_img = self.heart_full
        else:
            heart_img = self.heart_half

        self.screen.blit(heart_img, (10, 40))
        hp_text = self.font.render(str(self.hp), True, (0, 0, 0))
        self.screen.blit(hp_text, (40, 42))

        # POLA STATYSTYK (score, wave)
        self.draw_stat_box(f"Score: {self.score}", (0, 80))
        self.draw_stat_box(f"Wave: {self.wave_number}", (0, 130))
        
        # Komunikat o nadchodzącej fali
        if self.waiting_for_wave:
            ready_text = self.big_font.render("Next wave incoming...", True, (255, 200, 100))
            self.screen.blit(ready_text, (WIDTH//2 - ready_text.get_width()//2, 20))
        
        # Rysowanie menu ewolucji
        if self.evolution_menu:
            self.evolution_menu.draw(self.screen)

        # for slot in TOWER_SLOTS:
        #     color = (180, 180, 180) if slot not in self.used_slots else (100, 100, 100)
        #     pygame.draw.circle(self.screen, color, slot, 20, 2)

    def draw_stat_box(self, text, pos):
        """Rysuje pojedyncze pole dla statystyki (score/wave)"""
        mouse_pos = pygame.mouse.get_pos()
        padding_x = 20
        padding_y = 10

        # Przygotowanie tekstu
        txt_surface = self.font.render(text, True, (0, 0, 0))
        txt_rect = txt_surface.get_rect()

        # Obliczanie rozmiaru tła
        bg_width = txt_rect.width + padding_x * 2
        bg_height = txt_rect.height + padding_y * 2
        bg_rect = pygame.Rect(pos, (bg_width, bg_height))

        # efekt przezroczystości
        hover_score_alpha = 150 if bg_rect.collidepoint(mouse_pos) else 255 

        # Przygotowanie tła
        txt_bg = pygame.transform.scale(self.sign_img, (bg_width, bg_height)).copy()
        txt_bg.set_alpha(hover_score_alpha)
        txt_surface.set_alpha(hover_score_alpha)

        # Rysowanie
        self.screen.blit(txt_bg, pos)
        self.screen.blit(txt_surface, (
            pos[0] + (bg_width - txt_rect.width) // 2,
            pos[1] + (bg_height - txt_rect.height) // 2))

    def spawn_wave(self):
        """Tworzy nową falę przeciwników."""
        SOUNDS["wave_start"].play()

        count = 5 + (self.wave_number * 2)  # Liczba przeciwników w fali
        enemy_types = [Enemy, FastEnemy, TankEnemy] # Typy przeciwników
    
    # Szansa na typy wrogów zmienia się z kolejnymi falami
        if self.wave_number >= 10:
            weights = [0.4, 0.3, 0.3]
        elif self.wave_number >= 5:
            weights = [0.6, 0.3, 0.1]
        else:
            weights = [0.9, 0.1, 0.0]

        # Generowanie kolejki przeciwników
        self.spawn_queue = \
        [
            random.choices(enemy_types, weights=weights)[0](difficulty=self.difficulty)
            for _ in range(count)
        ]
