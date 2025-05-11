import pygame
import random
import math
import csv
import time
import os
import sys
from pygame import mixer

# Initialize pygame
pygame.init()
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Eagle Eyes")
clock = pygame.time.Clock()

# Game Constants
GAME_STATES = {
    "MENU": "menu",
    "COUNTDOWN": "countdown",
    "WAITING": "waiting",
    "SHOOTING": "shooting",
    "RESULT": "result",
    "GAME_OVER": "game_over"
}

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (139, 69, 19)
SKIN = (255, 220, 177)
DARK_BLUE = (0, 0, 139)
HAT = (160, 82, 45)
YELLOW = (255, 255, 0)
HIT_FLASH = (255, 100, 100, 100)
MENU_BG_COLOR = WHITE
MENU_TEXT_COLOR = BLACK

def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

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
        self.fire_rate = fire_rate
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
        self.head_rect = pygame.Rect(100, 300, 50, 30)
        self.body_rect = pygame.Rect(100, 330, 50, 70)
        self.is_shooting = False
        self.last_shot_time = 0

    def check_hit(self, bullet_pos):
        if self.head_rect.collidepoint(bullet_pos):
            return "head"
        elif self.body_rect.collidepoint(bullet_pos):
            return "body"
        return None

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
        self.head_rect = pygame.Rect(650, 300, 50, 30)
        self.body_rect = pygame.Rect(650, 330, 50, 70)
        self.is_shooting = False
        self.last_shot_time = 0
        self.has_shot_this_round = False  # New flag to track shooting per round

    def reset_for_new_round(self):
        """Reset shooting state for a new round"""
        self.reaction_time = self.random_reaction_time()
        self.is_shooting = False
        self.has_shot_this_round = False
        self.weapon.reload()

    def check_hit(self, bullet_pos):
        if self.head_rect.collidepoint(bullet_pos):
            return "head"
        elif self.body_rect.collidepoint(bullet_pos):
            return "body"
        return None

    def draw_gun(self):
        pass

    def shoot(self):
        accuracy_boost = min(0.2, self.difficulty_level * 0.02)
        if self.weapon.can_fire():
            self.weapon.last_shot_time = pygame.time.get_ticks()
            self.weapon.current_ammo -= 1
            self.is_shooting = True
            return random.random() <= (self.weapon.accuracy + accuracy_boost)
        return False

    def random_reaction_time(self):
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
        
        if self.is_shooting:
            pygame.draw.line(surface, YELLOW, (x - 10, y + 50), (x - 40, y + 40), 3)
            self.is_shooting = False
        else:
            pygame.draw.line(surface, (192, 192, 192), (x - 10, y + 50), (x, y + 50), 3)

