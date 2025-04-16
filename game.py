# Eagle Eyes - Cowboy Duel Game (Enhanced Version)
import pygame
import random
import csv
import time
import os

# Initialize Pygame
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Eagle Eyes")
font = pygame.font.SysFont(None, 48)
clock = pygame.time.Clock()

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
SKIN = (255, 220, 177)
DARK_BLUE = (0, 0, 139)
HAT = (160, 82, 45)
YELLOW = (255, 255, 0)

# ---------------------------- Classes ----------------------------
class Timer:
    def __init__(self):
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()

    def stop(self):
        self.end_time = time.time()

    def get_reaction_time(self):
        if self.start_time and self.end_time:
            return round(self.end_time - self.start_time, 3)
        return 0


class Weapon:
    def __init__(self, name, damage, accuracy, fire_rate=500, ammo=6):
        self.name = name
        self.damage = damage
        self.accuracy = accuracy
        self.fire_rate = fire_rate  # Time between shots in ms
        self.max_ammo = ammo
        self.current_ammo = ammo
        self.last_shot_time = 0
        
    def can_fire(self):
        now = pygame.time.get_ticks()
        return (now - self.last_shot_time > self.fire_rate and 
                self.current_ammo > 0)
                
    def fire(self):
        if self.can_fire():
            self.last_shot_time = pygame.time.get_ticks()
            self.current_ammo -= 1
            return random.random() <= self.accuracy
        return False

    def reload(self):
        self.current_ammo = self.max_ammo


class Player:
    def __init__(self, name="Player"):
        self.name = name
        self.score = 0
        self.health = 100
        self.max_health = 100
        self.reaction_time = 0
        self.weapon = Weapon("Revolver", damage=50, accuracy=0.8)
        self.rect = pygame.Rect(100, 300, 50, 100)
        self.is_shooting = False

    def draw_gun(self):
        pass

    def shoot(self):
        return self.weapon.fire()

    def update_score(self, amount):
        self.score += amount

    def draw(self, surface):
        x, y, w, h = self.rect
        pygame.draw.rect(surface, BROWN, (x + 10, y + 30, 30, 50))
        pygame.draw.circle(surface, SKIN, (x + 25, y + 20), 15)
        pygame.draw.rect(surface, HAT, (x + 10, y + 5, 30, 10))
        pygame.draw.rect(surface, HAT, (x + 5, y + 15, 40, 5))
        pygame.draw.rect(surface, DARK_BLUE, (x + 10, y + 80, 10, 20))
        pygame.draw.rect(surface, DARK_BLUE, (x + 30, y + 80, 10, 20))
        
        # Draw gun with animation when shooting
        if self.is_shooting:
            pygame.draw.line(surface, YELLOW, (x + 40, y + 50), (x + 70, y + 40), 3)
            self.is_shooting = False
        else:
            pygame.draw.line(surface, (192, 192, 192), (x + 40, y + 50), (x + 50, y + 50), 3)


class Opponent:
    def __init__(self, difficulty=5):
        self.difficulty_level = difficulty
        self.health = 100
        self.max_health = 100
        self.reaction_time = self.random_reaction_time()
        self.weapon = Weapon("Revolver", damage=50, accuracy=0.7)
        self.rect = pygame.Rect(650, 300, 50, 100)
        self.is_shooting = False

    def draw_gun(self):
        pass

    def shoot(self):
        # Make accuracy scale with difficulty
        accuracy_boost = min(0.3, self.difficulty_level * 0.03)
        if self.weapon.can_fire():
            self.weapon.last_shot_time = pygame.time.get_ticks()
            self.weapon.current_ammo -= 1
            self.is_shooting = True
            return random.random() <= (self.weapon.accuracy + accuracy_boost)
        return False

    def random_reaction_time(self):
        # More granular difficulty scaling
        base = max(0.1, 1.0 - self.difficulty_level * 0.08)
        variation = max(0.05, 0.3 - self.difficulty_level * 0.02)
        return round(random.uniform(base, base + variation), 2)

    def draw(self, surface):
        x, y, w, h = self.rect
        pygame.draw.rect(surface, BROWN, (x + 10, y + 30, 30, 50))
        pygame.draw.circle(surface, SKIN, (x + 25, y + 20), 15)
        pygame.draw.rect(surface, HAT, (x + 10, y + 5, 30, 10))
        pygame.draw.rect(surface, HAT, (x + 5, y + 15, 40, 5))
        pygame.draw.rect(surface, DARK_BLUE, (x + 10, y + 80, 10, 20))
        pygame.draw.rect(surface, DARK_BLUE, (x + 30, y + 80, 10, 20))
        
        # Draw gun with animation when shooting
        if self.is_shooting:
            pygame.draw.line(surface, YELLOW, (x - 10, y + 50), (x - 40, y + 40), 3)
            self.is_shooting = False
        else:
            pygame.draw.line(surface, (192, 192, 192), (x - 10, y + 50), (x, y + 50), 3)


