#game/effects.py
import pygame, math, os

class FireZone:
    """Klasa reprezentująca strefę ognia tworzoną przez FireTower"""
    def __init__(self, x, y, radius=50, duration=3.0, damage_per_second=70):
        self.x = x
        self.y = y
        self.radius = radius
        self.duration = duration
        self.timer = 0.0
        self.damage_per_second = damage_per_second

        self.frames = []
        self.current_frame = 0
        self.frame_timer = 0.0
        self.frame_speed = 0.15

        self.load_animation()

    def load_animation(self):
        """Ładuje animowaną grafikę strefy ognia"""
        path = "images/effects/firezone"
        i = 1
        while True:
            frame_path = os.path.join(path, f"firezone_f{i}.png")
            if not os.path.exists(frame_path):
                break
            image = pygame.image.load(frame_path).convert_alpha()
            scaled_image = pygame.transform.scale(image, (self.radius * 2, self.radius * 2))
            self.frames.append(scaled_image)
            i += 1

        if not self.frames:
            # fallback jeśli brak grafiki
            surf = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)
            pygame.draw.circle(surf, (255, 100, 0, 100), (self.radius, self.radius), self.radius)
            self.frames.append(surf)

    def update(self, dt, enemies):
        """Aktualizuje stan strefy ognia"""
        self.timer += dt

        # Zadawanie obrażeń przeciwnikom w strefie
        for enemy in enemies:
            if math.hypot(enemy.x - self.x, enemy.y - self.y) <= self.radius:
                enemy.hp -= self.damage_per_second * dt

        self.frame_timer += dt
        # Aktualizacja animacji
        if self.frame_timer >= self.frame_speed:
            self.frame_timer = 0
            self.current_frame = (self.current_frame + 1) % len(self.frames)

    def draw(self, screen):
        """Renderuje strefę ognia na ekranie"""
        frame = self.frames[self.current_frame]
        rect = frame.get_rect(center=(self.x, self.y))
        screen.blit(frame, rect)

    def is_expired(self):
        """Sprawdza czy strefa ognia wygasła"""
        return self.timer >= self.duration