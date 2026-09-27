
class Trie:
    def __init__(self):
        self.root = TrieNode()

    def add(self, word):
        curr = self.root

        for ch in word:
            if ch not in curr.children:
                curr.children[ch] = TrieNode(ch)
            curr = curr.children[ch]
        curr.make_word(True)

    def search(self, word):
        curr = self.root

        for ch in word:
            if ch not in curr.children: return False

            curr = curr.children[ch]
        return curr.isWord()


class TrieNode:
    def __init__(self, character=None):
        self.letter = character
        self.is_word = False
        self.children = {}


    def make_word(self, is_word): self.is_word = is_word

    def isWord(self): return self.is_word

