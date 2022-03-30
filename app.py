import eventlet
eventlet.monkey_patch()

import flask_socketio
import random
import string
from flask import Flask, request, send_from_directory
from dominion.expansions import IntrigueExpansion, ProsperityExpansion
from dominion.game import Game
from dominion.interactions import NetworkedCLIInteraction, BrowserInteraction, AutoInteraction


app = Flask(__name__)
app.config.from_object("config.Config")
socketio = flask_socketio.SocketIO(app)


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

# Global dictionary of CPUs, indexed by room ID, {room: CPU_COUNT}
cpus = {}


@socketio.on('join room')
def join_room(data):
    username = data['username']
    room = data['room']
    try:
        if data['client_type'] == 'browser':
            interaction_class = BrowserInteraction
    except KeyError:
        interaction_class = NetworkedCLIInteraction
    # Add the user to the room
    flask_socketio.join_room(room)
    sid = request.sid
    sids[sid] = (room, data)
    try:
        # Add the player to the game
        game = games[room]
        game_startable_before = game.startable
        game.add_player(username, sid, interactions_class=interaction_class)
        socketio.send(f'{username} has entered the room.\n', room=room)
        # If the game just became startable, push an event
        game_startable_after = game.startable
        if game_startable_after != game_startable_before:
            socketio.emit('game startable', room=room)
        return True # This activates the client's joined_room() callback
    except KeyError:
        return False

@socketio.on('create room')
def create_room(data):
    username = data['username']
    try:
        if data['client_type'] == 'browser':
            interaction_class = BrowserInteraction
    except KeyError:
        interaction_class = NetworkedCLIInteraction
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
    socketio.send(f'{cpu_name} has entered the room.\n', room=room)
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
    distribute_cost = data['distributeCost']
    disable_attack_cards = data['disableAttacks']
    # Send the game started event
    socketio.send(f'{username} has started the game.\n', room=room)
    socketio.emit('game started', room=room)
    # time.sleep(1) # I'm not sure why this was in here
    game = games[room]
    # Add in customization options
    if intrigue:
        game.add_expansion(IntrigueExpansion)
    if prosperity:
        game.add_expansion(ProsperityExpansion)
    if distribute_cost:
        game.distribute_cost = True
    if disable_attack_cards:
        game.disable_attack_cards = True
    # Start the game (nothing can happen after this)
    game.start()

@socketio.on('message')
def send_message(data):
    username = data['username']
    room = data['room']
    message = data['message']
    socketio.send(f'{username}: {message}\n', room=f'{room}_message_board')

@socketio.on("disconnect")
def disconnect():
    try:
        sid = request.sid
        room, data = sids[sid]
        username = data['username']
        flask_socketio.leave_room(room)
        socketio.send(f'{username} has left the room.\n', room=room)
    except KeyError:
        pass


if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=5000)