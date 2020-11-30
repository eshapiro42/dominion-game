import cards

def test_instantiate_cards():
    for card_class in cards.BASIC_CARDS:
        card = card_class()
    for card_class in cards.KINGDOM_CARDS:
        card = card_class()