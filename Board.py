import random

class Board:
    def __init__(self, rows=5, cols=5, trie=None, min_words=3):
        self.rows = rows
        self.cols = cols
        self.trie = trie
        self.min_words = min_words
        self.board = self.validate_board()



    def init_board(self):
        letter_pool = (
                "eeeeeeeeeeeeaaaaaaaaaiiiiiiiioooooooo"
                "nnnnnnrrrrrrttttttllllssssuuuuddddgg"
                "bbccmmppffhhvvwwyykjxqz"
            )
        return [[random.choice(letter_pool) for _ in range(self.cols)] for _ in range(self.rows)]



    def validate_board(self):
        while True:
            candidate_board = self.init_board()
            found_words = self.get_all_valid_words(candidate_board)
            if len(found_words) >= self.min_words:
                self.n_words = len(found_words)
                return candidate_board



    def dfs(self, r, c, node, prefix, visited, found_words, board):
        if not (0 <= r < self.rows) or not (0 <= c < self.cols) or (r, c) in visited: 
            return
        char = board[r][c].lower()
        if char not in node.children: 
            return
        next_node =  node.children[char]
        current_word = prefix + char
        if next_node.isWord(): 
            found_words.add(current_word)
        visited.add((r, c))
        directions = [
            (-1, -1),
            (-1, 0),
            (0, -1),
            (1, 1),
            (1, 0),
            (0, 1),
            (-1, 1),
            (1, -1)
        ]

        for dr, dc in directions:
            self.dfs(r + dr, c + dc, next_node, current_word, visited, found_words, board)
        visited.remove((r, c))



    def get_all_valid_words(self, board):
        found_words = set()
        if not self.trie: return found_words

        for r in range(self.rows):
            for c in range(self.cols):
                visited = set()
                self.dfs(r, c, self.trie.root, "", visited, found_words, board)
        return found_words

