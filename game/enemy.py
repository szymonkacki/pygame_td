# game/enemy.py

import pygame, math, os
from config import ENEMY_PATH
from game.assets import SOUNDS

# Stałe dla animacji
FRAME_WIDTH = 48
FRAME_HEIGHT = 48
FRAMES_PER_ANIMATION = 6
ANIMATION_SPEED = 0.15

COIN_FRAMES = 8
COIN_ANIMATION_SPEED = 0.1

class Enemy:
    """Klasa bazowa przeciwnika."""
    def __init__(self, difficulty='Normal', name = "normal"):
        self.name = name
        self.path = ENEMY_PATH
        self.current_point = 0
        self.x, self.y = self.path[0]
        
        self.speed = 80
        self.max_hp = 250
        self.hp = self.max_hp
        self.radius = 15
        self.reached_end = False
        self.slow_timer = 0
        self.speed_factor = 1.0


        if difficulty == 'Hard':
            self.hp *= 2
            self.max_hp *= 2

        self.animations = {}
        self.state = 'move'
        self.direction = 'down'
        self.animation_frame = 0
        self.animation_timer = 0
        self.death_timer = 0
        self.death_duration = FRAMES_PER_ANIMATION * ANIMATION_SPEED

        self.coin_frames = []
        self.coin_animation_frame = 0
        self.coin_animation_timer = 0
        self.coin_spawned = False
        self.coin_offset_y = 0  # do przesuwania monety w górę
        self.coin_scale = 0.2

        self.load_animations()
        self.load_coin_animation()

    def load_animations(self):
        """Wczytuje animacje dla ruchu przeciwników"""
        actions = ['move', 'death']
        directions = ['up', 'down', 'left']

        for action in actions:
            for direction in directions:
                path = f"images/enemies/{self.name}/{self.name}_{action}_{direction}.png"
                if not os.path.exists(path):
                    continue
                image = pygame.image.load(path).convert_alpha()
                frames = []
                for i in range(FRAMES_PER_ANIMATION):
                    frame = image.subsurface((i * FRAME_WIDTH, 0, FRAME_WIDTH, FRAME_HEIGHT))
                    frames.append(frame)
                self.animations[f"{action}_{direction}"] = frames

    def load_coin_animation(self):
        """Wczytuje animacje monety"""
        coin_sheet = pygame.image.load("images/interface/coin.png").convert_alpha()
        frame_size = coin_sheet.get_width() // COIN_FRAMES # Oblicz rozmiar pojedynczej klatki
        scaled_size = int(frame_size * self.coin_scale)    # Oblicz nowy rozmiar po skalowaniu
            
        for i in range(COIN_FRAMES):
            # Wycinanie klatki z arkusza
            frame = coin_sheet.subsurface((i * frame_size, 0, frame_size, 
                                           frame_size))
                
            # Skalowanie klatek
            if self.coin_scale != 1.0:
                frame = pygame.transform.scale(frame, (scaled_size, scaled_size))
                self.coin_frames.append(frame)


    def update(self, dt):
        """Aktualizuje stan przeciwnika na podstawie jego aktualnego stanu"""
        if self.state == 'death':
            self.update_death(dt)
        else:
            self.update_move(dt)


    def update_death(self, dt):
        """Aktualizacja stanu śmierci przeciwnika"""
        self.death_timer -= dt
        self.animation_timer += dt
        if self.animation_timer >= ANIMATION_SPEED:
            self.animation_timer = 0
            self.animation_frame = min(self.animation_frame + 1, FRAMES_PER_ANIMATION - 1)

        # Uruchamianie animacji monety po 3 klatce animacji śmierci
        if not self.coin_spawned and self.animation_frame >= 3:
            self.coin_spawned = True
            self.coin_animation_frame = 0
            self.coin_offset_y = 0

        # Aktualizacja animacji monety
        if self.coin_spawned:
            self.update_coin_anim(dt)

    def update_coin_anim(self, dt):
        """Aktualizuje animację monety wypadającej z przeciwnika."""
        self.coin_animation_timer += dt
        self.coin_offset_y -= 30 * dt  # Przesuń monetę w górę
           
        if self.coin_animation_timer >= COIN_ANIMATION_SPEED:
            self.coin_animation_timer = 0
            self.coin_animation_frame = (self.coin_animation_frame + 1) % len(self.coin_frames)

    def update_move(self, dt):
        """Aktualizuje pozycję i animację podczas ruchu przeciwnika."""
        if self.current_point >= len(self.path) - 1:
            self.reached_end = True
            return

        target_x, target_y = self.path[self.current_point + 1]
        dir_x, dir_y, distance = self.calculate_direction(target_x, target_y)

        if distance < 3:
            self.current_point += 1
            return

        if abs(dir_y) > abs(dir_x):
            self.direction = 'up' if dir_y < 0 else 'down'
        else:
            self.direction = 'left' if dir_x < 0 else 'right'

        if self.slow_timer > 0:
            self.slow_timer -= dt
        else:
            self.speed_factor = 1.0

        self.x += dir_x * self.speed * self.speed_factor * dt
        self.y += dir_y * self.speed * self.speed_factor * dt

        self.animation_timer += dt
        if self.animation_timer >= ANIMATION_SPEED:
            self.animation_timer = 0
            self.animation_frame = (self.animation_frame + 1) % FRAMES_PER_ANIMATION

    def calculate_direction(self, target_x, target_y):
        """Oblicza kierunek ruchu przeciwnika w stronę celu."""
        dir_x = target_x - self.x
        dir_y = target_y - self.y
        distance = math.hypot(dir_x, dir_y)

        if distance != 0:
            dir_x /= distance
            dir_y /= distance

        return dir_x, dir_y, distance

    def draw(self, screen):
        """Rysuje odpowiednie elementy na ekranie."""

        # Rysowanie mobów
        self.draw_anim(screen)

        # Rysowanie monety
        if self.state == 'death' and self.coin_spawned and self.coin_frames:
            self.draw_coin(screen)
        
        # Rysowanie paska hp
        self.draw_hp_bar(screen)
  

    def draw_anim(self, screen):
        """Rysuje animację przeciwnika"""
        key = f"{self.state}_{self.direction}"
        frames = self.animations.get(key)

        if self.direction == 'right': # Dla 'right' użycie 'left' z odbiciem
            frames = self.animations.get(f"{self.state}_left")

        if frames:
            frame = frames[self.animation_frame]
            if self.direction == "right":
                frame = pygame.transform.flip(frame, True, False)
            screen.blit(frame, (self.x - FRAME_WIDTH // 2, self.y - FRAME_HEIGHT // 2))

    def draw_coin(self, screen):
        """Rysuje animację monety nad martwym przeciwnikiem."""
        coin_frame = self.coin_frames[self.coin_animation_frame]
        coin_rect = coin_frame.get_rect()
        screen.blit(coin_frame, (self.x - coin_rect.width // 2, self.y - coin_rect.height - 20 + self.coin_offset_y))

    def draw_hp_bar(self, screen):
        """Rysuje pasek zdrowia przeciwnika."""
        hp_ratio = self.hp / self.max_hp
        pygame.draw.rect(screen, (0, 0, 0), (self.x - 15, self.y - 25, 30, 5))
        pygame.draw.rect(screen, (0, 255, 0), (self.x - 15, self.y - 25, 30 * hp_ratio, 5))

    def is_dead(self):
        """Sprawdza czy przeciwnik jest martwy."""
        if self.hp <= 0 and self.state != "death":
            self.state = 'death'
            self.animation_frame = 0
            self.death_timer = self.death_duration
            SOUNDS["enemy_death"].play()
            return False
        return self.hp <= 0 and self.state == "death" and self.death_timer <= 0
    
    def apply_slow(self, duration, factor):
        """Nakłada efekt spowolnienia na przeciwnika."""
        self.slow_timer = duration
        self.speed_factor = min(self.speed_factor, factor)


class FastEnemy(Enemy):
    """Klasa szybkiego przeciwnika."""
    def __init__(self, difficulty='Normal'):
        super().__init__(difficulty)
        self.name = "fast"
        self.speed = 200
        self.max_hp = 150
        self.hp = self.max_hp
        self.radius = 10

        if difficulty == 'Hard':
            self.hp *= 2
            self.max_hp *= 2
        
        self.load_animations()


class TankEnemy(Enemy):
    """Klasa przeciwnika o wysokiej wytrzymałości."""
    def __init__(self, difficulty='Normal'):
        super().__init__(difficulty)
        self.name = "tank"
        self.speed = 30
        self.max_hp = 600
        self.hp = self.max_hp
        self.radius = 20

        if difficulty == 'Hard':
            self.hp *= 2
            self.max_hp *= 2

        self.load_animations()

