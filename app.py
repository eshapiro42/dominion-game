from gevent import monkey
monkey.patch_all()

import flask_socketio
import random
import string
from collections import defaultdict
from config import Config
from flask import Flask, Blueprint, abort, request, send_from_directory, jsonify
from flask_httpauth import HTTPBasicAuth
from typing import Any, Dict, DefaultDict, List, Tuple
from dominion.cards import ALL_KINGDOM_CARDS, ALL_KINGDOM_CARDS_BY_EXPANSION
from dominion.cards.custom_sets import CustomSet
from dominion.cards.recommended_sets import ALL_RECOMMENDED_SETS
from dominion.expansions import DominionExpansion, IntrigueExpansion, ProsperityExpansion, CornucopiaExpansion, HinterlandsExpansion, GuildsExpansion
from dominion.game import Game, GameStartedError
from dominion.interactions import BrowserInteraction, AutoInteraction


app = Flask(__name__)
app.config.from_object("config.Config")
socketio = flask_socketio.SocketIO(app, async_mode="gevent", logger=False, engineio_logger=False)
auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    return username == "admin" and password == Config.ADMIN_PASSWORD


@app.route("/")
def base():
    return send_from_directory("client/public", "index.html")

@app.route("/<path:path>")
def home(path):
    return send_from_directory("client/public", path)


# Global dictionary of games, indexed by room ID
games: Dict[str, Game] = {}
# Global dictionary of sids, {sid: (room, data)}
sids: Dict[str, Tuple[str, Any]] = {}
# Global dictionary of connected players, indexed by room ID, {room: [username, ...], ...}
connected_players: DefaultDict[str, List[str]] = defaultdict(list)
# Global dictionary of disconnected players, indexed by room ID, {room: [username, ...], ...}
disconnected_players: DefaultDict[str, List[str]] = defaultdict(list)
# Global dictionary of CPUs, indexed by room ID, {room: CPU_COUNT}
cpus: Dict[str, int] = {}
# Global variable for admin use
allow_game_creation: bool = True
# All Kingdom cards (for building custom kingdoms)
all_kingdom_cards_json = [{"expansion": expansion.name, "cards": [card_class().json for card_class in sorted(expansion_card_classes, key=lambda card_class: card_class._cost)]} for expansion, expansion_card_classes in ALL_KINGDOM_CARDS_BY_EXPANSION.items()]

@socketio.on('join room')
def join_room(data):
    username = data['username']
    room = data['room']
    if data['client_type'] == 'browser':
        interaction_class = BrowserInteraction
    # If the user is already in the room, reject them
    if username in connected_players[room]:
        socketio.send(f'A player with that username has already joined the game.')
        return False
    # Add the user to the room
    flask_socketio.join_room(room)
    sid = request.sid
    sids[sid] = (room, data)
    connected_players[room].append(username)
    try:
        # Add the player to the game
        game = games[room]
        game.kill_scheduled = False # Cancel erasure of the game if necessary
        game_startable_before = game.startable
        game.add_player(username, sid, interactions_class=interaction_class)
        socketio.emit("players in room", game.player_names)
        socketio.send(f'{username} has entered room {room}.\n', room=room)
        # If the game just became startable, push an event
        game_startable_after = game.startable
        if game_startable_after != game_startable_before:
            socketio.emit('game startable', room=room)
        return True # This activates the client's joined_room() callback
    except GameStartedError:
        if username in disconnected_players[room]:
            disconnected_players[room].remove(username)
            connected_players[room].append(username)
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
    if not allow_game_creation:
        socketio.send("The server is not allowing new games to be created at this time.", to=request.sid)
        return None
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
    connected_players[room].append(username)
    # Create the game object
    game = Game(socketio=socketio, room=room)
    # Add the game object to the global dictionary of games
    games[room] = game
    # Create the game's heartbeat
    game.heartbeat = HeartBeat(game)
    # Add the player to the game
    game.add_player(username, sid, interactions_class=interaction_class)
    socketio.emit("players in room", game.player_names)
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
    socketio.emit("players in room", game.player_names)
    socketio.send(f'{cpu_name} has entered room {room}.\n', room=room)
    # If the game just became startable, push an event
    game_startable_after = game.startable
    if game_startable_after != game_startable_before:
        socketio.emit('game startable', room=room)

