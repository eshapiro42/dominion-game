from abc import abstractmethod, ABCMeta
from enum import Enum, auto
from string import Template
from typing import Type


class WordMeta(ABCMeta):
    pass


class Word(metaclass=WordMeta):
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


def a(word: str) -> str:
    """
    Decide whether or not to use "a " or "an " before a word.

    Args:
        word: The word to decide whether or not to use "a " or "an " before.

    Returns:
        The word with "a " or "an " prepended.
    """
    word = str(word)
    if word[0].lower() in ["a", "e", "i", "o", "u"]:
        return f"an {word}"
    else:
        return f"a {word}"


def s(num: int, word: str | Word | Type[Word], print_number: bool = True) -> str:
    """
    Pluralize a word (or a Word object (or a Type inheriting from Word)) based on a number.

    Args:
        num: The number to use to decide whether or not to pluralize the word.
        word: The word to pluralize.
        print_number: Whether or not to print the number before the word. Defaults to :obj:`True`.
                      If :obj:`False`, will prepend the word with "a " or "an " when singular. 

    Returns:
        The pluralized word.
    """
    num = int(num)
    if type(word) is str:
        word = str(word)
        if abs(num) == 1:
            if print_number:
                return f"{num} {word}"
            return a(word)
        else:
            if print_number:
                return f"{num} {word}s"
            return f"{word}s"
    elif isinstance(word, Word) or issubclass(word, Word):
        if abs(num) == 1:
            if print_number:
                return f"{num} {word.singular}"
            return a(word.singular)
        else:
            if print_number:
                return f"{num} {word.pluralized}"
            return word.pluralized
    return None

def it_or_them(num: int) -> str:
    """
    Decide whether or not to use "it" or "them" based on a number.

    Args:
        num: The number to use to decide whether or not to use "it" or "them".

    Returns:
        The word "it" or "them".
    """
    if abs(num) == 1:
        return "it"
    return "them"


# Pronouns


class GrammaticalPerson(Enum):
    SECOND_PERSON = auto() # you/you/your/yours/yourself
    THIRD_PERSON = auto() # they/them/their/theirs/themselves


class PronounType(Enum):
    SUBJECT_PRONOUN = auto() # you/they
    OBJECT_PRONOUN = auto() # you/them
    POSSESSIVE_ADJECTIVE = auto() # your/their
    POSSESSIVE_PRONOUN = auto() # yours/theirs
    REFLEXIVE_PRONOUN = auto() # yourself/themselves


PRONOUN = {
    GrammaticalPerson.SECOND_PERSON: {
        PronounType.SUBJECT_PRONOUN: "you",
        PronounType.OBJECT_PRONOUN: "you",
        PronounType.POSSESSIVE_ADJECTIVE: "your",
        PronounType.POSSESSIVE_PRONOUN: "yours",
        PronounType.REFLEXIVE_PRONOUN: "yourself",
    },
    GrammaticalPerson.THIRD_PERSON: {
        PronounType.SUBJECT_PRONOUN: "they",
        PronounType.OBJECT_PRONOUN: "them",
        PronounType.POSSESSIVE_ADJECTIVE: "their",
        PronounType.POSSESSIVE_PRONOUN: "theirs",
        PronounType.REFLEXIVE_PRONOUN: "themselves",
    },
}


def format_pronouns(string_to_format: str, grammatical_person: GrammaticalPerson) -> str:
    """
    Format a string with placeholders for different pronoun types
    that will be filled in with the appropriate pronoun for that
    grammatical person.

    Placeholders correspond to the members of the :obj:`PronounType`
    enumeration.

    E.g.:

    .. highlight:: python
    .. code-block:: python
            
        string_to_format = "How are $SUBJECT_PRONOUN enjoying $POSSESSIVE_ADJECTIVE tea?"
        format_pronouns(string_to_format, GrammaticalPerson.SECOND_PERSON) = "How are you enjoying your tea?"

    Args:
        string_to_format: The string containing pronoun placeholders to be formatted.
        grammatical_person: The grammatical person.

    Returns:
        A string with all pronouns formatted.
    """
    substitutions = {pronoun_type.name: PRONOUN[grammatical_person][pronoun_type] for pronoun_type in PronounType}
    return Template(string_to_format).safe_substitute(substitutions)
    