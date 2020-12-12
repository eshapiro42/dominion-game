from abc import ABCMeta, abstractmethod


class Interaction(metaclass=ABCMeta):
    def __init__(self, player, socketio=None, sid=None):
        self.player = player
        self.socketio = socketio
        self.sid = sid

    def start(self):
        self.hand = self.player.hand
        self.discard_pile = self.player.discard_pile
        self.deck = self.player.deck
        self.supply = self.player.game.supply
        self.game = self.player.game
        self.room = self.player.game.room

    @abstractmethod
    def send(self, message):
        pass

    @abstractmethod
    def display_supply(self):
        pass

    @abstractmethod
    def display_hand(self):
        pass

    @abstractmethod
    def display_discard_pile(self):
        pass

    @abstractmethod
    def choose_card_from_hand(self, prompt, force):
        pass

    @abstractmethod
    def choose_specific_card_class_from_hand(self, prompt, force, card_class):
        pass

    @abstractmethod
    def choose_specific_card_type_from_hand(self, prompt, card_type):
        pass

    @abstractmethod
    def choose_card_from_discard_pile(self, prompt, force):
        pass

    @abstractmethod
    def choose_card_class_from_supply(self, prompt, max_cost, force, invalid_card_classes=None, exact_cost=False):
        pass

    @abstractmethod
    def choose_specific_card_type_from_supply(self, prompt, max_cost, card_type, force):
        pass

    @abstractmethod
    def choose_specific_card_type_from_trash(self, prompt, max_cost, card_type, force):
        pass

    @abstractmethod
    def choose_yes_or_no(self, prompt):
        pass

    @abstractmethod
    def choose_from_range(self, prompt, minimum, maximum, force):
        pass

    @abstractmethod
    def choose_from_options(self, prompt, options, force):
        pass

    @abstractmethod
    def new_turn(self):
        pass