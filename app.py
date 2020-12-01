import random
import string
from flask import Flask
from game import Game
from interactions import NetworkedCLIInteraction, NetworkedCLIBroadcast, AutoInteraction
from socketio import Server, WSGIApp
import tornado
import tornado.websocket

socketio = Server(async_mode='threading')
app = Flask(__name__)
app.wsgi_app = WSGIApp(socketio, app.wsgi_app)


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
    # Add the user to the room
    socketio.enter_room(sid, room)
    sids[sid] = (room, data)
    try:
        # Add the player to the game
        game = games[room]
        game_startable_before = game.startable
        game.add_player(username, sid, interactions_class=NetworkedCLIInteraction)
        socketio.send(f'{username} has entered the room.', room=room)
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
    characters = string.ascii_uppercase + string.digits
    # Create a unique room ID
    room = ''.join(random.choice(characters) for i in range(4))
    while room in games:
        room = ''.join(random.choice(characters) for i in range(4))
    # Add the user to the room
    socketio.enter_room(sid, room)
    sids[sid] = (room, data)
    # Create the game object
    game = Game(broadcast_class=NetworkedCLIBroadcast, socketio=socketio, room=room)
    # Add the game object to the global dictionary of games
    games[room] = game
    # Add the player to the game
    game.add_player(username, sid, interactions_class=NetworkedCLIInteraction)
    socketio.send(f'{username} has created room {room}', room=room)
    return room # This activates the client's set_room() callback

@socketio.on('add cpu')
def add_cpu(sid, data):
    username = data['username']
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
    socketio.send(f'{cpu_name} has entered the room.', room=room)
    # If the game just became startable, push an event
    game_startable_after = game.startable
    if game_startable_after != game_startable_before:
        socketio.emit('game startable', room=room)

@socketio.on('start game')
def start_game(sid, data):
    username = data['username']
    room = data['room']
    # Start the game
    game = games[room]
    game.start()
    socketio.send(f'{username} has started the game.', room=room)

@socketio.event
def disconnect(sid):
    room, data = sids[sid]
    username = data['username']
    socketio.leave_room(sid, room)
    socketio.send(f'{username} has left the room.', room=room)


if __name__ == '__main__':
    # app = WSGIApp(socketio)
    # import eventlet
    # eventlet.wsgi.server(eventlet.listen(('0.0.0.0', 5000)), app)

    app.run(host='0.0.0.0', debug=True, threaded=True)

    # app.listen(5000)
    # tornado.ioloop.IOLoop.current().start()