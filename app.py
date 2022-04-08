from gevent import monkey
monkey.patch_all()

import flask_socketio
import random
import string
from collections import defaultdict
from flask import Flask, request, send_from_directory
from dominion.cards import cards, prosperity_cards
from dominion.expansions import IntrigueExpansion, ProsperityExpansion
from dominion.game import Game, GameStartedError
from dominion.interactions import BrowserInteraction, AutoInteraction


app = Flask(__name__)
app.config.from_object("config.Config")
socketio = flask_socketio.SocketIO(app, async_mode="gevent", logger=False, engineio_logger=False)


@app.route("/")
def base():
    return send_from_directory("client/public", "index.html")

@app.route("/<path:path>")
def home(path):
    return send_from_directory("client/public", path)


# Global dictionary of games, indexed by room ID
games = {}
# Global dictionary of sids, {sid: (room, data)}
sids = {}
# Global dictionary of disconnected players, indexed by room ID, {room: [username, ...], ...}
disconnected_players = defaultdict(list)
# Global dictionary of CPUs, indexed by room ID, {room: CPU_COUNT}
cpus = {}


@socketio.on('join room')
def join_room(data):
    username = data['username']
    room = data['room']
    if data['client_type'] == 'browser':
        interaction_class = BrowserInteraction
    # Add the user to the room
    flask_socketio.join_room(room)
    sid = request.sid
    sids[sid] = (room, data)
    try:
        # Add the player to the game
        game = games[room]
        game.kill_scheduled = False # Cancel erasure of the game if necessary
        game_startable_before = game.startable
        game.add_player(username, sid, interactions_class=interaction_class)
        socketio.send(f'{username} has entered room {room}.\n', room=room)
        # If the game just became startable, push an event
        game_startable_after = game.startable
        if game_startable_after != game_startable_before:
            socketio.emit('game startable', room=room)
        return True # This activates the client's joined_room() callback
    except GameStartedError:
        if username in disconnected_players[room]:
            disconnected_players[room].remove(username)
            # Find the player object and set its sid
            for player in game.players:
                if player.name == username:
                    player.sid = sid
                    socketio.send(f"{username} has rejoined game {room}.\n", room=room)
                    print(f"New sid for player {username}: {sid}")
                    # Send the events needed to get the rejoined player's UI back in the right state
                    socketio.emit("game started", to=sid)
                    socketio.emit("current player", data=game.current_turn.player.name, to=sid)
                    return True # This activates the client's joined_room() callback
        else:
            socketio.send(f'The game has already started.\n', sid=sid)
            return False
    except KeyError:
        return False

@socketio.on('create room')
def create_room(data):
    username = data['username']
    if data['client_type'] == 'browser':
        interaction_class = BrowserInteraction
    characters = string.ascii_uppercase + string.digits
    # Create a unique room ID
    room = ''.join(random.choice(characters) for i in range(4))
    while room in games:
        room = ''.join(random.choice(characters) for i in range(4))
    # Add the user to the room
    flask_socketio.join_room(room)
    sid = request.sid
    sids[sid] = (room, data)
    # Create the game object
    game = Game(socketio=socketio, room=room)
    # Add the game object to the global dictionary of games
    games[room] = game
    # Create the game's heartbeat
    game.heartbeat = HeartBeat(game)
    # Add the player to the game
    game.add_player(username, sid, interactions_class=interaction_class)
    socketio.send(f'{username} has created room {room}\n', room=room)
    return room # This activates the client's set_room() callback

@socketio.on('add cpu')
def add_cpu(data):
    room = data['room']
    # Add the CPU to the global dictionary of CPUs
    if room not in cpus:
        cpus[room] = 0
    cpus[room] += 1
    cpu_num = cpus[room]
    # Add the CPU player to the game
    game = games[room]
    game_startable_before = game.startable
    cpu_name = f'CPU {cpu_num}'
    game.add_player(cpu_name, sid=None, interactions_class=AutoInteraction)
    socketio.send(f'{cpu_name} has entered room {room}.\n', room=room)
    # If the game just became startable, push an event
    game_startable_after = game.startable
    if game_startable_after != game_startable_before:
        socketio.emit('game startable', room=room)

@socketio.on('start game')
def start_game(data):
    username = data['username']
    room = data['room']
    intrigue = data['intrigue']
    prosperity = data['prosperity']
    allow_simultaneous_reactions = data['allowSimultaneousReactions']
    distribute_cost = data['distributeCost']
    disable_attack_cards = data['disableAttacks']
    require_plus_two_action = data['requirePlusTwoAction']
    require_drawer = data['requireDrawer']
    require_buy = data['requireBuy']
    require_trashing = data['requireTrashing']
    # Send the game started event
    socketio.send(f'{username} has started game {room}.\n', room=room)
    socketio.emit('game started', room=room)
    game = games[room]
    # Add in customization options
    if intrigue:
        game.add_expansion(IntrigueExpansion)
    if prosperity:
        game.add_expansion(ProsperityExpansion)
    if allow_simultaneous_reactions:
        game.allow_simultaneous_reactions = True
    if distribute_cost:
        game.distribute_cost = True
    if disable_attack_cards:
        game.disable_attack_cards = True
    if require_plus_two_action:
        game.require_plus_two_action = True
    if require_drawer:
        game.require_drawer = True
    if require_buy:
        game.require_buy = True
    if require_trashing:
        game.require_trashing = True
    # Start the game's heartbeat
    socketio.start_background_task(game.heartbeat)
    # Start the game (nothing can happen after this)
    game.start()