class MainMenu:
    def __init__(self, sfx):
        self.font_large = pygame.font.SysFont("Arial", 64)
        self.font_small = pygame.font.SysFont("Arial", 32)
        self.options = ["Start Game", "How to Play", "Quit"]
        self.selected = 0
        self.show_instructions = False
        self.sfx = sfx
    
    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                if self.show_instructions:
                    if event.key == pygame.K_ESCAPE:
                        self.sfx.play("menu_select")
                        self.show_instructions = False
                else:
                    if event.key == pygame.K_DOWN:
                        self.selected = (self.selected + 1) % len(self.options)
                        self.sfx.play("menu_select")
                    elif event.key == pygame.K_UP:
                        self.selected = (self.selected - 1) % len(self.options)
                        self.sfx.play("menu_select")
                    elif event.key == pygame.K_RETURN:
                        self.sfx.play("menu_select")
                        if self.selected == 0:
                            return "game"
                        elif self.selected == 1:
                            self.show_instructions = True
                        elif self.selected == 2:
                            return "quit"
        return "menu"
    
    def draw(self, surface):
        surface.fill(MENU_BG_COLOR)
        
        if not self.show_instructions:
            title = self.font_large.render("EAGLE EYES", True, MENU_TEXT_COLOR)
            surface.blit(title, (400 - title.get_width()//2, 100))
            
            for i, option in enumerate(self.options):
                if i == self.selected:
                    text_rect = pygame.Rect(
                        400 - self.font_small.size(option)[0]//2 - 10,
                        240 + i*50,
                        self.font_small.size(option)[0] + 20,
                        40
                    )
                    pygame.draw.rect(surface, (220, 220, 220), text_rect)
                
                text = self.font_small.render(option, True, MENU_TEXT_COLOR)
                surface.blit(text, (400 - text.get_width()//2, 250 + i*50))
        else:
            instructions = [
                "HOW TO PLAY",
                "",
                " QUICK DRAW:",
                "- Press SPACE when 'DRAW!' appears",
                "- The faster you shoot, the better!",
                "",
                " AIM & SHOOT:",
                "- Headshots deal 50 damage",
                "- Body shots deal 20 damage",
                "",
                " LAST COWBOY WINS:",
                "- Health carries between rounds",
                "- First to 0 health loses",
                "",
                "ESC - Back to Menu"
            ]
            
            for i, line in enumerate(instructions):
                text = self.font_small.render(line, True, MENU_TEXT_COLOR)
                surface.blit(text, (400 - text.get_width()//2, 150 + i*30))

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
        self.channels = []
        self.music_channel = None
        self.sound_config = {
            "gunshot": {"file": "gunshot.wav", "volume": 0.7, "channel": 0},
            "laser": {"file": "laser.wav", "volume": 0.5, "channel": 1},
            "shell_drop": {"file": "shell_drop.wav", "volume": 0.4, "channel": 2, "max_time": 500},
            "gun_pump": {"file": "gun_pump.wav", "volume": 0.6, "channel": 3},
            "reload": {"file": "gun_pump.wav", "volume": 0.6, "channel": 4},
            "menu_select": {"file": "menu_sound.wav", "volume": 0.5, "channel": 6},
            "eagle": {"file": "eagle.wav", "volume": 0.6, "channel": 7},
            "desert_wind": {"file": "desert_wind.wav", "volume": 0.2, "channel": 8, "loop": True}
        }
        self.music_files = {
            "menu_music": "menu_bg_music.wav"
        }

        pygame.mixer.init()
        pygame.mixer.set_num_channels(10)
        
        for i in range(9):
            self.channels.append(pygame.mixer.Channel(i))
        self.music_channel = pygame.mixer.Channel(9)

        print("\nInitializing audio system...")
        
        for name, config in self.sound_config.items():
            path = resource_path(os.path.join("assets", "sounds", config["file"]))
            try:
                if os.path.exists(path):
                    sound = pygame.mixer.Sound(path)
                    sound.set_volume(config["volume"])
                    self.sounds[name] = sound
                    print(f"✅ Loaded sound: {name}")
                else:
                    print(f"❌ Sound file not found: {config['file']}")
                    self.sounds[name] = self._create_silent_sound()
            except Exception as e:
                print(f"⚠️ Error loading {name}: {e}")
                self.sounds[name] = self._create_silent_sound()
        
        self.music = {}
        for name, file in self.music_files.items():
            path = resource_path(os.path.join("assets", "sounds", file))
            try:
                if os.path.exists(path):
                    self.music[name] = path
                    print(f"✅ Loaded music: {name}")
                else:
                    print(f"❌ Music file not found: {file}")
                    self.music[name] = None
            except Exception as e:
                print(f"⚠️ Error loading music {name}: {e}")
                self.music[name] = None
        
        print("Audio system ready\n")
    
    def _create_silent_sound(self):
        silent_sound = pygame.mixer.Sound(buffer=bytes(44))
        silent_sound.set_volume(0)
        return silent_sound
    
    def play(self, name):
        if name not in self.sounds or name not in self.sound_config:
            return
        
        channel_num = self.sound_config[name]["channel"]
        channel = self.channels[channel_num]
        
        if name == "desert_wind":
            if not channel.get_busy():
                channel.play(self.sounds[name], loops=-1)
            return
        
        channel.play(self.sounds[name])
    
    def play_music(self, name):
        if name in self.music and self.music[name]:
            self.music_channel.stop()
            sound = pygame.mixer.Sound(self.music[name])
            sound.set_volume(0.4)
            self.music_channel.play(sound, loops=-1)
    
    def stop_music(self):
        self.music_channel.stop()
    
    def stop_all(self):
        for channel in self.channels:
            channel.stop()
        self.music_channel.stop()

class Background:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.cloud_path = resource_path(os.path.join("assets", "bg", "cloud.png"))
        self.desert_path = resource_path(os.path.join("assets", "bg", "desert.png"))
        
        print("\nLoading background images...")
        self.desert = self._load_image(self.desert_path, "desert_bg.png", True)
        self.cloud_img = self._load_image(self.cloud_path, "cloud.png", False)
        
        self.clouds = [
            {'x': random.randint(0, width), 'y': random.randint(50, 150), 'speed': random.uniform(0.2, 0.4)},
            {'x': random.randint(0, width), 'y': random.randint(100, 200), 'speed': random.uniform(0.4, 0.6)}
        ]
        
        self.scaled_clouds = [
            pygame.transform.scale(self.cloud_img, (int(self.cloud_img.get_width() * 0.8), int(self.cloud_img.get_height() * 0.8))),
            pygame.transform.scale(self.cloud_img, (int(self.cloud_img.get_width() * 0.6), int(self.cloud_img.get_height() * 0.6)))
        ]
        
        print(f"\nDesert size: {self.desert.get_size()}")
        print(f"Cloud size: {self.cloud_img.get_size()}")
        print("Background system ready\n")
    
    def _load_image(self, path, display_name, is_background):
        print(f"Attempting to load: {display_name}")
        try:
            if os.path.exists(path):
                img = pygame.image.load(path)
                print(f"✅ Successfully loaded: {display_name}")
                if is_background:
                    img = img.convert()
                    return pygame.transform.scale(img, (self.width, self.height))
                else:
                    return img.convert_alpha()
        except Exception as e:
            print(f"⚠️ Error loading {display_name}: {e}")
        
        print(f"Creating fallback surface for {display_name}")
        if is_background:
            surf = pygame.Surface((self.width, self.height))
            surf.fill((210, 180, 140))
            print("Created desert fallback")
            return surf
        else:
            surf = pygame.Surface((400, 200), pygame.SRCALPHA)
            pygame.draw.ellipse(surf, (200, 200, 200, 150), (0, 0, 400, 200))
            print("Created cloud fallback")
            return surf
    
    def update(self):
        for i, cloud in enumerate(self.clouds):
            cloud['x'] -= cloud['speed']
            if cloud['x'] < -self.scaled_clouds[i].get_width():
                cloud['x'] = self.width
                cloud['y'] = random.randint(50 if i == 0 else 100, 150 if i == 0 else 200)
                cloud['speed'] = random.uniform(0.2 if i == 0 else 0.4, 0.4 if i == 0 else 0.6)
    
    def draw(self, surface):
        surface.blit(self.desert, (0, 0))
        for i, cloud in enumerate(self.clouds):
            surface.blit(self.scaled_clouds[i], (cloud['x'], cloud['y']))

class Game:
    def __init__(self):
        self.sfx = SFX()
        self.sfx.play_music("menu_music")
        
        self.player = Player()
        self.opponent = Opponent(difficulty=5)
        self.timer = Timer()
        self.ui = UI()
        self.background = Background(800, 600)
        self.menu_bg = self._load_menu_bg()
        self.game_state = GAME_STATES["MENU"]
        self.round = 0
        self.max_rounds = 5
        self.game_over = False
        self.reaction_times = []
        self.results = []
        self.countdown_start_time = None
        self.countdown_duration = 3
        self.draw_trigger_time = 0
        self.bullet_trace = []
        self.opponent_shot_time = 0
        self.menu = MainMenu(self.sfx)
        self.hit_flash_end = 0
        self.played_eagle_sound = False
        self.show_hitboxes = False
        self.start_play_time = None
        self.total_play_time = 0

    def _load_menu_bg(self):
        try:
            path = resource_path(os.path.join("assets", "bg", "eagle_eyes.png"))
            if os.path.exists(path):
                img = pygame.image.load(path)
                return pygame.transform.scale(img, (800, 600))
        except:
            # Fallback if image fails to load
            surf = pygame.Surface((800, 600))
            surf.fill((50, 50, 70))  # Dark blue fallback
            return surf

    def start_game(self):
        if self.start_play_time is None:  # Only set on first round
            self.start_play_time = time.time()

        if self.game_over or self.round >= self.max_rounds:
            return
            
        self.sfx.stop_music()
        if not self.played_eagle_sound:
            self.sfx.play("eagle")
            self.played_eagle_sound = True
            
        self.sfx.play("desert_wind")
        self.round += 1
        
        if self.opponent.health <= 0:
            self.opponent = Opponent(difficulty=min(10, self.round + 3))
        else:
            self.opponent.reset_for_new_round()  # Use the new reset method
        
        self.game_state = GAME_STATES["COUNTDOWN"]
        self.countdown_start_time = pygame.time.get_ticks()
        delay = random.randint(2000, 4000)
        self.draw_trigger_time = pygame.time.get_ticks() + delay
        self.opponent_shot_time = self.draw_trigger_time + int(self.opponent.reaction_time * 1000)
        pygame.time.set_timer(pygame.USEREVENT, delay)
        pygame.time.set_timer(pygame.USEREVENT + 1, delay - 1800)
        self.player.weapon.reload()
        self.sfx.play("reload")
        self.bullet_trace.clear()
        self.timer = Timer()

    def check_winner(self, player_shot_first):
        now = pygame.time.get_ticks()
        mouse_pos = pygame.mouse.get_pos()
        
        if player_shot_first:
            if self.player.shoot():
                self.player.is_shooting = True
                self.player.last_shot_time = now
                
                start_pos = (self.player.rect.centerx + 30, self.player.rect.centery)
                angle = math.atan2(mouse_pos[1] - start_pos[1], mouse_pos[0] - start_pos[0])
                end_pos = (
                    start_pos[0] + math.cos(angle) * 1000,
                    start_pos[1] + math.sin(angle) * 1000
                )
                
                hit_location = None
                steps = 20
                for i in range(1, steps + 1):
                    check_pos = (
                        start_pos[0] + (end_pos[0] - start_pos[0]) * (i/steps),
                        start_pos[1] + (end_pos[1] - start_pos[1]) * (i/steps)
                    )
                    hit_location = self.opponent.check_hit(check_pos)
                    if hit_location:
                        break
                
                if hit_location:
                    if hit_location == "head":
                        damage = 50
                        result = "Player Hit"
                    else:
                        damage = 20
                        result = "Player Hit"
                    self.opponent.health -= damage
                    self.player.update_score(damage)
                else:
                    result = "Player Miss"
                
                self.results.append(result)
                self.sfx.play("gunshot")
                self.hit_flash_end = now + 200 if hit_location else 0
                self.bullet_trace.append(("player", start_pos, end_pos, now))
        else:
            if self.opponent.shoot():
                self.opponent.is_shooting = True
                self.opponent.last_shot_time = now
                
                start_pos = (self.opponent.rect.centerx - 30, self.opponent.rect.centery)
                target_choice = random.choices(
                    ["head", "body", "miss"],
                    weights=[0.3 + (0.02 * self.opponent.difficulty_level), 
                            0.5, 
                            0.2 - (0.02 * self.opponent.difficulty_level)]
                )[0]
                
                if target_choice == "head":
                    end_pos = (
                        self.player.head_rect.centerx + random.randint(-20, 20),
                        self.player.head_rect.centery + random.randint(-10, 10)
                    )
                elif target_choice == "body":
                    end_pos = (
                        self.player.body_rect.centerx + random.randint(-30, 30),
                        self.player.body_rect.centery + random.randint(-20, 20)
                    )
                else:
                    end_pos = (
                        random.randint(100, 700),
                        random.randint(200, 400)
                    )
                
                hit_location = None
                if target_choice != "miss":
                    steps = 20
                    for i in range(1, steps + 1):
                        check_pos = (
                            start_pos[0] + (end_pos[0] - start_pos[0]) * (i/steps),
                            start_pos[1] + (end_pos[1] - start_pos[1]) * (i/steps)
                        )
                        hit_location = self.player.check_hit(check_pos)
                        if hit_location:
                            break
                
                if hit_location:
                    if hit_location == "head":
                        damage = 50
                    else:
                        damage = 20
                    self.player.health -= damage
                    result = "Opponent Hit"
                else:
                    result = "Opponent Miss"
                
                self.results.append(result)
                self.sfx.play("gunshot")
                self.hit_flash_end = now + 200 if hit_location else 0
                self.bullet_trace.append(("opponent", start_pos, end_pos, now))

    def reset_game(self):
        if self.player.health <= 0 or self.opponent.health <= 0 or self.round >= self.max_rounds:
            self.game_over = True
            self.game_state = GAME_STATES["GAME_OVER"]
            self.sfx.stop_all()
            self.sfx.play_music("menu_music")
            self.played_eagle_sound = False
        else:
            self.player.weapon.reload()
            self.opponent.weapon.reload()
            self.game_state = GAME_STATES["WAITING"]
            self.save_data()
            self.bullet_trace.clear()

    def save_data(self):
        # Calculate current playtime
        current_time = time.time()
        if self.start_play_time:
            self.total_play_time = current_time - self.start_play_time
        
        write_header = not os.path.exists("game_data.csv")
        with open("game_data.csv", "a", newline="") as file:
            writer = csv.writer(file)
            if write_header:
                writer.writerow([
                    "Round", 
                    "Reaction Time", 
                    "Result", 
                    "Opponent Difficulty", 
                    "Score",
                    "Time Played (seconds)"
                ])
            
            # Simplify results to just Hit/Miss
            simple_result = "N/A"
            if self.results:
                last_result = self.results[-1]
                if "Hit" in last_result:
                    simple_result = "Player Hit" if "Player" in last_result else "Opponent Hit"
                else:
                    simple_result = "Player Miss" if "Player" in last_result else "Opponent Miss"
            
            writer.writerow([
                self.round,
                self.player.reaction_time,
                simple_result,
                self.opponent.difficulty_level,
                self.player.score,
                round(self.total_play_time, 2)  # Time played in seconds with 2 decimal places
            ])

    def draw_hitboxes(self):
        pygame.draw.rect(screen, RED, self.player.head_rect, 2)
        pygame.draw.rect(screen, BLUE, self.player.body_rect, 2)
        pygame.draw.rect(screen, RED, self.opponent.head_rect, 2)
        pygame.draw.rect(screen, BLUE, self.opponent.body_rect, 2)

    def draw_bullet_trace(self):
        now = pygame.time.get_ticks()
        self.bullet_trace = [trace for trace in self.bullet_trace if now - trace[3] < 500]
        
        for trace in self.bullet_trace:
            color = GREEN if trace[0] == "player" else RED
            width = 3 if trace[0] == "player" else 4
            
            # Draw the full trajectory
            pygame.draw.line(screen, color, trace[1], trace[2], width)
            
            # Add bullet "head" at current position
            progress = min(1.0, (now - trace[3]) / 200)  # Bullet travels in 200ms
            bullet_pos = (
                trace[1][0] + (trace[2][0] - trace[1][0]) * progress,
                trace[1][1] + (trace[2][1] - trace[1][1]) * progress
            )
            pygame.draw.circle(screen, YELLOW, (int(bullet_pos[0]), int(bullet_pos[1])), 5)

    def draw_muzzle_flash(self):
        now = pygame.time.get_ticks()
        if now - self.player.last_shot_time < 100 and self.player.is_shooting:
            pos = (self.player.rect.centerx + 40, self.player.rect.centery)
            pygame.draw.circle(screen, YELLOW, pos, 15)
        
        if now - self.opponent.last_shot_time < 100 and self.opponent.is_shooting:
            pos = (self.opponent.rect.centerx - 40, self.opponent.rect.centery)
            pygame.draw.circle(screen, YELLOW, pos, 15)

    def draw_hit_flash(self):
        now = pygame.time.get_ticks()
        if now < self.hit_flash_end:
            flash_surface = pygame.Surface((800, 600), pygame.SRCALPHA)
            flash_surface.fill(HIT_FLASH)
            screen.blit(flash_surface, (0, 0))

    def draw_health_bars(self):
        pygame.draw.rect(screen, RED, (50, 20, 200, 20))
        pygame.draw.rect(screen, GREEN, (50, 20, 200 * (self.player.health/self.player.max_health), 20))
        self.ui.draw_text(f"{self.player.health}/{self.player.max_health}", 150, 25, BLACK)
        
        pygame.draw.rect(screen, RED, (550, 20, 200, 20))
        pygame.draw.rect(screen, GREEN, (550, 20, 200 * (self.opponent.health/self.opponent.max_health), 20))
        self.ui.draw_text(f"{self.opponent.health}/{self.opponent.max_health}", 650, 25, BLACK)

    def draw_ammo(self):
        ammo_text = f"Ammo: {self.player.weapon.current_ammo}/{self.player.weapon.max_ammo}"
        self.ui.draw_text(ammo_text, 50, 50, BLACK)
        
        opp_ammo_text = f"Ammo: {self.opponent.weapon.current_ammo}/{self.opponent.weapon.max_ammo}"
        self.ui.draw_text(opp_ammo_text, 550, 50, BLACK)

    def draw_game_over(self):
        # Draw background
        screen.blit(self.menu_bg, (0, 0))
        
        # Semi-transparent overlay
        overlay = pygame.Surface((800, 600), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Darker overlay for better text contrast
        screen.blit(overlay, (0, 0))
        
        # Draw report text
        if self.player.health <= 0:
            result_text = "YOU LOST!"
        elif self.opponent.health <= 0:
            result_text = "YOU WON!"
        else:
            result_text = "GAME OVER"
        
        self.ui.draw_large_text(result_text, 400, 150, WHITE, center=True)
        self.ui.draw_text(f"Final Score: {self.player.score}", 400, 200, BLACK, center=True)
        self.ui.draw_text(f"Rounds Played: {self.round}/{self.max_rounds}", 400, 250, BLACK, center=True)
        self.ui.draw_text("Press R to restart or ESC for menu", 400, 300, BLACK, center=True)

    def run(self):
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            
            # Handle menu/game over states
            if self.game_state == GAME_STATES["MENU"]:
                screen.fill(WHITE)
                menu_result = self.menu.handle_input()
                if menu_result == "quit":
                    running = False
                elif menu_result == "game":
                    self.__init__()
                    self.game_state = GAME_STATES["WAITING"]
                self.menu.draw(screen)
                pygame.display.flip()
                clock.tick(60)
                continue
            
            if self.game_state == GAME_STATES["GAME_OVER"]:
                self.draw_game_over()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        running = False
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_r:
                            self.__init__()
                            self.game_state = GAME_STATES["WAITING"]
                        elif event.key == pygame.K_ESCAPE:
                            self.game_state = GAME_STATES["MENU"]
                        elif event.key == pygame.K_h:
                            self.show_hitboxes = not self.show_hitboxes
                pygame.display.flip()
                clock.tick(60)
                continue

            # Main game rendering
            self.background.update()
            self.background.draw(screen)
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.USEREVENT and self.game_state == GAME_STATES["COUNTDOWN"]:
                    self.timer.start()
                    self.game_state = GAME_STATES["SHOOTING"]
                elif event.type == pygame.USEREVENT + 1 and self.game_state == GAME_STATES["COUNTDOWN"]:
                    if not self.sfx.channels[3].get_busy():
                        self.sfx.play("gun_pump")
                elif event.type == pygame.MOUSEBUTTONDOWN and self.game_state == GAME_STATES["SHOOTING"]:
                    self.timer.stop()
                    self.player.reaction_time = self.timer.get_reaction_time()
                    self.reaction_times.append(self.player.reaction_time)
                    pygame.time.set_timer(pygame.USEREVENT + 2, 300, loops=1)
                    self.check_winner(player_shot_first=True)
                    self.game_state = GAME_STATES["RESULT"]
                elif event.type == pygame.USEREVENT + 2:
                    self.sfx.play("shell_drop")
                elif event.type == pygame.KEYDOWN:
                    if self.game_state == GAME_STATES["WAITING"] and event.key == pygame.K_SPACE:
                        self.start_game()
                    elif event.key == pygame.K_h:
                        self.show_hitboxes = not self.show_hitboxes

            # Opponent shooting logic - ensure they always shoot
            if (self.game_state == GAME_STATES["SHOOTING"] and 
                current_time >= self.opponent_shot_time and 
                not self.opponent.has_shot_this_round and
                not self.timer.end_time):
                
                # Only shoot if player hasn't already shot first
                if not self.player.is_shooting:
                    self.timer.stop()
                    if self.opponent.shoot():
                        self.opponent.has_shot_this_round = True
                        self.check_winner(player_shot_first=False)
                        self.game_state = GAME_STATES["RESULT"]

            # Game state rendering
            if self.game_state == GAME_STATES["WAITING"]:
                self.ui.draw_text("Press SPACE to start round", 400, 250, BLACK, center=True)
            elif self.game_state == GAME_STATES["COUNTDOWN"]:
                elapsed = (current_time - self.countdown_start_time) // 1000
                remaining = max(0, self.countdown_duration - elapsed)
                self.ui.draw_text(f"Get Ready... {remaining}", 400, 250, BLACK, center=True)
            elif self.game_state == GAME_STATES["SHOOTING"]:
                self.ui.draw_text("DRAW! SHOOT NOW!", 400, 250, BLACK, center=True)
            elif self.game_state == GAME_STATES["RESULT"]:
                if self.results:
                    result_text = f"Round {self.round} Result: {self.results[-1]}"
                    self.ui.draw_text(result_text, 400, 250, BLACK, center=True)
                self.ui.draw_text("Press SPACE to continue", 400, 300, BLACK, center=True)
                
                if pygame.key.get_pressed()[pygame.K_SPACE]:
                    self.reset_game()

            # Draw all game objects
            self.player.draw(screen)
            self.opponent.draw(screen)
            self.draw_health_bars()
            self.draw_ammo()
            if self.show_hitboxes:
                self.draw_hitboxes()
            self.draw_bullet_trace()
            self.draw_muzzle_flash()
            self.draw_hit_flash()
            
            # UI elements
            self.ui.draw_text(f"Round: {self.round}/{self.max_rounds}", 400, 10, BLACK, center=True)
            self.ui.draw_text(f"Score: {self.player.score}", 400, 40, BLACK, center=True)
            self.ui.draw_text("Press H to toggle hitboxes", 400, 550, BLACK, center=True)
            
            if self.game_state == GAME_STATES["RESULT"] and self.player.reaction_time > 0:
                self.ui.draw_text(f"Your reaction time: {self.player.reaction_time}s", 400, 350, BLACK, center=True)
                self.ui.draw_text(f"Opponent's reaction time: {self.opponent.reaction_time}s", 400, 380, BLACK, center=True)

            pygame.display.flip()
            clock.tick(60)

if __name__ == "__main__":
    os.makedirs(resource_path(os.path.join("assets", "sounds")), exist_ok=True)
    os.makedirs(resource_path(os.path.join("assets", "bg")), exist_ok=True)
    
    game = Game()
    game.run()
    pygame.quit()
