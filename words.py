'''
Author: Abrorjon Asralov
Description: This is a program that opens a file with tons of english
             words and after processing those words those are written
             every new line, it gets all those possible english words
             and returns a collection with those words. In further 
             steps the "words" collection is used to complete a "word
             search" program.
'''
import string


def readFile() -> None:
    '''
    This is a function that reads a file "enable1.txt that is retrived from
    https://norvig.com/ngrams/enable1.txt and after processing, it creates
    a collection of words those are kept in a python list that is named
    wordCollection. It is relatively easier to process the file since all
    words are written separetely each line. And afterall, it returns that
    wordCollection.
    '''
    wordCollection = []
    with open("enable1.txt") as file:
        content = file.readlines()
    for word in content:
        wordCollection += [word.strip("\n")]
    return wordCollection

# "words" is used in another file named wordSearch.py
words = readFile()
# "letters" is also used in the same file to create a grid with
# all randomly choosen letters.
letters = list(string.ascii_uppercase)
