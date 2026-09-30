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

        self.input_box = TextBox(width // 2 - 130, 210, 160, 46)
        self.submit_btn = pygame.Rect(width // 2 + 45, 210, 95, 46)
        self.hint_btn = pygame.Rect(width // 2 + 150, 210, 95, 46)
        self.HINT_PENALTY = 0.5
        self.hints_used = 0
        self.ROUND_TIME_MS = 20000
        self.round_start = 0

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
        self.round_start = pygame.time.get_ticks()
        self.input_box.clear()

    def submit_guess(self):
        guess = self.input_box.text.strip().upper()
        if not guess:
            self.feedback_msg = "Type a word before submitting!"
            self.feedback_color = (240, 170, 50)
            return

        # BUG SYMPTON: 
        # Player's guess is validated against the scrambled text instead of the original solution.
        is_correct = (guess == self.secret_word)

        if is_correct:
            self.score += 1
            self.feedback_msg = f"CORRECT! '{self.secret_word}' is right."
            self.feedback_color = (80, 230, 110)
            self.next_round()
        else:
            self.feedback_msg = "WRONG GUESS! Try again."
            self.feedback_color = (240, 80, 80)
            self.input_box.clear()

    def use_hint(self):
        if self.hints_used >= len(self.secret_word):
            self.feedback_msg = "All letters already revealed!"
            self.feedback_color = (240, 170, 50)
            return
        self.hints_used += 1
        self.score = max(0, self.score - self.HINT_PENALTY)
        self.feedback_msg = f"Hint used! -{self.HINT_PENALTY:g} point"
        self.feedback_color = (240, 170, 50)

    def hint_display(self):
        return " ".join(
            self.secret_word[i] if i < self.hints_used else "_"
            for i in range(len(self.secret_word))
        )

    def handle_event(self, event):
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

    def time_left_ms(self):
        elapsed = pygame.time.get_ticks() - self.round_start
        return max(0, self.ROUND_TIME_MS - elapsed)

    def update(self):
        if self.time_left_ms() <= 0:
            self.feedback_msg = f"TIME'S UP! The word was {self.secret_word}."
            self.feedback_color = (240, 80, 80)
            self.next_round()

    def render(self, screen):
        screen.fill((26, 30, 38))

        title_surf = self.font_title.render("Word Scramble Arena", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 25))

        score_surf = self.font_msg.render(f"Score: {self.score:g}", True, (255, 220, 80))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, 70))

        spaced_letters = "  ".join(self.scrambled_word)
        scramble_surf = self.font_word.render(spaced_letters, True, (100, 200, 255))
        screen.blit(scramble_surf, (self.width // 2 - scramble_surf.get_width() // 2, 130))

        if self.hints_used > 0:
            hint_surf = self.font_msg.render(self.hint_display(), True, (170, 235, 190))
            screen.blit(hint_surf, (self.width // 2 - hint_surf.get_width() // 2, 176))

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
        screen.blit(feedback_surf, (self.width // 2 - feedback_surf.get_width() // 2, 285))
                # Countdown timer bar
        bar_w, bar_h = 400, 16
        bar_x = self.width // 2 - bar_w // 2
        bar_y = 330
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