# game/bullet.py
import pygame, math, os

# Słownik animacji strzał
ARROW_ANIMATIONS = \
{            
    "default": [],
    "ice": [],
    "speed": [],
}

def load_arrow_animations(path="images/effects/arrows/arrows.png", scale_size=(40, 40)):
        """Ładuje animacje strzał z pliku"""
        global ARROW_ANIMATIONS

        if not os.path.exists(path):
            print("Brak pliku ze strzałami:", path)
            return ARROW_ANIMATIONS

        # Wczytanie pliku
        image = pygame.image.load(path).convert()
        image.set_colorkey((255,255,255))

        # Parametry pliku
        frame_cols = 3
        frame_rows = 4
        frame_width = image.get_width() // frame_cols
        frame_height = image.get_height() // frame_rows

        # Przetwarzanie i wyodrębnianie strzał z pliku
        for row in range(3):
            frames = []
            for col in range(3):
                frame = image.subsurface((col * frame_width, row * frame_height, frame_width, frame_height))
                frame = pygame.transform.scale(frame, scale_size)
                frames.append(frame)

            if row == 0:
                ARROW_ANIMATIONS["default"] = frames
            elif row == 1:
                ARROW_ANIMATIONS["ice"] = frames
            elif row == 2:
                ARROW_ANIMATIONS["speed"] = frames

        return ARROW_ANIMATIONS


class Bullet:
    """Klasa bazowa reprezentująca pocisk (strzałe) w grze"""
    def __init__(self, x, y, target, damage=20, speed=300):
        self.x = x
        self.y = y
        self.target = target
        self.damage = damage
        self.speed = speed
        self.radius = 5
        self.hit = False # czy pocisk trafił

        # Animacja pocisku
        self.anim = ARROW_ANIMATIONS.get("default", [])
        self.anim_index = 0
        self.anim_timer = 0
        self.anim_speed = 0.15

        self.start_x = x
        self.start_y = y
        
    def update(self, dt):
        """Aktualizuje stan pocisku."""
        if not self.target or self.target.is_dead():
            self.hit = True
            return

        if self.over_max_distance():
            self.hit = True
            return

        dx, dy, distance = self.calculate_direction()

        
        if distance < self.radius + self.target.radius:
            self.apply_hit_effect()
            return


        self.x += dx * self.speed * dt
        self.y += dy * self.speed * dt

        self.update_animation(dt)

    def draw(self, screen):
        """Rysuje pocisk na ekranie."""
        if self.anim:
            frame = self.anim[self.anim_index % len(self.anim)]
            angle = self.angle_to_target()
            rotated_frame = pygame.transform.rotate(frame, angle)
            rect = rotated_frame.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(rotated_frame, rect)

    def angle_to_target(self):
        """Oblicza kąt do celu dla rotacji animacji."""
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        return math.degrees(math.atan2(-dy, dx))
    
    def over_max_distance(self):
        """Sprawdza czy pocisk przekroczył maksymalny dozwolony dystans."""
        traveled_distance = math.hypot(self.x - self.start_x, self.y - self.start_y)
        return traveled_distance > 200  #max 200 pikseli
    
    def apply_hit_effect(self):
        """Efekt trafienia w cel."""
        self.target.hp -= self.damage
        self.hit = True

    def calculate_direction(self):
        """Oblicza kierunek ruchu pocisku w stronę celu."""
        dx = self.target.x - self.x
        dy = self.target.y - self.y
        distance = math.hypot(dx, dy)

        if distance != 0:
            dx /= distance
            dy /= distance

        return dx, dy, distance
    
    def update_animation(self, dt):
        """Aktualizuje animację pocisku."""
        if self.anim:
            self.anim_timer += dt
            if self.anim_timer >= self.anim_speed:
                self.anim_timer = 0
                self.anim_index = (self.anim_index + 1) % len(self.anim)
    



class IceBullet(Bullet):
    """Klasa pocisku lodowego (spowalnia cel)."""
    def __init__(self, x, y, target, damage = 40, slow_duration=2.0, slow_factor=0.5):
        super().__init__(x, y, target, damage)
        self.slow_duration = slow_duration
        self.slow_factor = slow_factor
        self.anim = ARROW_ANIMATIONS.get("ice", [])


    def apply_hit_effect(self):
            """Efekt trafienia w cel z nałożeniem spowolnienia."""
            self.target.hp -= self.damage
            self.target.apply_slow(self.slow_duration, self.slow_factor)
            self.hit = True
