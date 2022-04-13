# Grammatical helper functions

def a(word):
    """
    Decide whether or not to use "a " or "an " before a word.
    """
    word = str(word)
    if word[0].lower() in ['a', 'e', 'i', 'o', 'u']:
        return f'an {word}'
    else:
        return f'a {word}'

def s(num, word):
    """
    Pluralize a word based on a number.
    """
    num = int(num)
    word = str(word)
    if abs(num) == 1:
        return f'{num} {word}'
    else:
        return f'{num} {word}s'
