"""
Author: Abrorjon Asralov
Description: This is a program that is sort of word search game, but in the
             text version. It gets several user inputs, such as does user want
             to even start a game, then what should be a grid size, then it
             prints randomly generated grid of NxN size (the range is between
             5 and 10) and repeatadily asks for user's input that should be a
             word that is found either horizontally, vertically or diagonally.
             At the same time it shows how many words remain after each guess.
             If a word has been already guessed, it lets know that user already
             guessed that word. If the word really exists, it says that user
             found a word, otherwise lets user know that a guessed word does
             exist
"""
from words import letters  # a list with all possible upper case letters.
from words import words  # a list with all possible words that
from welcoming import welcome_text  # that is a welcoming text that prints at
                                    # the begining of the running this program
import sys
import random


class Board:
    """
    Description:
    This is a class instance called Board, it has all needed feature to start
    an individual board with randomly chosen letters. It has several features
    such as the board itself that is being represented as a 2d list with rows
    and columns, a size NxN that is chosen by a user (range is 5-10), a set of
    all possible words in that board, a set of found words (if user finds a
    word, then the word is added to this set, then a set of the guessed words.
    So whenever user enters any characters or words, this set is being modified
    and in the future trials user is being notified about already guessed words
    Attributes: self._board is a 2d list kind of a grid with randomly chosen
                upper case letters from an english alphabet.
                self._size is an integer that is a size for our grid, if the
                size N, then the size of the grid is NxN.
                self._possible is a set that holds all possible english words
                from the grid. Those words might be found, horizontally,
                vertically and diagonally.
                self._found is also a set of words, but this time for correcly
                guessed words, so number of possible words reduces and user is
                closer to win.
                self._guessed is a set as well, however, that is for all words
                those are being guessed by a user. It notifies user if they
                already guessed that word.
                self._helpTickets is a list of 3 elements which stands for
                user's 3 chances to find a random word to continue the game.
    Methods: __init__ is a special method to initialize all aforementioned
             attributes.
             size is a getter method that returns a int that is a size for the
             board.
             generateRandomCrossword is a setter method that creates that
             random grid with those randomly chosen upper case letters.
    """

    def __init__(self, size) -> None:
        '''
        This is a special method to initialize attributes mentioned above.
        There are all for a word search game, sets of found, guessed, and
        all possible words from created board, and other than that the board
        itself is a 2d list that is created using list comprehension, and
        lastly an attribute that is a python list that keeps three elements
        and those are like a game changer, it helps users not to stuck in one
        place and keep going. Those I would call as a help tickets and those
        are 3 in count.
        '''
        self._board = [["-"] * size for i in range(size)]
        self._size = size
        self._possible = set()
        self._found = set()
        self._guessed = set()
        self._helpTickets = ["T1", "T2", "T3"]

    def size(self) -> int:
        '''
        This is a getter method that returns a size of the board, if the board
        is NxN size, then when it is called, it returns an integer N
        '''
        return self._size

    def board(self) -> list[list]:
        '''
        This is a getter method that returns a 2d list that we can call as a
        grid of NxN size, and returns that 2d python list.
        '''
        return self._board

    def generateRandomCrossword(self) -> None:
        '''
        This is a setter method that creates a grid with random letters, and
        whenever it is called, it will create a new grid. If user finds all 
        words, then it means user wins the game, then will be asked for 
        another randomly generated grid with letters.
        '''
        L = len(letters)
        B = len(self.board())
        self._board = [
            [letters[random.randint(0, L - 1)] for i in range(B)] for j in range(B)
        ]

    def findHorizontalWords(self) -> set[str]:
        '''
        This is a method that finds all possible english words those are
        located in the grid horizontally back and forth. It is being kept
        in a set in order to avoid duplicates. Then when the method is called
        it returns that set with all possible horizontal english words with 
        3 and more length.
        '''
        wordSet = set()
        for rows in self._board:
            for i in range(len(rows)):
                for j in range(len(rows)):
                    # getting a horizontal word from Left to Right
                    horWordLR = "".join(rows[i : j + 1])
                    # getting a horizontal word from right to left
                    horWordRL = horWordLR[::-1]
                    if horWordLR.lower() in words and len(horWordLR.lower()) > 2:
                        wordSet.add(horWordLR.lower())
                    if horWordRL.lower() in words and len(horWordRL.lower()) > 2:
                        wordSet.add(horWordRL.lower())
        return wordSet

    def findVerticalWords(self) -> set[str]:
        '''
        This is a method that finds all possible english words those are
        located in the grid vertically back and forth. It is being kept
        in a set in order to avoid duplicates. Then when the method is called
        it returns that set with all possible vertical english words with 
        3 and more length.
        '''
        wordSet = set()
        verWordTB = ""
        # vertical search Top=>Bottom
        for i in range(len(self._board)):
            for k in range(len(self._board)):
                for j in range(len(self._board) - k):
                    verWordTB += self._board[j + k][i]
                    verWordBT = verWordTB[::-1]
                    if verWordTB.lower() in words and len(verWordTB.lower()) > 2:
                        wordSet.add(verWordTB.lower())
                    if verWordBT.lower() in words and len(verWordBT.lower()) > 2:
                        wordSet.add(verWordBT.lower())
                verWordTB = ""
        return wordSet

    def findDioganalWords(self) -> set[str]:
        '''
        Pretty much the same scheme, except, in this case we are looking for
        words those are located diagonally, processing them. Then after all,
        getting into set in order to avoid repeating words, and then when this
        method is called, it returns a set with all possible diagonal words.
        '''
        wordSet = set()
        w_c1 = ""
        w_c2 = ""
        for i in range(len(self._board)):
            for k in range(len(self._board) - i):
                for j in range(len(self._board) - k - i):
                    w_c1 += self._board[j + k][j + k + i]
                    w_c2 += self._board[j + k + i][j + k]
                    if w_c1.lower() in words and len(w_c1.lower()) > 2:
                        wordSet.add(w_c1.lower())
                    if w_c2.lower() in words and len(w_c2.lower()) > 2:
                        wordSet.add(w_c2.lower())
                # updating the variables in order to get new words in the
                # next iteration.
                w_c1 = ""
                w_c2 = ""
        return wordSet

    def findPossibleWords(self) -> set[str]:
        '''
        This is a method that is used for  a set connecting. It gets three sets
        of possible horizontal, vertical and diagonal words and after connecting
        them by transforming them into lists (since we cannot modify sets)
        and after all we get one big list of all possible words. Then we
        again convert it to be a set to avoid repeating words.
        '''
        horWords = self.findHorizontalWords()
        verWords = self.findVerticalWords()
        diagWords = self.findDioganalWords()
        possibleWords = set(list(horWords) + list(verWords) + list(diagWords))
        self._possible = possibleWords
        numberOfPossibilities = len(possibleWords)
        # in the case if the word search unsuccesful because of the randomly
        # generated grid, then it exits a system, so user can rerun the 
        # program
        if numberOfPossibilities == 0:
            print("Oops there are not enough possible words")
            print("Please try again generating a crossword later.")
            print("System exits...")
            sys.exit()
        else: # otherwise, it returns the main set of all english words in
            # the grid.
            return possibleWords

    def getUserWords(self) -> None:
        '''
        This is a special method that is used for getting user's input, so
        whatever user enters, it affects to outcomes of the game. In a case
        if user want to leave the game, he should enter a letter s, the reason
        why it is not a stop word, because there is a possibility that in a
        grid we might have a word stop, so when user tried to enter it, it 
        would simply stop the game. The same thing with H command for getting 
        a help ticket, if user were to enter help command, then it would not
        simply allow user to get a help since program would think that user
        would try to enter a word help. 
        '''
        while len(self._possible) != len(self._found):
            userWord = input(
                f"""Enter a word from a crossword that you found
If you want to quit a game, enter "S" command
If you want to use a help ticket, enter command "H"
You have {len(self._helpTickets)} help tickets to use\n"""
            )
            if (
                userWord.lower() in self._possible
                and userWord.lower() not in self._guessed
            ):
                self._found.add(userWord.lower())
                self._guessed.add(userWord.lower())
                print("Yay! You found a word")
                remaining = len(self._possible) - len(self._guessed)
                print(f"You have {remaining} words left to find!")
            elif (
                userWord.lower() in self._possible and userWord.lower() in self._guessed
            ):
                print("Oops! You have already guessed that word")
            elif (userWord.lower() == "s"):
                print("Words you did not guess:")
                for word in self._possible:
                    print(word)
                sys.exit()
            elif (userWord.lower() == 'h'):
                if self._helpTickets != [] and self._possible != []:
                    self._helpTickets.pop() # poping the last ticket that is being
                    # used by a user, so in the future they have less remaining
                    # tickets to use.
                    randomWordIndex = random.randint(0, len(self._possible)-1)
                    randomWord = list(self._possible)[randomWordIndex]
                    print(f'You used your ticket, you have {len(self._helpTickets)} tickets remaining')
                    print(randomWord)
                else:
                    print("Oops it seems to be that you already you used all your help tickets.")
            else:
                print("Please enter a valid word from a crossword!")

    def __str__(self) -> str:
        '''
        This is a special method that represents object when it is being
        printed, in our case with this game, it should print a grid with
        some random letters in it of the size that user chooses.
        '''
        res = ""
        for line in self.board():
            temp = ''
            for element in line:
                temp += element + '    '
            res += temp + "\n"
        return res


def startGame() -> None:
    # before going to loop, it prints a welcoming message for the user.
    print(welcome_text)
    while True:
        userWants = input(
            """Would you like to generate a random crossword?
If yes, enter Y, othewise enter N to exit the program.\n"""
        )
        # if user does not put y, then that means user does not want to 
        # even start a game, so program executes and it is done.
        if not userWants.lower() == "y":
            sys.exit()
        try:
            size = int(input("Please, enter a number between 5-10\n"))
            if not size in range(5, 11):
                print("Please enter a valid nunber between 5-10\nSystem exits...")
                sys.exit()
            board = Board(size)
            board.generateRandomCrossword()
            board.findPossibleWords()
            print("_" * board._size * 5)
            print(f"You have {len(board._possible)} word to find")
            print("_" * board._size * 5)
            print(board)
            board.getUserWords()
        except ValueError: # user needs to enter a valid number between 5 and
            # including 10. In a case when user enters a letter or some other
            # symbol, then program executes.
            print(
                """Oops, please enter a valid number between 5-10 in order
to create a valid grid for a randomly generated crossword."""
            )
            sys.exit()


if __name__ == "__main__":
    startGame()
