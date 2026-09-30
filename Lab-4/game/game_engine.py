import random
import pygame
from game.text_box import TextBox
 
class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height

        self.words = ["PYTHON", "PYGAME", "PLANET", "ROCKET", "GALAXY", "STREAM", "PUZZLE", "ALGORITHM"]
        self.secret_word = ""
        self.scrambled_word = ""

        self.score = 0
        self.feedback_msg = "Unscramble the letters above!"
        self.feedback_color = (210, 215, 225)

        self.input_box = TextBox(width // 2 - 130, 250, 160, 46)
        self.submit_btn = pygame.Rect(width // 2 + 45, 250, 95, 46)
        self.hint_btn = pygame.Rect(width // 2 + 150, 250, 95, 46)
        self.HINT_PENALTY = 0.5
        self.hints_used = 0
        self.ROUND_TIME_MS = 20000
        self.round_start = 0
        self.DEFAULT_MSG = "Unscramble the letters above!"
        self.FEEDBACK_MS = 4000
        self.feedback_time = 0
        self.TILE = 46
        self.TILE_GAP = 8
        self.TILE_Y = 100
        self.RACK_Y = 160
        self.rack = []
        self.font_tile = pygame.font.SysFont(None, 40)

        self.font_title = pygame.font.SysFont(None, 40)
        self.font_word = pygame.font.SysFont(None, 52)
        self.font_msg = pygame.font.SysFont(None, 26)
        self.font_btn = pygame.font.SysFont(None, 24)

        self.next_round()

    def scramble_string(self, word):
        letters = list(word)
        while True:
            random.shuffle(letters)
            shuffled = "".join(letters)
            if shuffled != word or len(word) <= 1:
                return shuffled

    def next_round(self):
        self.secret_word = random.choice(self.words)
        self.scrambled_word = self.scramble_string(self.secret_word)
        self.hints_used = 0
        self.rack = []
        self.round_start = pygame.time.get_ticks()
        self.input_box.clear()

    def set_feedback(self, msg, color):
        self.feedback_msg = msg
        self.feedback_color = color
        self.feedback_time = pygame.time.get_ticks()

    def submit_guess(self):
        guess = self.input_box.text.strip().upper()
        if not guess:
            self.set_feedback("Type a word before submitting!", (240, 170, 50))
            return

        is_correct = (guess == self.secret_word)

        if is_correct:
            self.score += 1
            self.set_feedback(f"CORRECT! '{self.secret_word}' is right.", (80, 230, 110))
            self.next_round()
        else:
            self.set_feedback("WRONG GUESS! Try again.", (240, 80, 80))
            self.input_box.clear()
            self.rack = []

    def use_hint(self):
        if self.hints_used >= len(self.secret_word):
            self.set_feedback("All letters already revealed!", (240, 170, 50))
            return
        self.hints_used += 1
        self.score = max(0, self.score - self.HINT_PENALTY)
        self.set_feedback(f"Hint used! -{self.HINT_PENALTY:g} point", (240, 170, 50))

    def hint_display(self):
        return " ".join(
            self.secret_word[i] if i < self.hints_used else "_"
            for i in range(len(self.secret_word))
        )

    def tile_rect(self, slot, y):
        n = len(self.scrambled_word)
        total_w = n * self.TILE + (n - 1) * self.TILE_GAP
        x = self.width // 2 - total_w // 2 + slot * (self.TILE + self.TILE_GAP)
        return pygame.Rect(x, y, self.TILE, self.TILE)

    def rack_word(self):
        return "".join(self.scrambled_word[i] for i in self.rack)

    def handle_tile_click(self, pos):
        # Click a tile already in the rack: send it back to the top row
        for slot in range(len(self.rack)):
            if self.tile_rect(slot, self.RACK_Y).collidepoint(pos):
                self.rack.pop(slot)
                self.input_box.text = self.rack_word()
                self.input_box.active = True
                return
        # Click a tile in the top row: move it into the rack
        for i in range(len(self.scrambled_word)):
            if i not in self.rack and self.tile_rect(i, self.TILE_Y).collidepoint(pos):
                self.rack.append(i)
                self.input_box.text = self.rack_word()
                self.input_box.active = True
                return

    def draw_tile(self, screen, rect, letter, fill, border):
        pygame.draw.rect(screen, fill, rect, border_radius=8)
        pygame.draw.rect(screen, border, rect, width=2, border_radius=8)
        surf = self.font_tile.render(letter, True, (255, 255, 255))
        screen.blit(surf, (rect.centerx - surf.get_width() // 2,
                           rect.centery - surf.get_height() // 2))

    def handle_event(self, event):
        # Typing on the keyboard takes over: send all tiles back to the top row
        if (event.type == pygame.KEYDOWN and self.rack
                and (event.key == pygame.K_BACKSPACE or event.unicode.isalpha())):
            self.rack = []

        self.input_box.handle_event(event)

        if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
            self.submit_guess()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.submit_btn.collidepoint(event.pos):
                self.submit_guess()
                self.input_box.active = True
            elif self.hint_btn.collidepoint(event.pos):
                self.use_hint()
                self.input_box.active = True
            else:
                self.handle_tile_click(event.pos)

    def time_left_ms(self):
        elapsed = pygame.time.get_ticks() - self.round_start
        return max(0, self.ROUND_TIME_MS - elapsed)

    def update(self):
        if self.time_left_ms() <= 0:
            self.set_feedback(f"TIME'S UP! The word was {self.secret_word}.", (240, 80, 80))
            self.next_round()
        elif (self.feedback_msg != self.DEFAULT_MSG
              and pygame.time.get_ticks() - self.feedback_time > self.FEEDBACK_MS):
            self.set_feedback(self.DEFAULT_MSG, (210, 215, 225))

    def render(self, screen):
        screen.fill((26, 30, 38))

        title_surf = self.font_title.render("Word Scramble Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 25))

        score_surf = self.font_msg.render(f"Score: {self.score:g}", True, (255, 220, 80))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 70))

        # Top row: scrambled letter tiles
        for i, letter in enumerate(self.scrambled_word):
            rect = self.tile_rect(i, self.TILE_Y)
            if i in self.rack:
                pygame.draw.rect(screen, (36, 41, 51), rect, border_radius=8)
                pygame.draw.rect(screen, (60, 66, 78), rect, width=2, border_radius=8)
            else:
                self.draw_tile(screen, rect, letter, (60, 130, 200), (140, 200, 255))

        # Rack row: the player's arrangement
        for slot in range(len(self.scrambled_word)):
            rect = self.tile_rect(slot, self.RACK_Y)
            if slot < len(self.rack):
                letter = self.scrambled_word[self.rack[slot]]
                self.draw_tile(screen, rect, letter, (50, 150, 85), (150, 235, 180))
            else:
                pygame.draw.rect(screen, (32, 36, 44), rect, border_radius=8)
                pygame.draw.rect(screen, (85, 92, 105), rect, width=2, border_radius=8)

        if self.hints_used > 0:
            hint_surf = self.font_msg.render(self.hint_display(), True, (170, 235, 190))
            screen.blit(hint_surf, (self.width // 2 - hint_surf.get_width() // 2, 218))

        self.input_box.render(screen)

        pygame.draw.rect(screen, (50, 150, 85), self.submit_btn, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), self.submit_btn, width=2, border_radius=6)
        btn_text = self.font_btn.render("SUBMIT", True, (255, 255, 255))
        screen.blit(btn_text, (self.submit_btn.centerx - btn_text.get_width() // 2, self.submit_btn.centery - btn_text.get_height() // 2))

        pygame.draw.rect(screen, (200, 140, 40), self.hint_btn, border_radius=6)
        pygame.draw.rect(screen, (220, 220, 220), self.hint_btn, width=2, border_radius=6)
        hint_text = self.font_btn.render("HINT", True, (255, 255, 255))
        screen.blit(hint_text, (self.hint_btn.centerx - hint_text.get_width() // 2, self.hint_btn.centery - hint_text.get_height() // 2))

        feedback_surf = self.font_msg.render(self.feedback_msg, True, self.feedback_color)
        screen.blit(feedback_surf, (self.width // 2 - feedback_surf.get_width() // 2, 315))

        # Countdown timer bar
        bar_w, bar_h = 400, 16
        bar_x = self.width // 2 - bar_w // 2
        bar_y = 360
        frac = self.time_left_ms() / self.ROUND_TIME_MS
        if frac > 0.5:
            bar_color = (80, 230, 110)
        elif frac > 0.25:
            bar_color = (240, 190, 60)
        else:
            bar_color = (240, 80, 80)
        pygame.draw.rect(screen, (60, 65, 75), (bar_x, bar_y, bar_w, bar_h), border_radius=8)
        pygame.draw.rect(screen, bar_color, (bar_x, bar_y, int(bar_w * frac), bar_h), border_radius=8)
        secs = (self.time_left_ms() + 999) // 1000
        time_surf = self.font_msg.render(f"{secs}s", True, (210, 215, 225))
        screen.blit(time_surf, (bar_x + bar_w + 12, bar_y - 1))