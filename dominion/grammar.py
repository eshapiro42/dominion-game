# Grammatical helper functions

def a(word):
    word = str(word)
    if word[0].lower() in ['a', 'e', 'i', 'o', 'u']:
        return f'an {word}'
    else:
        return f'a {word}'

def s(num, word):
    num = int(num)
    word = str(word)
    if abs(num) == 1:
        return f'{num} {word}'
    else:
        return f'{num} {word}s'
