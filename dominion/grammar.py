from abc import abstractmethod, ABCMeta


class Word(metaclass=ABCMeta):
    """
    Mixin class for objects that have grammatical class properties.
    """
    @classmethod
    @property
    @abstractmethod
    def singular(cls) -> str:
        pass

    @classmethod
    @property
    @abstractmethod
    def pluralized(cls) -> str:
        pass


# Grammatical helper functions


def a(word):
    """
    Decide whether or not to use "a " or "an " before a word.
    """
    word = str(word)
    if word[0].lower() in ["a", "e", "i", "o", "u"]:
        return f"an {word}"
    else:
        return f"a {word}"


def s(num, word: str | Word):
    """
    Pluralize a word (or a Word object (or a Type inheriting from Word)) based on a number.
    """
    num = int(num)
    if type(word) is str:
        word = str(word)
        if abs(num) == 1:
            return f"{num} {word}"
        else:
            return f"{num} {word}s"
    elif isinstance(word, Word) or issubclass(word, Word):
        if abs(num) == 1:
            return f"{num} {word.singular}"
        else:
            return f"{num} {word.pluralized}"