class MainMenu:
    def __init__(self):
        self.font_large = pygame.font.SysFont("Arial", 64)
        self.font_small = pygame.font.SysFont("Arial", 32)
        self.options = ["Start Game", "How to Play", "Quit"]
        self.selected = 0
        self.show_instructions = False
        
    def draw(self, surface):
        surface.fill(BLACK)
        # Draw title
        title = self.font_large.render("EAGLE EYES", True, WHITE)
        surface.blit(title, (400 - title.get_width()//2, 100))
        
        if not self.show_instructions:
            # Draw options
            for i, option in enumerate(self.options):
                color = GREEN if i == self.selected else WHITE
                text = self.font_small.render(option, True, color)
                surface.blit(text, (400 - text.get_width()//2, 250 + i*50))
        else:
            # Draw instructions
            instructions = [
                "HOW TO PLAY:",
                "- Press SPACE when you see DRAW!",
                "- Shoot faster than your opponent",
                "- Hit your shots to reduce their health",
                "- Last cowboy standing wins!",
                "",
                "Press ESC to return to menu"
            ]
            
            for i, line in enumerate(instructions):
                text = self.font_small.render(line, True, WHITE)
                surface.blit(text, (400 - text.get_width()//2, 150 + i*40))
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if self.show_instructions:
                    if event.key == pygame.K_ESCAPE:
                        self.show_instructions = False
                else:
                    if event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                    elif event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                    elif event.key == pygame.K_RETURN:
                        if self.selected == 0:  # Start Game
                            return "game"
                        elif self.selected == 1:  # How to Play
                            self.show_instructions = True
                        elif self.selected == 2:  # Quit
                            return "quit"
        return "menu"


class UI:
    def __init__(self):
        self.font = pygame.font.SysFont("Arial", 24)
        self.font_large = pygame.font.SysFont("Arial", 36)

    def draw_text(self, text, x, y, color=BLACK, center=False):
        render = self.font.render(text, True, color)
        if center:
            rect = render.get_rect(center=(x, y))
            screen.blit(render, rect)
        else:
            screen.blit(render, (x, y))

    def draw_large_text(self, text, x, y, color=BLACK, center=False):
        render = self.font_large.render(text, True, color)
        if center:
            rect = render.get_rect(center=(x, y))
            screen.blit(render, rect)
        else:
            screen.blit(render, (x, y))

    def update(self):
        pygame.display.flip()


class SFX:
    def __init__(self):
        self.sounds = {}
        try:
            # Try to load sounds, use silent placeholders if files don't exist
            self.sounds["gunshot"] = pygame.mixer.Sound("gunshot.wav") if os.path.exists("gunshot.wav") else self.create_silent_sound()
            self.sounds["laser"] = pygame.mixer.Sound("laser.wav") if os.path.exists("laser.wav") else self.create_silent_sound()
            self.sounds["shell_drop"] = pygame.mixer.Sound("shell_drop.wav") if os.path.exists("shell_drop.wav") else self.create_silent_sound()
            self.sounds["gun_pump"] = pygame.mixer.Sound("gun_pump.wav") if os.path.exists("gun_pump.wav") else self.create_silent_sound()
            self.sounds["reload"] = pygame.mixer.Sound("reload.wav") if os.path.exists("reload.wav") else self.create_silent_sound()
        except:
            # If any error occurs, create silent placeholders
            for sound_name in ["gunshot", "laser", "shell_drop", "gun_pump", "reload"]:
                self.sounds[sound_name] = self.create_silent_sound()

    def create_silent_sound(self):
        # Create a silent sound as placeholder
        sound = pygame.mixer.Sound(buffer=bytes(44))
        return sound

    def play_sound(self, name):
        if name in self.sounds:
            self.sounds[name].play()


class Game:
    def __init__(self):
        self.player = Player()
        self.opponent = Opponent(difficulty=5)
        self.timer = Timer()
        self.ui = UI()
        self.sfx = SFX()
        self.game_state = "menu"
        self.round = 0
        self.max_rounds = 5
        self.game_over = False
        self.reaction_times = []
        self.results = []
        self.countdown_start_time = None
        self.countdown_duration = 3
        self.draw_trigger_time = 0
        self.bullet_trace = []
        self.bg_desert = pygame.Surface((800, 600))
        self.bg_desert.fill((210, 180, 140))  # Desert color placeholder
        self.bg_cloud = pygame.Surface((400, 200), pygame.SRCALPHA)
        pygame.draw.ellipse(self.bg_cloud, (200, 200, 200, 150), (0, 0, 400, 200))
        self.bg_cloud_x = 0
        self.menu = MainMenu()
        self.opponent_shot_time = 0

    def start_game(self):
        self.round += 1
        self.opponent = Opponent(difficulty=random.randint(1, 10))
        self.game_state = "countdown"
        self.countdown_start_time = pygame.time.get_ticks()
        delay = random.randint(2000, 4000)
        self.draw_trigger_time = pygame.time.get_ticks() + delay
        self.opponent_shot_time = self.draw_trigger_time + int(self.opponent.reaction_time * 1000)
        pygame.time.set_timer(pygame.USEREVENT, delay)
        pygame.time.set_timer(pygame.USEREVENT + 1, delay - 1800)
        self.player.weapon.reload()
        self.opponent.weapon.reload()

    def check_winner(self, player_shot_first):
        if player_shot_first:
            if self.player.shoot():
                self.player.is_shooting = True
                self.opponent.health -= self.player.weapon.damage
                self.player.update_score(100)
                self.results.append("Hit")
            else:
                self.results.append("Miss")

            start = self.player.rect.center
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dir_x = mouse_x - start[0]
            dir_y = mouse_y - start[1]
            length = (dir_x ** 2 + dir_y ** 2) ** 0.5
            if length == 0:
                length = 1
            dir_x /= length
            dir_y /= length
            end = (start[0] + dir_x * 1000, start[1] + dir_y * 1000)
            self.bullet_trace.append((start, end))

        else:
            if self.opponent.shoot():
                self.opponent.is_shooting = True
                self.player.health -= self.opponent.weapon.damage
                self.results.append("Opponent Hit")
                self.bullet_trace.append((self.opponent.rect.center, self.player.rect.center))
            else:
                self.results.append("Opponent Miss")

    def reset_game(self):
        if self.round >= self.max_rounds or self.player.health <= 0 or self.opponent.health <= 0:
            self.game_over = True
            self.game_state = "game_over"
        else:
            self.game_state = "waiting"
            self.save_data()
            self.bullet_trace.clear()

    def save_data(self):
        write_header = not os.path.exists("game_data.csv")
        with open("game_data.csv", "a", newline="") as file:
            writer = csv.writer(file)
            if write_header:
                writer.writerow(["Round", "Reaction Time", "Result", "Opponent Difficulty", "Score"])
            writer.writerow([
                self.round,
                self.player.reaction_time,
                self.results[-1] if self.results else "N/A",
                self.opponent.difficulty_level,
                self.player.score
            ])

    def draw_hitboxes(self):
        pygame.draw.rect(screen, RED, self.player.rect, 2)
        pygame.draw.rect(screen, RED, self.opponent.rect, 2)

    def draw_bullet_trace(self):
        for start, end in self.bullet_trace:
            pygame.draw.line(screen, GREEN, start, end, 3)

    def draw_health_bars(self):
        # Player health
        pygame.draw.rect(screen, RED, (50, 20, 200, 20))
        pygame.draw.rect(screen, GREEN, (50, 20, 200 * (self.player.health/self.player.max_health), 20))
        self.ui.draw_text(f"{self.player.health}/{self.player.max_health}", 150, 25, WHITE)
        
        # Opponent health
        pygame.draw.rect(screen, RED, (550, 20, 200, 20))
        pygame.draw.rect(screen, GREEN, (550, 20, 200 * (self.opponent.health/self.opponent.max_health), 20))
        self.ui.draw_text(f"{self.opponent.health}/{self.opponent.max_health}", 650, 25, WHITE)

    def draw_ammo(self):
        # Player ammo
        ammo_text = f"Ammo: {self.player.weapon.current_ammo}/{self.player.weapon.max_ammo}"
        self.ui.draw_text(ammo_text, 50, 50, WHITE)
        
        # Opponent ammo
        opp_ammo_text = f"Ammo: {self.opponent.weapon.current_ammo}/{self.opponent.weapon.max_ammo}"
        self.ui.draw_text(opp_ammo_text, 550, 50, WHITE)

    def draw_background(self):
        screen.blit(self.bg_desert, (0, 0))

        self.bg_cloud_x -= 0.3  # Move cloud slower
        if self.bg_cloud_x <= -800:
            self.bg_cloud_x = 0
        screen.blit(self.bg_cloud, (self.bg_cloud_x, 0))
        screen.blit(self.bg_cloud, (self.bg_cloud_x + 800, 0))

    def draw_game_over(self):
        screen.fill(BLACK)
        if self.player.health <= 0:
            result_text = "YOU LOST!"
        elif self.opponent.health <= 0:
            result_text = "YOU WON!"
        else:
            result_text = f"GAME OVER! Score: {self.player.score}"
            
        self.ui.draw_large_text(result_text, 400, 200, WHITE, center=True)
        self.ui.draw_text(f"Final Score: {self.player.score}", 400, 250, WHITE, center=True)
        self.ui.draw_text("Press R to restart or ESC for menu", 400, 300, WHITE, center=True)

    def run(self):
        running = True
        draw_time = False

        while running:
            current_time = pygame.time.get_ticks()
            
            if self.game_state == "menu":
                screen.fill(BLACK)
                menu_result = self.menu.handle_input()
                if menu_result == "quit":
                    running = False
                elif menu_result == "game":
                    self.__init__()  # Reset game state
                    self.game_state = "waiting"
                self.menu.draw(screen)
                self.ui.update()
                clock.tick(60)
                continue
            elif self.game_state == "game_over":
                self.draw_game_over()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:  # Restart
                            self.__init__()
                            self.game_state = "waiting"
                        elif event.key == pygame.K_ESCAPE:  # Back to menu
                            self.game_state = "menu"
                self.ui.update()
                clock.tick(60)
                continue

            screen.fill(BLACK)
            self.draw_background()
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.USEREVENT and self.game_state == "countdown":
                    self.timer.start()
                    draw_time = True
                    self.game_state = "shooting"
                elif event.type == pygame.USEREVENT + 1 and self.game_state == "countdown":
                    self.sfx.play_sound("gun_pump")
                elif event.type == pygame.MOUSEBUTTONDOWN and self.game_state == "shooting":
                    self.timer.stop()
                    self.player.reaction_time = self.timer.get_reaction_time()
                    self.reaction_times.append(self.player.reaction_time)
                    self.sfx.play_sound("gunshot")
                    self.sfx.play_sound("laser")
                    pygame.time.set_timer(pygame.USEREVENT + 2, 300)
                    self.check_winner(player_shot_first=True)
                    self.game_state = "result"
                elif event.type == pygame.USEREVENT + 2:
                    self.sfx.play_sound("shell_drop")
                elif event.type == pygame.KEYDOWN and self.game_state == "waiting" and event.key == pygame.K_SPACE:
                    self.start_game()

            # Opponent auto-shooting logic
            if self.game_state == "shooting" and current_time >= self.opponent_shot_time:
                if not self.timer.end_time:  # Player hasn't shot yet
                    self.timer.stop()
                    self.sfx.play_sound("gunshot")
                    self.check_winner(player_shot_first=False)
                    self.game_state = "result"

            if self.game_state == "waiting":
                self.ui.draw_text("Press SPACE to start round", 400, 250, WHITE, center=True)

            elif self.game_state == "countdown":
                elapsed = (current_time - self.countdown_start_time) // 1000
                remaining = max(0, self.countdown_duration - elapsed)
                self.ui.draw_text(f"Get Ready... {remaining}", 400, 250, WHITE, center=True)

            elif self.game_state == "shooting":
                self.ui.draw_text("DRAW! SHOOT NOW!", 400, 250, RED, center=True)

            elif self.game_state == "result":
                result_text = f"Round {self.round} Result: {self.results[-1] if self.results else 'N/A'}"
                self.ui.draw_text(result_text, 400, 250, WHITE, center=True)
                self.ui.draw_text("Press SPACE to continue", 400, 300, WHITE, center=True)
                
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    self.reset_game()

            # Draw game elements
            self.player.draw(screen)
            self.opponent.draw(screen)
            self.draw_health_bars()
            self.draw_ammo()
            self.draw_hitboxes()
            self.draw_bullet_trace()
            
            # Centered UI Text
            self.ui.draw_text(f"Round: {self.round}/{self.max_rounds}", 400, 10, WHITE, center=True)
            self.ui.draw_text(f"Score: {self.player.score}", 400, 40, WHITE, center=True)
            
            if self.game_state == "result" and self.player.reaction_time > 0:
                self.ui.draw_text(f"Your reaction time: {self.player.reaction_time}s", 400, 350, WHITE, center=True)
                self.ui.draw_text(f"Opponent's reaction time: {self.opponent.reaction_time}s", 400, 380, WHITE, center=True)

            self.ui.update()
            clock.tick(60)


# ---------------------------- Main Game Loop ----------------------------
if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()