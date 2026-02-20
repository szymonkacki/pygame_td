# main.py

import pygame, sys
from config import WIDTH, HEIGHT, TILE_SIZE, BLACK, WHITE, GLOBAL_VOLUME
from game.game_manager import GameManager, interface_images
from game.map_builder import MapBuilder
from game.bullet import load_arrow_animations
from game.assets import mute_sounds, unmute_sounds

# Inicjalizacja pygame
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 48)

def draw_menu_background(map_builder, dt, opacity):
    """Wyświetla tło menu z nałożoną ciemną przejrzystą nakładką."""
    map_builder.update_animation(dt)
    map_builder.draw_map(screen)
    
    # Ciemna nakładka
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(opacity)  # Stopień przyciemnienia
    overlay.fill((0, 0, 0))
    screen.blit(overlay, (0, 0))


def draw_title_background(text, offset_y):
    """Rysuje baner tytułowy z wyśrodkowanym tekstem"""

    _, _, _, _, bg_img = interface_images()

    title_surface = font.render(text, True, (255, 255, 255))
    board_rect = bg_img.get_rect(center=(WIDTH // 2, offset_y))
    text_rect = title_surface.get_rect(center=board_rect.center)

    screen.blit(bg_img, board_rect)
    screen.blit(title_surface, text_rect)


# Ustawienia głośności
muted = False
volume = GLOBAL_VOLUME
previous_volume = volume
dragging_slider = False

# Muzyka w tle
pygame.mixer.music.load("sounds/background.mp3")
pygame.mixer.music.set_volume(0.1)
pygame.mixer.music.play(-1)  # zapętlenie


load_arrow_animations()

def draw_volume_slider(current_volume, offset_y = 50):
    """Rysuje suwak głośności oraz przycisk wyciszenia."""
    bar_rect = pygame.Rect(WIDTH - 130, offset_y, 120, 20)
    handle_x = bar_rect.x + int(current_volume * bar_rect.width)
    handle_rect = pygame.Rect(handle_x - 5, bar_rect.y - 5, 10, 30)

    pygame.draw.rect(screen, (100, 100, 100), bar_rect)
    pygame.draw.rect(screen, (200, 200, 200), handle_rect)
    
    vol_text = pygame.font.SysFont(None, 24).render("Głośność", True, (255, 255, 255))
    screen.blit(vol_text, (bar_rect.x, bar_rect.y - 20))

    # Przyciski mute/unmute
    icon_font = pygame.font.SysFont(None, 36)
    icon_img = pygame.image.load("images/effects/volume/muted.png").convert_alpha() if muted else pygame.image.load("images/effects/volume/unmuted.png").convert_alpha()
    icon_img_scaled = pygame.transform.scale(icon_img, (32, 32))
    icon_rect = icon_img_scaled.get_rect()
    icon_rect.topleft = (bar_rect.x - 50, bar_rect.y - 5)
    screen.blit(icon_img_scaled, icon_rect)

    return bar_rect, handle_rect, icon_rect

def handle_volume_slider_click(pos, bar_rect):
    """Zmiana głośności po kliknięciu paska głośności."""
    global muted, previous_volume, volume

    rel_x = pos[0] - bar_rect.x
    rel_x = max(0, min(bar_rect.width, rel_x))  # clamp
    new_volume = rel_x / bar_rect.width

    pygame.mixer.music.set_volume(new_volume)
    volume = new_volume

    if muted:
        muted = False
        previous_volume = new_volume
        unmute_sounds()
    
    return volume

def draw_button(text, rect, color, text_color=(255, 255, 255)):
    """Tworzy przyciski UI."""
    pygame.draw.rect(screen, color, rect, border_radius=20)
    rendered = font.render(text, True, text_color)
    rendered_rect = rendered.get_rect(center=rect.center)
    screen.blit(rendered, rendered_rect)

def draw_menu(map_builder):
    """Tworzy menu wyboru poziomu trudności."""
    global volume

    dt = clock.tick(60) / 1000
    draw_menu_background(map_builder, dt, 160)
    draw_title_background("Choose difficulty", 100)

    normal_button = pygame.Rect(WIDTH//2 - 125, 200, 250, 80)
    hard_button = pygame.Rect(WIDTH//2 - 125, 320, 250, 80)

    draw_button("Normal", normal_button, (0,150,0))
    draw_button("Hard",hard_button, (150,0,0))

    bar_rect, handle_rect, icon_rect = draw_volume_slider(volume, offset_y = 30)

    pygame.display.flip()
    return normal_button, hard_button, bar_rect, icon_rect

def main_menu(map_builder):
    """Główne menu gry umożliwiające zmianę głośności, wybór poziomu trudności lub przejście do gry."""
    global volume, dragging_slider, muted, previous_volume

    while True:
        normal_button, hard_button, vol_bar, mute_rect = draw_menu(map_builder)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if normal_button.collidepoint(event.pos):
                    return "Normal"
                elif hard_button.collidepoint(event.pos):
                    return "Hard"
                elif vol_bar.collidepoint(event.pos):
                    dragging_slider = True
                    volume = handle_volume_slider_click(event.pos, vol_bar)
                elif mute_rect.collidepoint(event.pos):
                    if muted:
                        volume = previous_volume
                        muted = False
                        pygame.mixer.music.set_volume(volume)
                        unmute_sounds()
                    else:
                        previous_volume = volume
                        volume = 0.0
                        muted = True
                        pygame.mixer.music.set_volume(0)
                        mute_sounds()
                    pygame.mixer.music.set_volume(volume)

            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = False
            elif event.type == pygame.MOUSEMOTION and dragging_slider:
                volume = handle_volume_slider_click(event.pos, vol_bar)

        clock.tick(60)

def end_screen(result_text, score, wave):
    """Ekran końcowy z wynikiem gry i opcją zapisu wyniku lub przejścia do menu"""
    saved = False
    small_font = pygame.font.SysFont(None, 36)

    while True:
        screen.fill((30, 30, 30))
  

        draw_title_background(result_text, 100)

        score_surface = small_font.render(f"Wynik końcowy: {score}", True, (255, 255, 255))
        wave_surface = small_font.render(f"Fala: {wave}", True, (255, 255, 255))
        score_rect = score_surface.get_rect(center=(WIDTH // 2, 220))
        wave_rect = wave_surface.get_rect(center=(WIDTH // 2, 260))
        screen.blit(score_surface, score_rect)
        screen.blit(wave_surface, wave_rect)

        if saved:
            confirm_surface = small_font.render("Zapisano wynik do pliku!", True, (0, 255, 0))
            confirm_rect = confirm_surface.get_rect(center=(WIDTH // 2, 320))
            screen.blit(confirm_surface, confirm_rect)

        save_button = pygame.Rect(WIDTH // 2 - 125, 370, 250, 80)
        menu_button = pygame.Rect(WIDTH // 2 - 125, 490, 250, 80)
        exit_button = pygame.Rect(WIDTH // 2 - 125, 610, 250, 80)

        draw_button("Zapisz wynik", save_button, (0, 100, 100))
        draw_button("Menu", menu_button, (0, 120, 255))
        draw_button("Wyjdź", exit_button, (200, 50, 50))
        
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if save_button.collidepoint(event.pos):
                    save_score(score, wave)
                    saved = True
                elif menu_button.collidepoint(event.pos):
                    return "menu"
                elif exit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()

def pause_menu(background):
    """Menu pauzy podczas gry."""
    global volume, dragging_slider, muted, previous_volume
    while True:
        screen.blit(background, (0,0))
        draw_title_background("Pauza", 100)
        bar_rect, handle_rect, mute_rect = draw_volume_slider(volume, offset_y= 30)

        resume_button = pygame.Rect(WIDTH // 2 - 125, 200, 250, 80)
        menu_button = pygame.Rect(WIDTH // 2 - 125, 320, 250, 80)

        draw_button("Kontynuuj", resume_button, (0, 150, 0))
        draw_button("Menu", menu_button, (0, 120, 255))


        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if resume_button.collidepoint(event.pos):
                    return "resume"
                elif menu_button.collidepoint(event.pos):
                    return "menu"
                elif bar_rect.collidepoint(event.pos):
                    dragging_slider = True
                    volume = handle_volume_slider_click(event.pos, bar_rect)
                elif mute_rect.collidepoint(event.pos):
                    if muted:
                        volume = previous_volume
                        muted = False
                        pygame.mixer.music.set_volume(volume)
                        unmute_sounds()
                    else:
                        previous_volume = volume
                        volume = 0.0
                        muted = True
                        pygame.mixer.music.set_volume(0)
                        mute_sounds()
                    pygame.mixer.music.set_volume(volume)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                dragging_slider = False

            elif event.type == pygame.MOUSEMOTION and dragging_slider:
                volume = handle_volume_slider_click(event.pos, bar_rect)
                    
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "resume"
        clock.tick(60)

def start_screen(map_builder):
    """Ekran startowy umożliwiający przejście do gry."""

    while True:
        dt = clock.tick(60) / 1000
        draw_menu_background(map_builder, dt, 230)
        draw_title_background("Tower Defense Game", 100)


        start_button = pygame.Rect(WIDTH // 2 - 125, 200, 250, 80)
        exit_button = pygame.Rect(WIDTH // 2 - 125, 320, 250, 80)

        draw_button("Start", start_button, (0, 150, 0))
        draw_button("Wyjdź", exit_button, (150, 0, 0))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if start_button.collidepoint(event.pos):
                    return "start"
                elif exit_button.collidepoint(event.pos):
                    pygame.quit()
                    sys.exit()


def save_score(score, wave):
    """Zapisuje wynik gry do pliku tekstowego."""
    with open("wynik.txt", "w") as f:
        f.write(f"Niestety poległeś.\n")
        f.write(f"Zostałeś przytłoczony na {wave} fali.\n")
        f.write(f"Twój wynik końcowy to: {score}")

def main():
    """Główna funkcja zarządzająca przepływem gry."""
    map_builder = MapBuilder()
    action = start_screen(map_builder)

    if action == "start":
        difficulty = main_menu(map_builder)

        game = GameManager(screen, difficulty)

        while True:
            dt = clock.tick(60) / 1000  # delta time in sec
            if dt > 0.1:
                dt = 0.1
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    game_ss = screen.copy()
                    action = pause_menu(game_ss)
                    if action == "menu":
                        return main()
                
                else:
                    game.handle_event(event)

            game.update(dt)
            game.draw()
            pygame.display.flip()

            if game.hp <= 0:
                result = end_screen("Game over!", game.score, game.wave_number)
                if result == "menu":
                    return main()
            

if __name__ == "__main__":
    main()

