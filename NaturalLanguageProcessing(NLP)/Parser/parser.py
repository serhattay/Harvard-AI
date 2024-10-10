import nltk
import sys

TERMINALS = """
Adj -> "country" | "dreadful" | "enigmatical" | "little" | "moist" | "red"
Adv -> "down" | "here" | "never"
Conj -> "and" | "until"
Det -> "a" | "an" | "his" | "my" | "the"
N -> "armchair" | "companion" | "day" | "door" | "hand" | "he" | "himself"
N -> "holmes" | "home" | "i" | "mess" | "paint" | "palm" | "pipe" | "she"
N -> "smile" | "thursday" | "walk" | "we" | "word"
P -> "at" | "before" | "in" | "of" | "on" | "to"
V -> "arrived" | "came" | "chuckled" | "had" | "lit" | "said" | "sat"
V -> "smiled" | "tell" | "were"
"""

NONTERMINALS = """
S -> NP VP
NP -> N
NP -> Det N
NP -> Det Adj N
NP -> Adj N
NP -> N
NP -> NP PP
VP -> V
VP -> V NP
VP -> V NP PP
VP -> V PP
VP -> V Adv
VP -> V NP Adv
VP -> V S
PP -> P NP
AdjP -> Adj
AdjP -> Adv Adj
AdvP -> Adv
AdvP -> Adv Adv
NP -> NP Conj NP
VP -> VP Conj VP

"""

grammar = nltk.CFG.fromstring(NONTERMINALS + TERMINALS)
parser = nltk.ChartParser(grammar)


def main():

    # If filename specified, read sentence from file
    if len(sys.argv) == 2:
        with open(sys.argv[1]) as f:
            s = f.read()

    # Otherwise, get sentence as input
    else:
        s = input("Sentence: ")

    # Convert input into list of words
    s = preprocess(s)

    # Attempt to parse sentence
    try:
        trees = list(parser.parse(s))
    except ValueError as e:
        print(e)
        return
    if not trees:
        print("Could not parse sentence.")
        return

    # Print each tree with noun phrase chunks
    for tree in trees:
        tree.pretty_print()

        print("Noun Phrase Chunks")
        for np in np_chunk(tree):
            print(" ".join(np.flatten()))


def preprocess(sentence):
    """
    Convert `sentence` to a list of its words.
    Pre-process sentence by converting all characters to lowercase
    and removing any word that does not contain at least one alphabetic
    character.
    """
    list_of_words = nltk.word_tokenize(sentence)

    list_of_words = [word.lower() for word in list_of_words]

    for word in list_of_words:
        if not any(char.isalpha() for char in word):
            list_of_words.remove(word)

    return list_of_words


def np_chunk(tree):
    """
    Return a list of all noun phrase chunks in the sentence tree.
    A noun phrase chunk is defined as any subtree of the sentence
    whose label is "NP" that does not itself contain any other
    noun phrases as subtrees.
    """
    np_list = []

    for subtree in tree.subtrees():
        if subtree.label() == "NP":
            if all(sub_subtree.label() != "NP" for sub_subtree in subtree.subtrees() if sub_subtree != subtree):
                np_list.append(subtree)

    return np_list


if __name__ == "__main__":
    main()
