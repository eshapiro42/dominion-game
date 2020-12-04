import random
import string
import time
from game import Game
from interactions import NetworkedCLIInteraction, BrowserInteraction, AutoInteraction
from socketio import Server, WSGIApp


# socketio = Server(async_mode='eventlet', async_handlers=True, cors_allowed_origins='*')
socketio = Server(async_mode='eventlet', async_handlers=True)

static_files = {
    '/': 'static/index.html',
    '/static/socket.io.js': 'static/socket.io.js',
    '/static/socket.io.js.map': 'static/socket.io.js.map',
    '/static/client.js': 'static/client.js',
    # '/static/style.css': 'static/style.css',
}

app = WSGIApp(socketio, static_files=static_files)

# Global dictionary of games, indexed by room ID
games = {}

# Global dictionary of sids, {sid: (room, data)}
sids = {}

# Global dictionary of CPUs, indexed by room ID, {room: CPU_COUNT}
cpus = {}


@socketio.on('join room')
def join_room(sid, data):
    username = data['username']
    room = data['room']
    try:
        if data['client_type'] == 'browser':
            interaction_class = BrowserInteraction
    except KeyError:
        interaction_class = NetworkedCLIInteraction
    # Add the user to the room
    socketio.enter_room(sid, room)
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
def create_room(sid, data):
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
    socketio.enter_room(sid, room)
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
def add_cpu(sid, data):
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
def start_game(sid, data):
    username = data['username']
    room = data['room']
    # Start the game
    socketio.send(f'{username} has started the game.\n', room=room)
    socketio.emit('game started', room=room)
    time.sleep(1)
    game = games[room]
    game.start()

@socketio.on('message')
def send_message(sid, data):
    username = data['username']
    room = data['room']
    message = data['message']
    socketio.send(f'{username}: {message}\n', room=f'{room}_message_board')

@socketio.event
def disconnect(sid):
    try:
        room, data = sids[sid]
        username = data['username']
        socketio.leave_room(sid, room)
        socketio.send(f'{username} has left the room.\n', room=room)
    except KeyError:
        pass


if __name__ == '__main__':
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)