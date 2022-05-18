from .cards import CardType, TreasureCard, VictoryCard, CurseCard


# BASIC CARDS


class Copper(TreasureCard):
    name = 'Copper'
    _cost = 0
    types = [CardType.TREASURE]
    image_path = ''
    description = '1 $'
    value = 1

class Silver(TreasureCard):
    name = 'Silver'
    _cost = 3
    types = [CardType.TREASURE]
    image_path = ''
    description = '2 $'
    value = 2

class Gold(TreasureCard):
    name = 'Gold'
    _cost = 6
    types = [CardType.TREASURE]
    image_path = ''
    description = '3 $'
    value = 3

class Estate(VictoryCard):
    name = 'Estate'
    _cost = 2
    types = [CardType.VICTORY]
    image_path = ''
    description = '1 victory point'
    points = 1

class Duchy(VictoryCard):
    name = 'Duchy'
    pluralized = 'Duchies'
    _cost = 5
    types = [CardType.VICTORY]
    image_path = ''
    description = '3 victory points'
    points = 3

class Province(VictoryCard):
    name = 'Province'
    _cost = 8
    types = [CardType.VICTORY]
    image_path = ''
    description = '6 victory points'
    points = 6

class Curse(CurseCard):
    name = 'Curse'
    _cost = 0
    types = [CardType.CURSE]
    image_path = ''
    description = '-1 victory point'
    points = -1


BASIC_CARDS = [
    Copper,
    Silver,
    Gold,
    Estate,
    Duchy,
    Province,
    Curse
]


for card_class in BASIC_CARDS:
    card_class.expansion = "Base"