@socketio.on('start game')
def start_game(data):
    username = data['username']
    room = data['room']
    allow_simultaneous_reactions = data['allowSimultaneousReactions']
    recommended_set_index = data.get('recommended_set_index')
    custom_set_data = data.get('custom_set_data')
    dominion = data.get('dominion')
    intrigue = data.get('intrigue')
    prosperity = data.get('prosperity')
    cornucopia = data.get('cornucopia')
    hinterlands = data.get('hinterlands')
    guilds = data.get('guilds')
    # distribute_cost = data.get('distributeCost')
    disable_attack_cards = data.get('disableAttacks')
    require_plus_two_action = data.get('requirePlusTwoAction')
    require_drawer = data.get('requireDrawer')
    require_buy = data.get('requireBuy')
    require_trashing = data.get('requireTrashing')
    # Send the game started event
    socketio.send(f'{username} has started game {room}.\n', room=room)
    socketio.emit('game started', room=room)
    game = games[room]
    # Add in customization options
    if recommended_set_index is not None:
        print("Recommended set detected.")
        # Recommended Set
        recommended_set = ALL_RECOMMENDED_SETS[recommended_set_index]
        game.recommended_set = recommended_set
    elif custom_set_data is not None:
        # Custom Set
        print("Custom set detected.")
        custom_set = CustomSet.from_json(custom_set_data)
        game.custom_set = custom_set
    else:
        # Random Game
        print("Creating random game from selected expansions.")
        if dominion:
            game.add_expansion(DominionExpansion)
        if intrigue:
            game.add_expansion(IntrigueExpansion)
        if prosperity:
            game.add_expansion(ProsperityExpansion)
        if cornucopia:
            game.add_expansion(CornucopiaExpansion)
        if hinterlands:
            game.add_expansion(HinterlandsExpansion)
        if guilds:
            game.add_expansion(GuildsExpansion)
        # if distribute_cost:
        #     game.distribute_cost = True
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
    # Simultaneous Reactions
    if allow_simultaneous_reactions:
        game.allow_simultaneous_reactions = True
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

@socketio.on('request recommended sets')
def send_recommended_sets(data):
    room = data['room']
    fake_game = Game()
    socketio.emit(
        'recommended sets',
        data=[recommended_set(fake_game).json for recommended_set in ALL_RECOMMENDED_SETS],
        room=room,
    )
    del(fake_game)

@socketio.on('request all kingdom cards')
def send_all_cards(data):
    room = data['room']
    socketio.emit(
        'all kingdom cards',
        data=all_kingdom_cards_json,
        room=room,
    )

@socketio.on("request kingdom json")
def send_kingdom_json(data):
    room = data["room"]
    game = games[room]
    supply = game.supply
    json_data = {"cards": [], "additional_cards": None}
    bane_card_class = None
    for expansion_instance in supply.customization.expansions:
        if isinstance(expansion_instance, CornucopiaExpansion):
            # Check whether there is a Bane card
            bane_card_class = expansion_instance.bane_card_class
            if bane_card_class is not None:
                json_data["bane_card_name"] = bane_card_class.name
        if isinstance(expansion_instance, ProsperityExpansion):
            # Check whether Platinum and Colony are in use
            json_data["use_platinum_and_colony"] = expansion_instance.platinum_and_colony
    for card_class in supply.card_stacks.keys():
        if card_class not in ALL_KINGDOM_CARDS or card_class == bane_card_class:
            continue
        json_data["cards"].append(card_class.name)
    print(f"Sending Kingdom JSON: {json_data}.")
    socketio.emit(
        "kingdom json",
        data=json_data,
        room=room,
    )

@socketio.on("disconnect")
def disconnect():
    try:
        sid = request.sid
        room, data = sids[sid]
        game = games[room]
        username = data['username']
        connected_players[room].remove(username)
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
                kill_game(room)
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


def kill_game(room):
    game = games[room]
    game.killed = True
    game.heartbeat.stop()
    # Erase the game from existence
    games.pop(room, None)
    connected_players.pop(room, None)
    disconnected_players.pop(room, None)
    cpus.pop(room, None)
    socketio.send(f'Game {room} has ended.\n', room=room)


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
                # Send expansion-specific info
                for expansion in self.game.supply.customization.expansions:
                    expansion.heartbeat()
            except Exception as exception:
                print(exception)
            counter += 1

    def stop(self):
        self.run = False


admin = Blueprint("admin", __name__)


@admin.before_request
@auth.login_required
def login_required():
    pass


@admin.route("/num_active_games")
def admin_num_active_games():
    return str(len(games))


@admin.route("/list_active_games")
def admin_list_active_games():
    return jsonify(connected_players)


@admin.route("/kill_game/<room>")
def admin_kill_game(room):
    if room not in games:
        abort(404)
    socketio.send(f"An administrator has killed game {room}.")
    kill_game(room)
    return f"Game {room} has been killed."


@admin.route("/forbid_new_games")
def admin_forbid_new_games():
    global allow_game_creation
    allow_game_creation = False
    return "Game creation is now forbidden."


@admin.route("/allow_new_games")
def admin_allow_new_games():
    global allow_game_creation
    allow_game_creation = True
    return "Game creation is now allowed."


@admin.route("/broadcast_message/<message>")
def admin_broadcast_message(message):
    socketio.send(message)
    return "Message broadcasted."


@admin.route("/kill_server")
def kill_server():
    print("An administrator has stopped the game server.")
    socketio.send("An administrator has stopped the game server. You have been disconnected.")
    socketio.stop()
    exit()


app.register_blueprint(admin, url_prefix="/admin")


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)