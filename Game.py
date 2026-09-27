import pygame
import random
import os
from Trie import Trie
from Board import Board

class GameUI:
    def __init__(self, board, trie):
        pygame.init()
        pygame.font.init()
        
        try:
            pygame.mixer.init()
            self.volume = 0.5
            if os.path.exists("music.mp3"):
                pygame.mixer.music.load("music.mp3")
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play(-1)
        except:
            self.volume = 0.5

        self.board_logic = board
        self.trie = trie
        
        self.WIDTH, self.HEIGHT = 800, 800
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Trie Word Hunt")
        self.clock = pygame.time.Clock()

        self.state = "GAME"
        self.setting_rows = self.board_logic.rows
        self.setting_cols = self.board_logic.cols

        self.selected_path = []  
        self.is_selecting = False
        self.found_words = set()
        self.score = 0

        self.hints_remaining = 3
        self.current_hint = ""

        self.all_valid_words = self.board_logic.get_all_valid_words(self.board_logic.board)
        self.target_words = min(len(self.all_valid_words), max(5, int((self.setting_rows * self.setting_cols) * 0.4)))
        self.time_limit = self.target_words * 20
        self.start_ticks = pygame.time.get_ticks()

        self.start_x = 0
        self.start_y = 0
        self.tile_size = 0
        self.padding = 8
        
        self.settings_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.hint_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.row_minus_rect = pygame.Rect(0, 0, 0, 0)
        self.row_plus_rect = pygame.Rect(0, 0, 0, 0)
        self.col_minus_rect = pygame.Rect(0, 0, 0, 0)
        self.col_plus_rect = pygame.Rect(0, 0, 0, 0)
        self.volume_minus_rect = pygame.Rect(0, 0, 0, 0)
        self.volume_plus_rect = pygame.Rect(0, 0, 0, 0)
        self.back_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.apply_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.new_game_btn_rect = pygame.Rect(0, 0, 0, 0)

        self.BG_COLOR = (30, 30, 46)
        self.PANEL_COLOR = (24, 24, 37)
        self.TILE_COLOR = (49, 50, 68)
        self.SELECTED_COLOR = (137, 180, 250)  
        self.LINE_COLOR = (245, 194, 231)      
        self.TEXT_COLOR = (205, 214, 244)
        self.FOUND_COLOR = (166, 227, 161)     
        self.BTN_COLOR = (203, 166, 247)
        self.WARN_COLOR = (243, 139, 168)

    def start_new_game(self):
        self.board_logic = Board(rows=self.setting_rows, cols=self.setting_cols, trie=self.trie, min_words=4)
        self.all_valid_words = self.board_logic.get_all_valid_words(self.board_logic.board)
        self.found_words.clear()
        self.score = 0
        self.selected_path = []
        self.hints_remaining = 3
        self.current_hint = ""
        self.target_words = min(len(self.all_valid_words), max(5, int((self.setting_rows * self.setting_cols) * 0.4)))
        self.time_limit = self.target_words * 20
        self.start_ticks = pygame.time.get_ticks()
        self.state = "GAME"

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            elif event.type == pygame.VIDEORESIZE:
                self.WIDTH, self.HEIGHT = event.w, event.h
                self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)

            if self.state == "SETTINGS":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.row_minus_rect.collidepoint(event.pos) and self.setting_rows > 3:
                        self.setting_rows -= 1
                    elif self.row_plus_rect.collidepoint(event.pos) and self.setting_rows < 12:
                        self.setting_rows += 1
                    elif self.col_minus_rect.collidepoint(event.pos) and self.setting_cols > 3:
                        self.setting_cols -= 1
                    elif self.col_plus_rect.collidepoint(event.pos) and self.setting_cols < 12:
                        self.setting_cols += 1
                    elif self.volume_minus_rect.collidepoint(event.pos):
                        self.volume = max(0.0, self.volume - 0.1)
                        try:
                            pygame.mixer.music.set_volume(self.volume)
                        except:
                            pass
                    elif self.volume_plus_rect.collidepoint(event.pos):
                        self.volume = min(1.0, self.volume + 0.1)
                        try:
                            pygame.mixer.music.set_volume(self.volume)
                        except:
                            pass
                    elif self.back_btn_rect.collidepoint(event.pos):
                        self.setting_rows = self.board_logic.rows
                        self.setting_cols = self.board_logic.cols
                        self.state = "GAME"
                    elif self.apply_btn_rect.collidepoint(event.pos):
                        self.start_new_game()

            elif self.state in ["WIN", "LOSE"]:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.new_game_btn_rect.collidepoint(event.pos):
                        self.start_new_game()

            elif self.state == "GAME":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.settings_btn_rect.collidepoint(event.pos):
                        self.state = "SETTINGS"
                    
                    elif self.hint_btn_rect.collidepoint(event.pos):
                        if self.hints_remaining > 0:
                            unfound_words = self.all_valid_words - self.found_words
                            if unfound_words:
                                hint_word = random.choice(list(unfound_words))
                                self.current_hint = hint_word[:2].upper() + " _" * (len(hint_word) - 2)
                                self.hints_remaining -= 1
                    
                    else:
                        tile = self.get_tile_at_pos(event.pos)
                        if tile:
                            self.is_selecting = True
                            self.selected_path = [tile]

                elif event.type == pygame.MOUSEMOTION and self.is_selecting:
                    tile = self.get_tile_at_pos(event.pos)
                    if tile:
                        last_tile = self.selected_path[-1]
                        if len(self.selected_path) > 1 and tile == self.selected_path[-2]:
                            self.selected_path.pop()
                        elif tile not in self.selected_path and self.is_adjacent(last_tile, tile):
                            self.selected_path.append(tile)

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    if self.is_selecting:
                        self.is_selecting = False
                        self.check_selected_word()
                        self.selected_path = []

        return True

    def get_tile_at_pos(self, pos):
        px, py = pos
        if self.tile_size == 0:
            return None
            
        for r in range(self.board_logic.rows):
            for c in range(self.board_logic.cols):
                x = self.start_x + c * (self.tile_size + self.padding)
                y = self.start_y + r * (self.tile_size + self.padding)
                rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                hitbox = rect.inflate(-self.tile_size * 0.4, -self.tile_size * 0.4)
                if hitbox.collidepoint(px, py):
                    return (r, c)
        return None

    def is_adjacent(self, tile1, tile2):
        r1, c1 = tile1
        r2, c2 = tile2
        return abs(r1 - r2) <= 1 and abs(c1 - c2) <= 1 and tile1 != tile2

    def check_selected_word(self):
        word = "".join(self.board_logic.board[r][c] for r, c in self.selected_path).lower()
        
        if len(word) >= 3 and self.trie.search(word):
            if word not in self.found_words:
                self.found_words.add(word)
                self.score += len(word) * 100

    def check_game_state(self):
        if self.state == "GAME":
            if len(self.found_words) >= self.target_words:
                self.state = "WIN"
            else:
                elapsed = (pygame.time.get_ticks() - self.start_ticks) // 1000
                if self.time_limit - elapsed <= 0:
                    self.state = "LOSE"

    def draw_end_screen(self, title_text, color):
        self.screen.fill(self.BG_COLOR)
        
        panel_w, panel_h = 400, 300
        panel_x = (self.WIDTH - panel_w) // 2
        panel_y = (self.HEIGHT - panel_h) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        
        pygame.draw.rect(self.screen, self.PANEL_COLOR, panel_rect, border_radius=16)
        
        title_font = pygame.font.SysFont("arial", 40, bold=True)
        text_font = pygame.font.SysFont("arial", 24, bold=True)
        
        title = title_font.render(title_text, True, color)
        self.screen.blit(title, title.get_rect(center=(self.WIDTH // 2, panel_y + 60)))
        
        score_txt = text_font.render(f"Final Score: {self.score}", True, self.TEXT_COLOR)
        self.screen.blit(score_txt, score_txt.get_rect(center=(self.WIDTH // 2, panel_y + 130)))
        
        self.new_game_btn_rect = pygame.Rect(panel_x + 50, panel_y + 200, panel_w - 100, 50)
        pygame.draw.rect(self.screen, self.BTN_COLOR, self.new_game_btn_rect, border_radius=12)
        btn_txt = text_font.render("Play Again", True, (30, 30, 46))
        self.screen.blit(btn_txt, btn_txt.get_rect(center=self.new_game_btn_rect.center))

    def draw_settings(self):
        self.screen.fill(self.BG_COLOR)
        
        panel_w, panel_h = 420, 480
        panel_x = (self.WIDTH - panel_w) // 2
        panel_y = (self.HEIGHT - panel_h) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        
        pygame.draw.rect(self.screen, self.PANEL_COLOR, panel_rect, border_radius=16)
        
        title_font = pygame.font.SysFont("arial", 32, bold=True)
        btn_font = pygame.font.SysFont("arial", 24, bold=True)
        
        title = title_font.render("Board Settings", True, self.TEXT_COLOR)
        self.screen.blit(title, title.get_rect(center=(self.WIDTH // 2, panel_y + 40)))

        row_txt = btn_font.render(f"Rows:  {self.setting_rows}", True, self.TEXT_COLOR)
        self.screen.blit(row_txt, (panel_x + 50, panel_y + 110))
        self.row_minus_rect = pygame.Rect(panel_x + 280, panel_y + 105, 35, 35)
        self.row_plus_rect = pygame.Rect(panel_x + 330, panel_y + 105, 35, 35)
        
        col_txt = btn_font.render(f"Columns:  {self.setting_cols}", True, self.TEXT_COLOR)
        self.screen.blit(col_txt, (panel_x + 50, panel_y + 170))
        self.col_minus_rect = pygame.Rect(panel_x + 280, panel_y + 165, 35, 35)
        self.col_plus_rect = pygame.Rect(panel_x + 330, panel_y + 165, 35, 35)

        vol_txt = btn_font.render(f"Volume:  {int(self.volume * 100)}%", True, self.TEXT_COLOR)
        self.screen.blit(vol_txt, (panel_x + 50, panel_y + 230))
        self.volume_minus_rect = pygame.Rect(panel_x + 280, panel_y + 225, 35, 35)
        self.volume_plus_rect = pygame.Rect(panel_x + 330, panel_y + 225, 35, 35)

        for rect in [self.row_minus_rect, self.row_plus_rect, self.col_minus_rect, 
                     self.col_plus_rect, self.volume_minus_rect, self.volume_plus_rect]:
            pygame.draw.rect(self.screen, self.TILE_COLOR, rect, border_radius=8)

        self.screen.blit(btn_font.render("-", True, self.TEXT_COLOR), self.row_minus_rect.move(11, 2))
        self.screen.blit(btn_font.render("+", True, self.TEXT_COLOR), self.row_plus_rect.move(9, 2))
        self.screen.blit(btn_font.render("-", True, self.TEXT_COLOR), self.col_minus_rect.move(11, 2))
        self.screen.blit(btn_font.render("+", True, self.TEXT_COLOR), self.col_plus_rect.move(9, 2))
        self.screen.blit(btn_font.render("-", True, self.TEXT_COLOR), self.volume_minus_rect.move(11, 2))
        self.screen.blit(btn_font.render("+", True, self.TEXT_COLOR), self.volume_plus_rect.move(9, 2))

        self.back_btn_rect = pygame.Rect(panel_x + 50, panel_y + 310, panel_w - 100, 50)
        pygame.draw.rect(self.screen, self.TILE_COLOR, self.back_btn_rect, border_radius=12)
        back_txt = btn_font.render("Back to Game", True, self.TEXT_COLOR)
        self.screen.blit(back_txt, back_txt.get_rect(center=self.back_btn_rect.center))

        self.apply_btn_rect = pygame.Rect(panel_x + 50, panel_y + 380, panel_w - 100, 50)
        pygame.draw.rect(self.screen, self.BTN_COLOR, self.apply_btn_rect, border_radius=12)
        apply_txt = btn_font.render("Apply & New Game", True, (30, 30, 46))
        self.screen.blit(apply_txt, apply_txt.get_rect(center=self.apply_btn_rect.center))

    def draw_board(self):
        if self.state == "SETTINGS":
            self.draw_settings()
            return
        elif self.state == "WIN":
            self.draw_end_screen("You Win!", self.FOUND_COLOR)
            return
        elif self.state == "LOSE":
            self.draw_end_screen("Time's Up!", self.WARN_COLOR)
            return

        self.screen.fill(self.BG_COLOR)

        margin_x = 40
        margin_y = 130 
        
        avail_w = self.WIDTH - (margin_x * 2)
        avail_h = self.HEIGHT - margin_y - 100
        
        temp_max_w = avail_w // self.board_logic.cols if self.board_logic.cols > 0 else 10
        self.padding = max(12, int(temp_max_w * 0.15))

        if self.board_logic.cols > 0 and self.board_logic.rows > 0:
            max_tile_w = (avail_w - (self.board_logic.cols - 1) * self.padding) // self.board_logic.cols
            max_tile_h = (avail_h - (self.board_logic.rows - 1) * self.padding) // self.board_logic.rows
            self.tile_size = max(10, min(max_tile_w, max_tile_h))

        font_size = max(12, int(self.tile_size * 0.5))
        dynamic_font = pygame.font.SysFont("arial", font_size, bold=True)
        header_font = pygame.font.SysFont("arial", 24, bold=True)
        score_font = pygame.font.SysFont("arial", 20, bold=True)

        total_grid_w = self.board_logic.cols * self.tile_size + (self.board_logic.cols - 1) * self.padding
        total_grid_h = self.board_logic.rows * self.tile_size + (self.board_logic.rows - 1) * self.padding
        self.start_x = (self.WIDTH - total_grid_w) // 2
        self.start_y = margin_y + (avail_h - total_grid_h) // 2

        self.settings_btn_rect = pygame.Rect(self.WIDTH - 150, 20, 110, 40)
        pygame.draw.rect(self.screen, self.TILE_COLOR, self.settings_btn_rect, border_radius=8)
        settings_txt = header_font.render("Settings", True, self.TEXT_COLOR)
        self.screen.blit(settings_txt, settings_txt.get_rect(center=self.settings_btn_rect.center))

        current_word = "".join(self.board_logic.board[r][c] for r, c in self.selected_path).upper()
        elapsed = (pygame.time.get_ticks() - self.start_ticks) // 1000
        remaining_time = max(0, self.time_limit - elapsed)
        
        word_surface = header_font.render(f"Word: {current_word}", True, self.TEXT_COLOR)
        stat_string = f"Score: {self.score} | Target: {len(self.found_words)}/{self.target_words} | Time: {remaining_time}s"
        score_surface = score_font.render(stat_string, True, self.FOUND_COLOR)
        self.screen.blit(word_surface, (self.start_x, 30))
        self.screen.blit(score_surface, (self.start_x, 70))

        for r in range(self.board_logic.rows):
            for c in range(self.board_logic.cols):
                x = self.start_x + c * (self.tile_size + self.padding)
                y = self.start_y + r * (self.tile_size + self.padding)
                rect = pygame.Rect(x, y, self.tile_size, self.tile_size)

                tile_bg = self.SELECTED_COLOR if (r, c) in self.selected_path else self.TILE_COLOR
                pygame.draw.rect(self.screen, tile_bg, rect, border_radius=max(4, self.tile_size // 6))

                char = self.board_logic.board[r][c].upper()
                text_color = (30, 30, 46) if (r, c) in self.selected_path else self.TEXT_COLOR
                text_surface = dynamic_font.render(char, True, text_color)
                text_rect = text_surface.get_rect(center=rect.center)
                self.screen.blit(text_surface, text_rect)

        hint_y = self.start_y + total_grid_h + 20
        self.hint_btn_rect = pygame.Rect(self.start_x, hint_y, 140, 45)
        pygame.draw.rect(self.screen, self.TILE_COLOR, self.hint_btn_rect, border_radius=8)
        
        hint_btn_font = pygame.font.SysFont("arial", 20, bold=True)
        hint_txt = hint_btn_font.render(f"Hint ({self.hints_remaining})", True, self.TEXT_COLOR)
        self.screen.blit(hint_txt, hint_txt.get_rect(center=self.hint_btn_rect.center))

        if self.current_hint:
            hint_display = header_font.render(f"Hint: {self.current_hint}", True, self.LINE_COLOR)
            self.screen.blit(hint_display, (self.start_x + 160, hint_y + 5))

        if len(self.selected_path) > 1:
            points = []
            for r, c in self.selected_path:
                cx = self.start_x + c * (self.tile_size + self.padding) + self.tile_size // 2
                cy = self.start_y + r * (self.tile_size + self.padding) + self.tile_size // 2
                points.append((cx, cy))
            pygame.draw.lines(self.screen, self.LINE_COLOR, False, points, max(3, self.tile_size // 8))

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            running = self.handle_events()
            self.check_game_state()
            self.draw_board()
            pygame.display.flip()
            
        pygame.quit()


if __name__ == "__main__":
    trie = Trie()
    
    try:
        with open("enable1.txt", "r") as f:
            for word in f.read().splitlines():
                trie.add(word.strip().lower())
    except:
        pass
        
    board = Board(rows=5, cols=5, trie=trie, min_words=4)
    ui = GameUI(board, trie)
    ui.run()