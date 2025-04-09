import pygame
import random
import time
import csv
from datetime import datetime

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gun Blood-like Game")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

font = pygame.font.Font(None, 36)

CSV_FILE = "game_data.csv"

PLAYER_HEALTH = 100
OPPONENT_HEALTH = 100
DUEL_TIME = 30
WEAPON_DAMAGE = 10
WEAPON_ACCURACY = 0.8

class Timer:
    def __init__(self, duration):
        self.duration = duration
        self.start_time = None

    def start(self):
        self.start_time = time.time()

    def is_finished(self):
        if self.start_time is None:
            return False
        return time.time() - self.start_time >= self.duration

    def remaining_time(self):
        if self.start_time is None:
            return self.duration
        return max(0, self.duration - (time.time() - self.start_time))

class Weapon:
    def __init__(self, damage, accuracy):
        self.damage = damage
        self.accuracy = accuracy

    def fire(self):
        return random.random() < self.accuracy

class Player:
    def __init__(self, name):
        self.name = name
        self.health = PLAYER_HEALTH
        self.score = 0
        self.reaction_time = None
        self.weapon = Weapon(WEAPON_DAMAGE, WEAPON_ACCURACY)

    def shoot(self, opponent):
        if self.weapon.fire():
            opponent.take_damage(self.weapon.damage)
            self.score += 1
            return True
        return False

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def reset(self):
        self.health = PLAYER_HEALTH
        self.score = 0
        self.reaction_time = None

class Opponent:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.health = OPPONENT_HEALTH
        self.reaction_time = self.random_reaction_time()
        self.weapon = Weapon(WEAPON_DAMAGE, WEAPON_ACCURACY)

    def random_reaction_time(self):
        if self.difficulty == "easy":
            return random.uniform(0.5, 1.0)
        elif self.difficulty == "medium":
            return random.uniform(0.3, 0.7)
        elif self.difficulty == "hard":
            return random.uniform(0.1, 0.5)

    def shoot(self, player):
        if self.weapon.fire():
            player.take_damage(self.weapon.damage)
            return True
        return False

    def take_damage(self, damage):
        self.health -= damage
        if self.health < 0:
            self.health = 0

    def reset(self):
        self.health = OPPONENT_HEALTH
        self.reaction_time = self.random_reaction_time()

class Game:
    def __init__(self):
        self.player = Player("Player 1")
        self.opponent = Opponent("medium")
        self.timer = Timer(DUEL_TIME)
        self.game_state = "menu"
        self.start_time = None

    def start_game(self):
        self.game_state = "playing"
        self.timer.start()
        self.player.reset()
        self.opponent.reset()
        self.start_time = datetime.now()

    def check_winner(self):
        if self.player.health <= 0:
            return "Opponent"
        elif self.opponent.health <= 0:
            return "Player"
        return None

    def reset_game(self):
        self.game_state = "menu"
        self.player.reset()
        self.opponent.reset()

    def update(self):
        if self.game_state == "playing":
            if self.timer.is_finished():
                self.game_state = "ended"
            winner = self.check_winner()
            if winner:
                self.game_state = "ended"
                self.record_game_data(winner)
        elif self.game_state == "menu":
            self.draw_text("Press SPACE to start", WIDTH // 2 - 100, HEIGHT // 2)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.start_game()

    def draw_text(self, text, x, y):
        text_surface = font.render(text, True, BLACK)
        screen.blit(text_surface, (x, y))

    def record_game_data(self, winner):
        end_time = datetime.now()
        time_played = (end_time - self.start_time).total_seconds()
        data = {
            "player_name": self.player.name,
            "player_score": self.player.score,
            "player_reaction_time": self.player.reaction_time,
            "opponent_difficulty": self.opponent.difficulty,
            "time_played": time_played,
            "winner": winner,
        }
        with open(CSV_FILE, mode="a", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=data.keys())
            if file.tell() == 0:
                writer.writeheader()
            writer.writerow(data)

def main():
    game = Game()
    clock = pygame.time.Clock()
    running = True

    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and game.game_state == "playing":
                    if game.player.shoot(game.opponent):
                        game.player.reaction_time = game.timer.remaining_time()

        game.update()

        if game.game_state == "playing":
            game.draw_text(f"Player Health: {game.player.health}", 10, 10)
            game.draw_text(f"Opponent Health: {game.opponent.health}", 10, 50)
            game.draw_text(f"Time Left: {int(game.timer.remaining_time())}", 10, 90)
            game.draw_text(f"Score: {game.player.score}", 10, 130)

            if random.random() < 0.02:
                game.opponent.shoot(game.player)

        elif game.game_state == "ended":
            winner = game.check_winner()
            game.draw_text(f"{winner} wins!", WIDTH // 2 - 50, HEIGHT // 2)
            game.draw_text("Press R to restart", WIDTH // 2 - 80, HEIGHT // 2 + 40)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                game.reset_game()

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()