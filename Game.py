import os, sys, math, json, random, pygame
from Trie import Trie
from Board import Board

class GameUI:
    def __init__(self, board, trie):
        pygame.init()
        pygame.font.init()
        
        self.trie = trie
        
        # Audio setup
        self.volume = 0.5
        self.music_tracks = []
        for name in ["music1.mp3", "music2.mp3", "music3.mp3"]:
            path =  resource_path(os.path.join("sounds", name))
            if os.path.exists(path):
                self.music_tracks.append(path)
        
        self.current_music_idx = 0
        self.MUSIC_END_EVENT = pygame.USEREVENT + 1
        try:
            pygame.mixer.init()
            if self.music_tracks:
                pygame.mixer.music.set_endevent(self.MUSIC_END_EVENT)
        except:
            pass

        # Screen setup: Force fullscreen/maximized initially, but allow resize with minimum bounds
        info = pygame.display.Info()
        self.WIDTH = max(800, info.current_w)
        self.HEIGHT = max(600, info.current_h)
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption("Trie Word Hunt")
        self.clock = pygame.time.Clock()

        # Default Settings
        self.is_dark_mode = True
        self.setting_rows = 5
        self.setting_cols = 5
        
        # Scale & Fonts Setup
        self.scale = 1.0
        self.init_fonts()
        
        # Game State Variables
        self.state = "MENU"
        self.previous_state = "MENU"
        self.board_logic = board
        self.selected_path = []  
        self.is_selecting = False
        self.found_words = set()
        self.score = 0
        self.hints_remaining = 3
        self.hint_path = []
        self.target_words = 0
        self.time_left = 0
        self.has_saved_game = False
        self.popups = []
        
        # Timing
        self.last_time = pygame.time.get_ticks()

        # UI Layout vars
        self.start_x = 0
        self.start_y = 0
        self.tile_size = 0
        self.padding = 8
        self.is_dragging_slider = False
        
        # Left Sidebar
        self.show_sidebar = False
        self.sidebar_scroll = 0
        self.sidebar_w = 260
        self.sidebar_tab_rect = pygame.Rect(0, 0, 0, 0)

        # Interactive Rects
        self.new_game_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.continue_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.menu_settings_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.menu_exit_btn_rect = pygame.Rect(0, 0, 0, 0)
        
        self.settings_theme_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.settings_exit_btn_rect = pygame.Rect(0, 0, 0, 0)
        
        self.settings_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.theme_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.home_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.hint_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.row_minus_rect = pygame.Rect(0, 0, 0, 0)
        self.row_plus_rect = pygame.Rect(0, 0, 0, 0)
        self.col_minus_rect = pygame.Rect(0, 0, 0, 0)
        self.col_plus_rect = pygame.Rect(0, 0, 0, 0)
        self.slider_track_rect = pygame.Rect(0, 0, 0, 0)
        self.slider_knob_rect = pygame.Rect(0, 0, 0, 0)
        self.back_btn_rect = pygame.Rect(0, 0, 0, 0)
        self.apply_btn_rect = pygame.Rect(0, 0, 0, 0)

        # Load game and apply theme
        self.load_game()
        self.apply_theme()
        self.play_current_music()

    def init_fonts(self):
        self.scale = min(self.WIDTH / 800.0, self.HEIGHT / 800.0)
        self.sidebar_w = int(240 * self.scale)
        
        self.font_title = pygame.font.SysFont("arial", int(60 * self.scale), bold=True)
        self.font_h1 = pygame.font.SysFont("arial", int(40 * self.scale), bold=True)
        self.font_h2 = pygame.font.SysFont("arial", int(32 * self.scale), bold=True)
        self.font_btn = pygame.font.SysFont("arial", int(26 * self.scale), bold=True)
        self.font_body = pygame.font.SysFont("arial", int(22 * self.scale), bold=True)
        self.font_list = pygame.font.SysFont("arial", int(20 * self.scale))

    def apply_theme(self):
        if self.is_dark_mode:
            self.BG_COLOR = (30, 30, 46)
            self.PANEL_COLOR = (24, 24, 37)
            self.TILE_COLOR = (49, 50, 68)
            self.SELECTED_COLOR = (137, 180, 250)  
            self.LINE_COLOR = (245, 194, 231)      
            self.TEXT_COLOR = (205, 214, 244)
            self.FOUND_COLOR = (166, 227, 161)     
            self.BTN_COLOR = (203, 166, 247)
            self.WARN_COLOR = (243, 139, 168)
            self.CARD_BG = (45, 45, 65)
            self.ICON_COLOR = (205, 214, 244)
            self.POPUP_BG = (30, 30, 46)
        else:
            self.BG_COLOR = (239, 241, 245)
            self.PANEL_COLOR = (230, 233, 239)
            self.TILE_COLOR = (204, 208, 218)
            self.SELECTED_COLOR = (30, 102, 245)  
            self.LINE_COLOR = (234, 118, 203)      
            self.TEXT_COLOR = (76, 79, 105)
            self.FOUND_COLOR = (64, 160, 43)     
            self.BTN_COLOR = (136, 57, 239)
            self.WARN_COLOR = (210, 15, 57)
            self.CARD_BG = (218, 224, 236)
            self.ICON_COLOR = (76, 79, 105)
            self.POPUP_BG = (239, 241, 245)

    def play_current_music(self):
        if self.music_tracks:
            try:
                pygame.mixer.music.load(self.music_tracks[self.current_music_idx])
                pygame.mixer.music.set_volume(self.volume)
                pygame.mixer.music.play()
            except:
                pass

    def load_game(self):
        try:
            if os.path.exists("savegame.json"):
                with open("savegame.json", "r") as f:
                    data = json.load(f)
                    
                self.is_dark_mode = data.get("is_dark_mode", True)
                self.volume = data.get("volume", 0.5)
                self.setting_rows = data.get("setting_rows", 5)
                self.setting_cols = data.get("setting_cols", 5)
                
                if data.get("game_active"):
                    self.board_logic = Board(self.setting_rows, self.setting_cols, self.trie, 4)
                    self.board_logic.board = data["board"]
                    self.all_valid_words = self.board_logic.get_all_valid_words(self.board_logic.board)
                    self.found_words = set(data.get("found_words", []))
                    self.score = data.get("score", 0)
                    self.hints_remaining = data.get("hints_remaining", 3)
                    self.time_left = data.get("time_left", 60)
                    self.target_words = data.get("target_words", 5)
                    self.has_saved_game = True
                else:
                    self.has_saved_game = False
        except Exception:
            self.has_saved_game = False

    def save_game(self):
        game_active = self.has_saved_game and self.state not in ["WIN", "LOSE"]
        data = {
            "is_dark_mode": self.is_dark_mode,
            "volume": self.volume,
            "setting_rows": self.setting_rows,
            "setting_cols": self.setting_cols,
            "game_active": game_active
        }
        
        if game_active and hasattr(self, 'board_logic'):
            data.update({
                "board": self.board_logic.board,
                "found_words": list(self.found_words),
                "score": self.score,
                "hints_remaining": self.hints_remaining,
                "time_left": self.time_left,
                "target_words": self.target_words
            })
            
        try:
            with open("savegame.json", "w") as f:
                json.dump(data, f)
        except:
            pass

    def start_new_game(self):
        self.board_logic = Board(rows=self.setting_rows, cols=self.setting_cols, trie=self.trie, min_words=4)
        self.all_valid_words = self.board_logic.get_all_valid_words(self.board_logic.board)
        self.found_words.clear()
        self.score = 0
        self.selected_path = []
        self.hint_path = []
        self.hints_remaining = 3
        self.target_words = min(len(self.all_valid_words), max(5, int((self.setting_rows * self.setting_cols) * 0.4)))
        self.time_left = self.target_words * 20
        self.has_saved_game = True
        self.popups.clear()
        self.state = "GAME"
        self.show_sidebar = False
        self.save_game()

    def get_word_path(self, target_word):
        def dfs(r, c, idx, current_path):
            if idx == len(target_word):
                return current_path
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0: continue
                    nr, nc = r + dr, c + dc
                    if 0 <= nr < self.board_logic.rows and 0 <= nc < self.board_logic.cols:
                        if (nr, nc) not in current_path:
                            if self.board_logic.board[nr][nc].lower() == target_word[idx]:
                                res = dfs(nr, nc, idx + 1, current_path + [(nr, nc)])
                                if res: return res
            return None
        
        for r in range(self.board_logic.rows):
            for c in range(self.board_logic.cols):
                if self.board_logic.board[r][c].lower() == target_word[0]:
                    res = dfs(r, c, 1, [(r, c)])
                    if res: return res
        return []

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.save_game()
                return False
                
            elif event.type == self.MUSIC_END_EVENT:
                if self.music_tracks:
                    self.current_music_idx = (self.current_music_idx + 1) % len(self.music_tracks)
                    self.play_current_music()

            elif event.type == pygame.VIDEORESIZE:
                new_w, new_h = max(800, event.w), max(600, event.h)
                self.WIDTH, self.HEIGHT = new_w, new_h
                self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT), pygame.RESIZABLE)
                self.init_fonts()

            elif event.type == pygame.MOUSEWHEEL:
                if self.state == "GAME" and self.show_sidebar:
                    scroll_amt = int(25 * self.scale)
                    self.sidebar_scroll = max(0, self.sidebar_scroll - event.y * scroll_amt)

            if self.state == "MENU":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.has_saved_game and self.continue_btn_rect.collidepoint(event.pos):
                        self.state = "GAME"
                    elif self.new_game_btn_rect.collidepoint(event.pos):
                        self.start_new_game()
                    elif self.menu_settings_btn_rect.collidepoint(event.pos):
                        self.previous_state = "MENU"
                        self.state = "SETTINGS"
                    elif self.menu_exit_btn_rect.collidepoint(event.pos):
                        self.save_game()
                        return False

            elif self.state == "SETTINGS":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.row_minus_rect.collidepoint(event.pos) and self.setting_rows > 3:
                        self.setting_rows -= 1
                    elif self.row_plus_rect.collidepoint(event.pos) and self.setting_rows < 12:
                        self.setting_rows += 1
                    elif self.col_minus_rect.collidepoint(event.pos) and self.setting_cols > 3:
                        self.setting_cols -= 1
                    elif self.col_plus_rect.collidepoint(event.pos) and self.setting_cols < 12:
                        self.setting_cols += 1
                    elif self.settings_theme_btn_rect.collidepoint(event.pos):
                        self.is_dark_mode = not self.is_dark_mode
                        self.apply_theme()
                        self.save_game()
                    elif self.slider_track_rect.inflate(20, 30).collidepoint(event.pos) or self.slider_knob_rect.collidepoint(event.pos):
                        self.is_dragging_slider = True
                        self.update_volume_from_mouse(event.pos[0])
                    elif self.back_btn_rect.collidepoint(event.pos):
                        self.state = self.previous_state
                        self.save_game()
                    elif self.apply_btn_rect.collidepoint(event.pos):
                        self.start_new_game()
                    elif self.settings_exit_btn_rect.collidepoint(event.pos):
                        self.save_game()
                        return False

                elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    self.is_dragging_slider = False
                    self.save_game()

                elif event.type == pygame.MOUSEMOTION and self.is_dragging_slider:
                    self.update_volume_from_mouse(event.pos[0])

            elif self.state in ["WIN", "LOSE"]:
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.home_btn_rect.collidepoint(event.pos):
                        self.state = "MENU"
                    elif self.new_game_btn_rect.collidepoint(event.pos):
                        self.start_new_game()

            elif self.state == "GAME":
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    if self.sidebar_tab_rect.collidepoint(event.pos):
                        self.show_sidebar = not self.show_sidebar
                    elif self.theme_btn_rect.collidepoint(event.pos):
                        self.is_dark_mode = not self.is_dark_mode
                        self.apply_theme()
                        self.save_game()
                    elif self.settings_btn_rect.collidepoint(event.pos):
                        self.previous_state = "GAME"
                        self.state = "SETTINGS"
                    elif self.home_btn_rect.collidepoint(event.pos):
                        self.save_game()
                        self.state = "MENU"
                    elif self.hint_btn_rect.collidepoint(event.pos):
                        if self.hints_remaining > 0:
                            unfound_words = self.all_valid_words - self.found_words
                            if unfound_words:
                                hint_word = random.choice(list(unfound_words))
                                path = self.get_word_path(hint_word)
                                if path:
                                    self.hint_path = path
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

    def update_volume_from_mouse(self, mouse_x):
        rel_x = max(0, min(mouse_x - self.slider_track_rect.x, self.slider_track_rect.width))
        self.volume = rel_x / float(self.slider_track_rect.width)
        try:
            pygame.mixer.music.set_volume(self.volume)
        except:
            pass

    def get_tile_at_pos(self, pos):
        px, py = pos
        if self.tile_size == 0:
            return None
            
        for r in range(self.board_logic.rows):
            for c in range(self.board_logic.cols):
                x = self.start_x + c * (self.tile_size + self.padding)
                y = self.start_y + r * (self.tile_size + self.padding)
                rect = pygame.Rect(x, y, self.tile_size, self.tile_size)
                hitbox = rect.inflate(-self.tile_size * 0.35, -self.tile_size * 0.35)
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
                self.hint_path = []
                
                # Setup Pop-up Animation
                cx = sum(c for r, c in self.selected_path) / len(self.selected_path)
                cy = sum(r for r, c in self.selected_path) / len(self.selected_path)
                screen_x = self.start_x + cx * (self.tile_size + self.padding) + self.tile_size // 2
                screen_y = self.start_y + cy * (self.tile_size + self.padding) + self.tile_size // 2
                
                self.popups.append({
                    "text": f"FOUND: {word.upper()}",
                    "start": pygame.time.get_ticks(),
                    "duration": 1200, 
                    "x": screen_x,
                    "y": screen_y
                })

    def draw_gear_icon(self, surface, center, radius, color):
        cx, cy = center
        pygame.draw.circle(surface, color, center, int(radius * 0.85), max(2, int(3 * self.scale)))
        pygame.draw.circle(surface, color, center, int(radius * 0.35))
        for i in range(8):
            angle = i * (math.pi / 4)
            x1 = cx + math.cos(angle) * (radius * 0.6)
            y1 = cy + math.sin(angle) * (radius * 0.6)
            x2 = cx + math.cos(angle) * (radius * 1.05)
            y2 = cy + math.sin(angle) * (radius * 1.05)
            pygame.draw.line(surface, color, (x1, y1), (x2, y2), max(2, int(3 * self.scale)))

    def draw_theme_icon(self, surface, center, radius, color):
        cx, cy = center
        if self.is_dark_mode:
            pygame.draw.circle(surface, color, center, radius)
            pygame.draw.circle(surface, self.CARD_BG, (cx + radius // 2, cy - radius // 3), radius)
        else:
            pygame.draw.circle(surface, color, center, radius // 2)
            for i in range(8):
                angle = i * (math.pi / 4)
                x1 = cx + math.cos(angle) * (radius // 2 + 3)
                y1 = cy + math.sin(angle) * (radius // 2 + 3)
                x2 = cx + math.cos(angle) * radius
                y2 = cy + math.sin(angle) * radius
                pygame.draw.line(surface, color, (x1, y1), (x2, y2), 2)

    def draw_home_icon(self, surface, center, radius, color):
        cx, cy = center
        w = radius * 1.5
        h = radius * 1.2
        points = [
            (cx, cy - h/2 - 2),
            (cx - w/2 - 2, cy),
            (cx - w/2 + 2, cy),
            (cx - w/2 + 2, cy + h/2),
            (cx + w/2 - 2, cy + h/2),
            (cx + w/2 - 2, cy),
            (cx + w/2 + 2, cy)
        ]
        pygame.draw.polygon(surface, color, points, 2)
        pygame.draw.rect(surface, color, (cx - 3, cy + h/2 - 6, 6, 6))

    def draw_menu(self):
        self.screen.fill(self.BG_COLOR)
        
        title = self.font_title.render("Trie Word Hunt", True, self.TEXT_COLOR)
        self.screen.blit(title, title.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 3)))

        btn_w = int(280 * self.scale)
        btn_h = int(60 * self.scale)
        btn_spacing = int(80 * self.scale)
        btn_y = self.HEIGHT // 2
        
        if self.has_saved_game:
            self.continue_btn_rect = pygame.Rect((self.WIDTH - btn_w) // 2, btn_y, btn_w, btn_h)
            pygame.draw.rect(self.screen, self.BTN_COLOR, self.continue_btn_rect, border_radius=12)
            cont_txt = self.font_btn.render("Continue", True, (30, 30, 46))
            self.screen.blit(cont_txt, cont_txt.get_rect(center=self.continue_btn_rect.center))
            btn_y += btn_spacing

        self.new_game_btn_rect = pygame.Rect((self.WIDTH - btn_w) // 2, btn_y, btn_w, btn_h)
        color = self.BTN_COLOR if not self.has_saved_game else self.TILE_COLOR
        txt_color = (30, 30, 46) if not self.has_saved_game else self.TEXT_COLOR
        pygame.draw.rect(self.screen, color, self.new_game_btn_rect, border_radius=12)
        start_txt = self.font_btn.render("New Game", True, txt_color)
        self.screen.blit(start_txt, start_txt.get_rect(center=self.new_game_btn_rect.center))
        
        btn_y += btn_spacing
        self.menu_settings_btn_rect = pygame.Rect((self.WIDTH - btn_w) // 2, btn_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, self.TILE_COLOR, self.menu_settings_btn_rect, border_radius=12)
        set_txt = self.font_btn.render("Settings", True, self.TEXT_COLOR)
        self.screen.blit(set_txt, set_txt.get_rect(center=self.menu_settings_btn_rect.center))
        
        btn_y += btn_spacing
        self.menu_exit_btn_rect = pygame.Rect((self.WIDTH - btn_w) // 2, btn_y, btn_w, btn_h)
        pygame.draw.rect(self.screen, self.WARN_COLOR, self.menu_exit_btn_rect, border_radius=12)
        exit_txt = self.font_btn.render("Exit Game", True, (30, 30, 46))
        self.screen.blit(exit_txt, exit_txt.get_rect(center=self.menu_exit_btn_rect.center))

    def draw_end_screen(self, title_text, color):
        self.screen.fill(self.BG_COLOR)
        
        panel_w = int(480 * self.scale)
        panel_h = int(360 * self.scale)
        panel_x = (self.WIDTH - panel_w) // 2
        panel_y = (self.HEIGHT - panel_h) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        
        pygame.draw.rect(self.screen, self.PANEL_COLOR, panel_rect, border_radius=16)
        
        title = self.font_h1.render(title_text, True, color)
        self.screen.blit(title, title.get_rect(center=(self.WIDTH // 2, panel_y + int(70 * self.scale))))
        
        score_txt = self.font_h2.render(f"Final Score: {self.score}", True, self.TEXT_COLOR)
        self.screen.blit(score_txt, score_txt.get_rect(center=(self.WIDTH // 2, panel_y + int(150 * self.scale))))
        
        btn_w = int(320 * self.scale)
        btn_h = int(60 * self.scale)
        self.new_game_btn_rect = pygame.Rect(panel_x + (panel_w - btn_w) // 2, panel_y + int(240 * self.scale), btn_w, btn_h)
        pygame.draw.rect(self.screen, self.BTN_COLOR, self.new_game_btn_rect, border_radius=12)
        btn_txt = self.font_btn.render("Play Again", True, (30, 30, 46))
        self.screen.blit(btn_txt, btn_txt.get_rect(center=self.new_game_btn_rect.center))
        
        home_sz = int(60 * self.scale)
        self.home_btn_rect = pygame.Rect(panel_rect.right - home_sz - 10, panel_rect.top - home_sz // 2, home_sz, home_sz)
        pygame.draw.rect(self.screen, self.TILE_COLOR, self.home_btn_rect, border_radius=12)
        self.draw_home_icon(self.screen, self.home_btn_rect.center, int(14 * self.scale), self.TEXT_COLOR)

    def draw_settings(self):
        self.screen.fill(self.BG_COLOR)
        
        panel_w = int(500 * self.scale)
        panel_h = int(580 * self.scale)
        panel_x = (self.WIDTH - panel_w) // 2
        panel_y = (self.HEIGHT - panel_h) // 2
        panel_rect = pygame.Rect(panel_x, panel_y, panel_w, panel_h)
        
        pygame.draw.rect(self.screen, self.PANEL_COLOR, panel_rect, border_radius=16)
        
        title = self.font_h2.render("Settings", True, self.TEXT_COLOR)
        self.screen.blit(title, title.get_rect(center=(self.WIDTH // 2, panel_y + int(40 * self.scale))))

        content_x = panel_x + int(40 * self.scale)
        y_offset = panel_y + int(110 * self.scale)
        y_step = int(65 * self.scale)
        btn_sz = int(35 * self.scale)

        # Rows
        row_txt = self.font_body.render(f"Rows:  {self.setting_rows}", True, self.TEXT_COLOR)
        self.screen.blit(row_txt, (content_x, y_offset))
        self.row_minus_rect = pygame.Rect(panel_rect.right - int(120 * self.scale), y_offset, btn_sz, btn_sz)
        self.row_plus_rect = pygame.Rect(panel_rect.right - int(70 * self.scale), y_offset, btn_sz, btn_sz)
        y_offset += y_step
        
        # Cols
        col_txt = self.font_body.render(f"Columns:  {self.setting_cols}", True, self.TEXT_COLOR)
        self.screen.blit(col_txt, (content_x, y_offset))
        self.col_minus_rect = pygame.Rect(panel_rect.right - int(120 * self.scale), y_offset, btn_sz, btn_sz)
        self.col_plus_rect = pygame.Rect(panel_rect.right - int(70 * self.scale), y_offset, btn_sz, btn_sz)
        y_offset += y_step

        # Volume
        vol_txt = self.font_body.render(f"Volume: {int(self.volume * 100)}%", True, self.TEXT_COLOR)
        self.screen.blit(vol_txt, (content_x, y_offset))
        
        slider_w = int(180 * self.scale)
        slider_h = max(6, int(8 * self.scale))
        slider_x = panel_rect.right - slider_w - int(40 * self.scale)
        slider_y = y_offset + int(12 * self.scale)
        
        self.slider_track_rect = pygame.Rect(slider_x, slider_y, slider_w, slider_h)
        pygame.draw.rect(self.screen, self.TILE_COLOR, self.slider_track_rect, border_radius=4)
        
        fill_w = int(slider_w * self.volume)
        if fill_w > 0:
            pygame.draw.rect(self.screen, self.BTN_COLOR, pygame.Rect(slider_x, slider_y, fill_w, slider_h), border_radius=4)
            
        knob_cx = slider_x + fill_w
        knob_cy = slider_y + slider_h // 2
        knob_r = max(8, int(12 * self.scale))
        self.slider_knob_rect = pygame.Rect(knob_cx - knob_r, knob_cy - knob_r, knob_r * 2, knob_r * 2)
        pygame.draw.circle(self.screen, self.TEXT_COLOR, (knob_cx, knob_cy), knob_r)
        
        y_offset += y_step
        
        # Theme toggle
        theme_lbl = self.font_body.render("Theme:", True, self.TEXT_COLOR)
        self.screen.blit(theme_lbl, (content_x, y_offset))
        theme_w = int(180 * self.scale)
        theme_h = int(40 * self.scale)
        self.settings_theme_btn_rect = pygame.Rect(panel_rect.right - theme_w - int(40 * self.scale), y_offset - int(5 * self.scale), theme_w, theme_h)
        pygame.draw.rect(self.screen, self.TILE_COLOR, self.settings_theme_btn_rect, border_radius=8)
        theme_val = self.font_body.render("Dark Mode" if self.is_dark_mode else "Light Mode", True, self.TEXT_COLOR)
        self.screen.blit(theme_val, theme_val.get_rect(center=self.settings_theme_btn_rect.center))
        
        y_offset += int(80 * self.scale)

        # Buttons -, + Drawing
        for rect, sym in [(self.row_minus_rect, "-"), (self.row_plus_rect, "+"), (self.col_minus_rect, "-"), (self.col_plus_rect, "+")]:
            pygame.draw.rect(self.screen, self.TILE_COLOR, rect, border_radius=8)
            sym_txt = self.font_body.render(sym, True, self.TEXT_COLOR)
            self.screen.blit(sym_txt, sym_txt.get_rect(center=rect.center))

        # Bottom Buttons
        btn_w = panel_w - int(80 * self.scale)
        btn_h = int(50 * self.scale)
        
        self.apply_btn_rect = pygame.Rect(content_x, y_offset, btn_w, btn_h)
        pygame.draw.rect(self.screen, self.BTN_COLOR, self.apply_btn_rect, border_radius=12)
        apply_txt = self.font_body.render("Apply & New Game", True, (30, 30, 46))
        self.screen.blit(apply_txt, apply_txt.get_rect(center=self.apply_btn_rect.center))
        
        y_offset += btn_h + int(12 * self.scale)
        
        self.back_btn_rect = pygame.Rect(content_x, y_offset, btn_w // 2 - int(6 * self.scale), btn_h)
        pygame.draw.rect(self.screen, self.TILE_COLOR, self.back_btn_rect, border_radius=12)
        back_text = "Menu" if self.previous_state == "MENU" else "Game"
        back_txt = self.font_body.render(f"Back to {back_text}", True, self.TEXT_COLOR)
        self.screen.blit(back_txt, back_txt.get_rect(center=self.back_btn_rect.center))
        
        self.settings_exit_btn_rect = pygame.Rect(content_x + btn_w // 2 + int(6 * self.scale), y_offset, btn_w // 2 - int(6 * self.scale), btn_h)
        pygame.draw.rect(self.screen, self.WARN_COLOR, self.settings_exit_btn_rect, border_radius=12)
        exit_txt = self.font_body.render("Exit Game", True, (30, 30, 46))
        self.screen.blit(exit_txt, exit_txt.get_rect(center=self.settings_exit_btn_rect.center))

    def draw_left_sidebar(self):
        tab_w = int(45 * self.scale)
        tab_h = int(120 * self.scale)
        tab_y = (self.HEIGHT - tab_h) // 2

        if self.show_sidebar:
            panel_rect = pygame.Rect(0, 0, self.sidebar_w, self.HEIGHT)
            s = pygame.Surface((self.sidebar_w, self.HEIGHT))
            s.set_alpha(245)
            s.fill(self.PANEL_COLOR)
            self.screen.blit(s, (0, 0))
            pygame.draw.line(self.screen, self.TILE_COLOR, (self.sidebar_w, 0), (self.sidebar_w, self.HEIGHT), max(2, int(3 * self.scale)))

            title = self.font_body.render("Found Words", True, self.TEXT_COLOR)
            self.screen.blit(title, (int(20 * self.scale), int(30 * self.scale)))
            pygame.draw.line(self.screen, self.TILE_COLOR, (int(20 * self.scale), int(65 * self.scale)), (self.sidebar_w - int(20 * self.scale), int(65 * self.scale)), 2)

            start_y = int(80 * self.scale) - self.sidebar_scroll
            found_list = sorted(list(self.found_words))
            y_spacing = int(35 * self.scale)
            
            max_scroll = max(0, len(found_list) * y_spacing - (self.HEIGHT - int(100 * self.scale)))
            if self.sidebar_scroll > max_scroll:
                self.sidebar_scroll = max_scroll

            for i, word in enumerate(found_list):
                y_pos = start_y + i * y_spacing
                if int(65 * self.scale) < y_pos < self.HEIGHT:
                    word_surf = self.font_list.render(word.capitalize(), True, self.TEXT_COLOR)
                    self.screen.blit(word_surf, (int(20 * self.scale), y_pos))

            self.sidebar_tab_rect = pygame.Rect(self.sidebar_w, tab_y, tab_w, tab_h)
            arrow_text = "<"
        else:
            self.sidebar_tab_rect = pygame.Rect(0, tab_y, tab_w, tab_h)
            arrow_text = ">"

        pygame.draw.rect(self.screen, self.TILE_COLOR, self.sidebar_tab_rect, border_bottom_right_radius=12, border_top_right_radius=12)
        
        arr_surf = self.font_btn.render(arrow_text, True, self.TEXT_COLOR)
        self.screen.blit(arr_surf, arr_surf.get_rect(center=self.sidebar_tab_rect.center))

    def draw_board(self):
        if self.state == "MENU":
            self.draw_menu()
            return
        elif self.state == "SETTINGS":
            self.draw_settings()
            return
        elif self.state == "WIN":
            self.draw_end_screen("You Win!", self.FOUND_COLOR)
            return
        elif self.state == "LOSE":
            self.draw_end_screen("Time's Up!", self.WARN_COLOR)
            return

        self.screen.fill(self.BG_COLOR)

        margin_x = int(40 * self.scale)
        margin_y = int(150 * self.scale)
        
        calc_w = self.WIDTH - (margin_x * 2)
        if self.show_sidebar:
            calc_w -= self.sidebar_w
            
        avail_h = self.HEIGHT - margin_y - int(100 * self.scale)
        
        temp_max_w = calc_w // self.board_logic.cols if self.board_logic.cols > 0 else 10
        self.padding = max(int(8 * self.scale), int(temp_max_w * 0.15))

        if self.board_logic.cols > 0 and self.board_logic.rows > 0:
            max_tile_w = (calc_w - (self.board_logic.cols - 1) * self.padding) // self.board_logic.cols
            max_tile_h = (avail_h - (self.board_logic.rows - 1) * self.padding) // self.board_logic.rows
            self.tile_size = max(int(10 * self.scale), min(max_tile_w, max_tile_h))

        font_size = max(int(12 * self.scale), int(self.tile_size * 0.5))
        dynamic_font = pygame.font.SysFont("arial", font_size, bold=True)

        total_grid_w = self.board_logic.cols * self.tile_size + (self.board_logic.cols - 1) * self.padding
        total_grid_h = self.board_logic.rows * self.tile_size + (self.board_logic.rows - 1) * self.padding
        
        if self.show_sidebar:
            self.start_x = self.sidebar_w + (self.WIDTH - self.sidebar_w - total_grid_w) // 2
        else:
            self.start_x = (self.WIDTH - total_grid_w) // 2
            
        self.start_y = margin_y + (avail_h - total_grid_h) // 2

        btn_sz = int(45 * self.scale)
        btn_base_x = self.WIDTH - btn_sz - int(20 * self.scale)

        self.theme_btn_rect = pygame.Rect(btn_base_x, int(20 * self.scale), btn_sz, btn_sz)
        pygame.draw.rect(self.screen, self.CARD_BG, self.theme_btn_rect, border_radius=10)
        self.draw_theme_icon(self.screen, self.theme_btn_rect.center, int(12 * self.scale), self.ICON_COLOR)

        self.settings_btn_rect = pygame.Rect(btn_base_x - btn_sz - int(15 * self.scale), int(20 * self.scale), btn_sz, btn_sz)
        pygame.draw.rect(self.screen, self.CARD_BG, self.settings_btn_rect, border_radius=10)
        self.draw_gear_icon(self.screen, self.settings_btn_rect.center, int(12 * self.scale), self.ICON_COLOR)

        self.home_btn_rect = pygame.Rect(btn_base_x - (btn_sz * 2) - int(30 * self.scale), int(20 * self.scale), btn_sz, btn_sz)
        pygame.draw.rect(self.screen, self.CARD_BG, self.home_btn_rect, border_radius=10)
        self.draw_home_icon(self.screen, self.home_btn_rect.center, int(11 * self.scale), self.ICON_COLOR)

        current_word = "".join(self.board_logic.board[r][c] for r, c in self.selected_path).upper()
        
        display_time = max(0, int(self.time_left))
        mins = display_time // 60
        secs = display_time % 60
        
        word_card_w = max(int(240 * self.scale), total_grid_w)
        word_card_rect = pygame.Rect(self.start_x + (total_grid_w - word_card_w) // 2, int(20 * self.scale), word_card_w, int(60 * self.scale))
        pygame.draw.rect(self.screen, self.CARD_BG, word_card_rect, border_radius=12)
        word_surface = self.font_h2.render(f"Word:  {current_word}", True, self.TEXT_COLOR)
        self.screen.blit(word_surface, word_surface.get_rect(center=word_card_rect.center))

        stats_y = int(90 * self.scale)
        card_gap = int(12 * self.scale)
        card_w = (total_grid_w - (card_gap * 2)) // 3
        if card_w < int(100 * self.scale):
            card_w = int(100 * self.scale)
            
        score_card = pygame.Rect(self.start_x, stats_y, card_w, int(50 * self.scale))
        target_card = pygame.Rect(self.start_x + card_w + card_gap, stats_y, card_w, int(50 * self.scale))
        time_card = pygame.Rect(self.start_x + (card_w + card_gap) * 2, stats_y, card_w, int(50 * self.scale))

        for card in [score_card, target_card, time_card]:
            pygame.draw.rect(self.screen, self.CARD_BG, card, border_radius=10)

        score_txt = self.font_body.render(f"Score: {self.score}", True, self.TEXT_COLOR)
        target_txt = self.font_body.render(f"Words: {len(self.found_words)}/{self.target_words}", True, self.FOUND_COLOR)
        
        time_color = self.WARN_COLOR if display_time <= 10 else self.TEXT_COLOR
        time_txt = self.font_body.render(f"Time: {mins:02d}:{secs:02d}", True, time_color)

        self.screen.blit(score_txt, score_txt.get_rect(center=score_card.center))
        self.screen.blit(target_txt, target_txt.get_rect(center=target_card.center))
        self.screen.blit(time_txt, time_txt.get_rect(center=time_card.center))

        for r in range(self.board_logic.rows):
            for c in range(self.board_logic.cols):
                x = self.start_x + c * (self.tile_size + self.padding)
                y = self.start_y + r * (self.tile_size + self.padding)
                rect = pygame.Rect(x, y, self.tile_size, self.tile_size)

                if (r, c) in self.hint_path:
                    glow_rect = rect.inflate(max(2, int(8 * self.scale)), max(2, int(8 * self.scale)))
                    pygame.draw.rect(self.screen, self.FOUND_COLOR, glow_rect, border_radius=max(6, self.tile_size // 5))

                tile_bg = self.SELECTED_COLOR if (r, c) in self.selected_path else self.TILE_COLOR
                pygame.draw.rect(self.screen, tile_bg, rect, border_radius=max(4, self.tile_size // 6))

                char = self.board_logic.board[r][c].upper()
                text_color = (255, 255, 255) if (r, c) in self.selected_path else self.TEXT_COLOR
                text_surface = dynamic_font.render(char, True, text_color)
                text_rect = text_surface.get_rect(center=rect.center)
                self.screen.blit(text_surface, text_rect)

        hint_y = self.start_y + total_grid_h + int(25 * self.scale)
        self.hint_btn_rect = pygame.Rect(self.start_x, hint_y, int(150 * self.scale), int(50 * self.scale))
        pygame.draw.rect(self.screen, self.TILE_COLOR, self.hint_btn_rect, border_radius=8)
        
        hint_txt = self.font_body.render(f"Hint ({self.hints_remaining})", True, self.TEXT_COLOR)
        self.screen.blit(hint_txt, hint_txt.get_rect(center=self.hint_btn_rect.center))

        if len(self.selected_path) > 1:
            points = []
            for r, c in self.selected_path:
                cx = self.start_x + c * (self.tile_size + self.padding) + self.tile_size // 2
                cy = self.start_y + r * (self.tile_size + self.padding) + self.tile_size // 2
                points.append((cx, cy))
            pygame.draw.lines(self.screen, self.LINE_COLOR, False, points, max(3, self.tile_size // 8))

        self.draw_left_sidebar()

        # Draw pop-up animations (over everything else)
        current_time = pygame.time.get_ticks()
        for popup in self.popups[:]:
            elapsed = current_time - popup["start"]
            if elapsed > popup["duration"]:
                self.popups.remove(popup)
                continue

            # Calculate progress 0 to 1
            progress = elapsed / popup["duration"]
            
            # Float upwards
            current_y = popup["y"] - (progress * int(60 * self.scale))
            
            # Fade out alpha
            alpha = max(0, min(255, int(255 * (1 - progress))))

            # Text Surface
            txt_surf = self.font_body.render(popup["text"], True, self.FOUND_COLOR)
            txt_surf.set_alpha(alpha)
            txt_rect = txt_surf.get_rect(center=(popup["x"], current_y))

            # Background Surface for contrast
            bg_rect = txt_rect.inflate(int(20 * self.scale), int(10 * self.scale))
            bg_surf = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            pygame.draw.rect(bg_surf, (*self.POPUP_BG, alpha), bg_surf.get_rect(), border_radius=8)
            pygame.draw.rect(bg_surf, (*self.FOUND_COLOR, alpha), bg_surf.get_rect(), width=max(1, int(2 * self.scale)), border_radius=8)

            self.screen.blit(bg_surf, bg_rect)
            self.screen.blit(txt_surf, txt_rect)


    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            
            current_time = pygame.time.get_ticks()
            dt = (current_time - self.last_time) / 1000.0
            self.last_time = current_time

            if self.state == "GAME":
                self.time_left -= dt
                if len(self.found_words) >= self.target_words:
                    self.state = "WIN"
                    self.has_saved_game = False
                    self.save_game()
                elif self.time_left <= 0:
                    self.state = "LOSE"
                    self.has_saved_game = False
                    self.save_game()

            running = self.handle_events()
            self.draw_board()
            pygame.display.flip()
            
        pygame.quit()


def resource_path(relative_path):
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    trie = Trie()
    try:
        with open(resource_path("enable1.txt"), "r") as f:
            for word in f.read().splitlines():
                trie.add(word.strip().lower())
    except:
        pass
        
    board = Board(rows=5, cols=5, trie=trie, min_words=4)
    ui = GameUI(board, trie)
    ui.run()