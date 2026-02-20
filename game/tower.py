# game/tower.py

import pygame, math, os
from game.effects import FireZone
from game.bullet import Bullet, IceBullet, ARROW_ANIMATIONS
from config import TOWER_BASE_COST
from game.assets import SOUNDS

BASE_FRAME_WIDTH = 70
BASE_FRAME_HEIGHT = 70
ANIMATION_SPEED = 0.15
ARCHER_FRAME_WIDTH = ARCHER_FRAME_HEIGHT = 48

class Tower:
    """Klasa bazowa wieży"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.range = 120
        self.damage = 40
        self.reload_time = 1.0  # sekundy między strzałami
        self.fire_rate = 1 / self.reload_time

        self.radius = 20
        self.level = 1
        self.upgrade_cost = 50
        self.cooldown = 0.0

        self.shot_pending = False
        self.target_pending = None
        self.bullets_pending = None
        self.shot_frame = 2

        self.archer_state = "idle"
        self.archer_direction = "down"
        self.archer_flipped = False
        self.archer_frame = 0
        self.archer_animation_timer= 0
        self.archer_offsets_y = \
        {
            1: -24,
            2: -32,
            3: -32,
            4: -32
        } #offsety łucznika względem podstawy
        self.archer_offset_y = self.archer_offsets_y.get(self.level, -32)

        self.base_animation_timer = 0
        self.base_frame = 0
        self.base_animations = []
        self.archer_animations = {}

        self.load_images()

    def load_images(self):
        """Wczytuje animacje podstawy i łucznika z plików."""

        # Wczytaj obrazy podstawy
        for lvl in range(1, 5):
            path = f"images/towers/{lvl}.png"
            if os.path.exists(path):
                img = pygame.image.load(path).convert_alpha()
                frames = []

                # Określ liczbę klatek na podstawie poziomu
                frames_count = 4 if lvl in [1, 2] else 6
                frame_width = img.get_width() // frames_count
                frame_height = img.get_height()
                
                for i in range(frames_count):
                    frame = img.subsurface((i * frame_width, 0, frame_width, frame_height))
                    frames.append(frame)
                
                self.base_animations.append(frames)

        # Wczytaj animacje łucznika
        actions = ["attack", "idle"]
        directions = ["down", "left", "up"]

        for action in actions:
            for direction in directions:
                key = f"{action}_{direction}"
                path = f"images/towers/archer/{key}.png"

                if os.path.exists(path):
                    img = pygame.image.load(path).convert_alpha()
                    
                    # Określ liczbę klatek na podstawie akcji
                    frames_number = 4 if action == "idle" else 6
                    frame_width = img.get_width() // frames_number

                    frames = []
                    for i in range(frames_number):
                        frame = img.subsurface((i * frame_width, 0, frame_width, img.get_height()))
                        frames.append(frame)
                    
                    self.archer_animations[key] = frames

    def get_base_animation(self):
        """Zwraca obraz podstawy odpowiedni dla poziomu wieży"""
        level_index = min(self.level - 1, len(self.base_animations) - 1)
        if level_index < 0 or level_index >= len(self.base_animations):
            return None
        return self.base_animations[level_index]

    def get_archer_animation(self):
        """Zwraca aktualną animację łucznika"""
        key = f"{self.archer_state}_{self.archer_direction}"
        return self.archer_animations.get(key)
    
    def set_direction(self, target):
        """Ustawia kierunek łucznika względem celu"""
        dx = target.x - self.x
        dy = target.y - self.y
        
        if abs(dx) > abs(dy):
            self.archer_direction = "left"
            self.archer_flipped = dx > 0
        else:
            self.archer_direction = "up" if dy < 0 else "down"
            self.archer_flipped = False

    def update_animation(self, dt):
        """Aktualizuje stan animacji"""
        base_animation = self.get_base_animation()
        if base_animation:
            self.base_animation_timer += dt
            if self.base_animation_timer >= ANIMATION_SPEED:
                self.base_animation_timer = 0
                self.base_frame = (self.base_frame + 1) % len(base_animation)

        archer_animation = self.get_archer_animation()
        if archer_animation:
            self.archer_animation_timer += dt
            if self.archer_animation_timer >= ANIMATION_SPEED:
                self.archer_animation_timer = 0
                self.archer_frame = (self.archer_frame + 1) % len(archer_animation)
                

            if self.archer_state == "attack" and self.archer_frame == self.shot_frame:
                if self.shot_pending and self.target_pending:
                    self.fire_at_target(self.target_pending, self.bullets_pending)
                    self.cooldown = 1 / self.fire_rate
                    self.shot_pending = False
                    self.target_pending = None

            # Po zakończeniu animacji ataku powrót do idle
            if self.archer_state == "attack" and self.archer_frame >= 3 and not self.shot_pending:
                self.archer_state = "idle"
                self.archer_frame = 0

    def update(self, dt, enemies, bullets=None):
        """Aktualizuje stan wieży."""
        self.bullets_pending = bullets
        # animacja łucznika
        self.cooldown -= dt
        self.update_animation(dt)

        if self.cooldown <= 0 and not self.shot_pending:
            target = self.get_target(enemies)
            if target: #and not self.shot_pending:
                self.set_direction(target)
                self.archer_state = "attack"
                self.archer_frame = 0
                self.target_pending = target
                self.shot_pending = True

    def fire_at_target(self, target, bullets):
        """Tworzy pocisk w kierunku celu"""
        SOUNDS["arrow"].play()
        if bullets is not None:
            # Oblicz pozycję startową pocisku
            start_x, start_y = self.get_bullet_start_pos()
            bullets.append(Bullet(start_x, start_y, target, damage=self.damage))

    def get_bullet_start_pos(self):
        """Zwraca pozycję startową pocisku"""
        # Domyślna pozycja - środek wieży
        x, y = self.x, self.y + self.archer_offset_y
        
        # Dostosuj pozycję w zależności od kierunku
        if self.archer_direction == "up":
            y -= 20
        elif self.archer_direction == "down":
            y += 10
        elif self.archer_direction == "left":
            if self.archer_flipped:
                x += 20
            else:
                x -= 25
            
        return x, y

    def get_target(self, enemies):
        """Wybiera cel w zasięgu o najmniejszym HP."""
        enemies_in_range = [ e for e in enemies if e.hp > 0 and self.distance_to(e) <= self.range]
        return min(enemies_in_range, key=lambda e: e.hp, default=None)
       
    def distance_to(self, enemy):
        """Oblicza odległość do przeciwnika"""
        return math.hypot(enemy.x - self.x, enemy.y - self.y)

    def sell_value(self):
        """Oblicza wartość sprzedaży wieży."""
        base = TOWER_BASE_COST
        upgrades_total = 0

        if self.level >= 2:
            upgrades_total += 50
        if self.level >= 3:
            upgrades_total += 100
        if self.level == 4:
            upgrades_total += 200

        return int(base + upgrades_total * 0.5) #baza + 50% ulepszeń

    def upgrade(self):
        """Ulepsza wieżę na wyższy poziom."""
        if self.level < 3:
            self.level += 1
            self.range *= 1.2
            self.damage *= 1.2
            self.reload_time *= 0.9  # szybciej strzela
            self.upgrade_cost += 50  # wzrost kosztu kolejnego ulepszenia
            self.fire_rate = 1 / self.reload_time

            # Reset stanu animacji
            self.base_frame = 0
            self.shot_pending = False
            self.target_pending = None



    def evolve(self, type_name):
        """Ewoluuje wieżę do wybranego typu."""
        if type_name == "FireTower":
            return FireTower(self.x, self.y)
        elif type_name == "IceTower":
            return IceTower(self.x, self.y)
        elif type_name == "SpeedyTower":
            return SpeedyTower(self.x, self.y)
        return self
    
    def draw(self, screen):
        """Rysuje wieżę na ekranie."""
        self.draw_base(screen)
        self.draw_archer(screen)
        self.draw_level(screen)
        self.draw_range(screen)
    
    def draw_base(self, screen):
        """Rysuje podstawę wieży."""
        base_animation = self.get_base_animation()
        if base_animation:
            frame = base_animation[self.base_frame % len(base_animation)]
            base_rect = frame.get_rect(midbottom=(int(self.x - 1), int(self.y + 29)))
            screen.blit(frame, base_rect)


    def draw_archer(self, screen):
        """Rysuje łucznika na szczycie wieży."""
        frames = self.get_archer_animation()
        self.archer_offset_y = self.archer_offsets_y.get(self.level, -32)
        if frames:
            frame = frames[self.archer_frame % len(frames)]

            # Odbicie lustrzane dla prawej strony
            if self.archer_flipped:
                frame = pygame.transform.flip(frame, True, False)

            archer_rect = frame.get_rect(center=(int(self.x - 1), int(self.y + self.archer_offset_y)))
            screen.blit(frame, archer_rect)
        

    def draw_level(self, screen):
        """Rysuje aktualny poziom wieży."""
        font = pygame.font.SysFont("arial", 16)
        level_text = font.render(f"Lv{self.level}", True, (255, 255, 255))
        screen.blit(level_text, (self.x - 10, self.y - 10))

    def draw_range(self, screen):
        """Rysuje zasięg wieży jako półprzezroczyste koło."""
        surface = pygame.Surface((self.range*2, self.range*2), pygame.SRCALPHA)
        pygame.draw.circle(surface, (0, 100, 255, 40), (self.range, self.range), self.range)
        screen.blit(surface, (self.x - self.range, self.y - self.range))

class FireTower(Tower):
    """Wieża ognia, zadająca obrażenia obszarowe"""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = 150
        self.reload_time = 2
        self.fire_rate = 1 / self.reload_time
        self.fire_zones = []

    def fire_at_target(self, target, bullets):
            """Zamiast standardowego pocisku tworzy strefę ognia w miejscu wroga"""
            self.create_fire_zone(target)
            self.archer_state = "attack"
            self.archer_frame = 0
    
    def create_fire_zone(self, target):
        """Tworzy nową strefe ognia"""
        self.fire_zones.append(FireZone(target.x, target.y))

    def update(self, dt, enemies, bullets = None):
        """Aktualizuje stan wieży ognia """

        self.update_animation(dt)

        # aktualizuje strefy ognia
        for zone in self.fire_zones:
            zone.update(dt, enemies)
            if zone.is_expired():
                self.fire_zones.remove(zone)

        self.cooldown -= dt

        # sprawdzenie czy można stworzyć kolejne pole ognia
        if self.cooldown <= 0:
            target = self.get_target(enemies)

            if target:
                self.set_direction(target)
                self.archer_state = "attack"
                self.archer_frame = 0
                self.fire_at_target(target, bullets)
                self.cooldown = 1 / self.fire_rate



    def draw(self, screen):
        """Rysuje wieżę i strefy ognia"""
        super().draw(screen)

        for patch in self.fire_zones:
            patch.draw(screen)

class IceTower(Tower):
    """Lodowa wieża, spowalniająca przeciwników."""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = 150

        self.slow_duration = 2.0
        self.slow_factor = 0.5

    def fire_at_target(self, target, bullets):
        """Wystrzeliwuje lodowy pocisk spowalniający cel."""
        if bullets is not None:
            start_x, start_y = self.get_bullet_start_pos()

            # Utworzenie lodowego pocisku
            bullet = IceBullet(start_x, start_y, target, damage=self.damage,
                slow_duration=self.slow_duration, slow_factor=self.slow_factor)
            
            SOUNDS["arrow"].play()
            bullets.append(bullet)
            self.archer_state = "attack"
            self.archer_frame = 0
    
    def get_target(self, enemies):
        """Wybór za cel, przeciwnika który nie jest spowolniony (priorytet) lub z najmniejszym HP."""

        enemies_in_range = [] #lista wrogow w zasiegu

        for enemy in enemies: #sprawdzanie odleglosci miedzy wieza a wrogiem
            dx = enemy.x - self.x
            dy = enemy.y - self.y
            distance = math.hypot(dx, dy)

            if distance <= self.range: # sprawdzanie czy w zasięgu i czy nie jest juz spowolniony/jedyny
                if enemy.slow_timer <= 0 or len(enemies) == 1:
                    enemies_in_range.append(enemy)

        if enemies_in_range: #atak wroga z najmniejszym hp
            return min(enemies_in_range, key=lambda e: e.hp)

        return None #brak wrogow w zasiegu

class SpeedyTower(Tower):
    """Wieża o zwiększonej szybkostrzelności."""
    def __init__(self, x, y):
        super().__init__(x, y)
        self.range = 150

        self.reload_time = 0.4
        self.fire_rate = 1 / self.reload_time
        self.shot_frame = 1

    def fire_at_target(self, target, bullets):
        """Wystrzeliwuje szybkiego pocisku w stronę celu."""
        if bullets is not None:
            start_x, start_y = self.get_bullet_start_pos()
            bullet = Bullet(start_x, start_y, target)
            bullet.damage = self.damage

            bullet.anim = ARROW_ANIMATIONS.get("speed", [])
            SOUNDS["arrow"].play()
            bullets.append(bullet)

    

class EvolutionMenu:
    """Menu umożliwiające ewolucję wieży do typu specjalnego."""
    def __init__(self, tower):
        self.tower = tower
        self.options = ["FireTower", "IceTower", "SpeedyTower"]
        self.menu_width = 100
        self.button_height = 25
        self.menu_height = self.button_height * len(self.options)
        self.selected_option = None

        self.x = tower.x - self.menu_width // 2

        # domyślnie menu nad wieżą
        self.y = tower.y - self.menu_height - 50

        # jeśli menu nie mieści się nad — przenieś pod wieżę
        if self.y < 0:
            self.y = tower.y + 30

    def handle_click(self, pos):
        """Obsługuje kliknięcie w menu ewolucji."""
        mx, my = pos
        # Sprawdzenie kliknięcia w przycisk
        for i, option in enumerate(self.options):
            bx = self.x
            by = self.y + i * self.button_height
            # Sprawdzenie czy kliknięcie w obszarze przycisku
            if bx <= mx <= bx + self.menu_width and by <= my <= by + self.button_height:
                return option
        return None

    def draw(self, screen):
        """Rysuje menu ewolucji na ekranie"""
        font = pygame.font.SysFont("arial", 16)

        background_colors = \
        {
            "FireTower" : (255,100,100),
            "IceTower": (100, 200, 255),
            "SpeedyTower": (255, 255, 100)
        }

        pygame.draw.rect(screen, (50, 50, 50), (self.x, self.y, self.menu_width, self.menu_height))
        
        # Rysowanie przycisków
        for i, option in enumerate(self.options):
            bx = self.x
            by = self.y + i * self.button_height
            color = background_colors.get(option, (200,200,200))

            pygame.draw.rect(screen, color, (bx, by, self.menu_width, self.button_height))
            pygame.draw.rect(screen, (0, 0, 0), (bx, by, self.menu_width, self.button_height), 2)

            # Tekst przycisków
            label = font.render(option.capitalize(), True, (0, 0, 0))
            text_x = bx + (self.menu_width - label.get_width()) // 2
            text_y = by + (self.button_height - label.get_height()) // 2
            screen.blit(label, (text_x, text_y))