@socketio.on('message')
def send_message(data):
    username = data['username']
    room = data['room']
    message = data['message']
    socketio.send(f'{username}: {message}\n', room=room)

@socketio.on('player sent message')
def send_message(data):
    username = data['username']
    room = data['room']
    message = data['message']
    socketio.emit("player message", f'{username}: {message}\n', room=room)

@socketio.on("disconnect")
def disconnect():
    try:
        sid = request.sid
        room, data = sids[sid]
        game = games[room]
        username = data['username']
        disconnected_players[room].append(username)
        sids.pop(sid, None)
        flask_socketio.leave_room(room)
        socketio.send(f'{username} has left room {room}.\n', room=room)
        # If there are no human players left, erase the game after a short delay
        human_players = [player for player in game.players if not isinstance(player.interactions, AutoInteraction)]
        print(f"human_players: {human_players}")
        print(f"disconnected_players: {disconnected_players[room]}")
        if len(disconnected_players[room]) == len(human_players):
            game.kill_scheduled = True
            socketio.sleep(30)
            if game.kill_scheduled:
                game.killed = True
                game.heartbeat.stop()
                # Erase the game from existence
                games.pop(room, None)
                disconnected_players.pop(room, None)
                cpus.pop(room, None)
                socketio.send(f'Game {room} has ended.\n', room=room)
    except KeyError:
        pass

@socketio.on("response")
def handle_response(response_data):
    # Only process responses from the player we're waiting for!!!
    # Find the player who sent the response
    try:
        room = sids[request.sid][0]
    except:
        print(f"There is no player with SID {request.sid}.")
        return
    game = games[room]
    for player in game.players:
        if player.sid == request.sid:
            break
    # Process the response
    player.interactions.response = response_data
    player.interactions.event.set()


class HeartBeat():
    def __init__(self, game):
        self.game = game
        self.run = True
        self.beats_per_second = 5 # Must be an integer
        self.message_interval = 60 # In seconds
        self.sleep_time = 1 / self.beats_per_second
        self.message_frequency = self.beats_per_second * self.message_interval

    def __call__(self):
        counter = 0
        while self.run:
            socketio.sleep(self.sleep_time)
            if counter == self.message_frequency:
                counter = 0
                print(f"<3 Game {self.game.room} heartbeat <3")
            if not self.game.started or self.game.current_turn is None:
                continue
            try:
                # Display cards in carousels
                # All players see the current player's played cards
                self.game.current_turn.player.interactions.display_played_cards()
                # Each player sees their own hand and discard, as well as the supply and trash
                for player in self.game.players:
                    if isinstance(player.interactions, BrowserInteraction):
                        player.interactions.display_hand()
                        player.interactions.display_supply()
                        player.interactions.display_discard_pile()
                        player.interactions.display_trash()
                # Display current turn info in status bar
                if hasattr(self.game, "current_turn"):
                    self.game.current_turn.display()
                # Display player info
                if hasattr(self.game, "turn_order"):
                    players_info = [player.get_info() for player in self.game.turn_order] # Get player info in turn order
                    socketio.emit(
                        "players info",
                        players_info,
                        room=self.game.room
                    )
                # Display Trade Route info
                if prosperity_cards.TradeRoute in self.game.supply.card_stacks:
                    # Find remaining Trade Route post gain hooks to see which Victory cards still have coin tokens
                    victory_card_classes = [card_class for card_class in self.game.supply.card_stacks if cards.CardType.VICTORY in card_class.types]
                    victory_card_classes_with_coin_tokens = []
                    for victory_card_class in victory_card_classes:
                        for post_gain_hook in self.game.supply.post_gain_hooks[victory_card_class]:
                            if isinstance(post_gain_hook, prosperity_cards.TradeRoute.TradeRoutePostGainHook):
                                victory_card_classes_with_coin_tokens.append(victory_card_class)
                                break
                    sorted_victory_card_classes_with_coin_tokens = sorted(victory_card_classes_with_coin_tokens, key=lambda card_class: card_class.cost)
                    victory_card_names_with_coin_tokens = [card_class.name for card_class in sorted_victory_card_classes_with_coin_tokens]
                    socketio.emit(
                        "trade route",
                        {
                            "victory_cards": victory_card_names_with_coin_tokens,
                            "tokens": self.game.supply.trade_route,
                        },
                        room=self.game.room
                    )
            except Exception as exception:
                print(exception)
            counter += 1

    def stop(self):
        self.run = False


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)