import random
import string
from flask import Flask
from game import Game
from interactions import NetworkedCLIInteraction, NetworkedCLIBroadcast
from socketio import Server, WSGIApp

socketio = Server()
app = Flask(__name__)
app.config['SECRET_KEY'] = 'Dooooooo?'
app.wsgi_app = WSGIApp(socketio, app.wsgi_app)


# Global dictionary of games, indexed by room ID
games = {}

# Global dictionary of sids, {sid: (room, data)}
sids = {}


@socketio.on('join room')
def join_room(sid, data):
    username = data['username']
    room = data['room']
    # Add the user to the room
    socketio.enter_room(sid, room)
    sids[sid] = (room, data)
    # Add the player to the game
    game = games[room]
    game_startable_before = game.startable
    game.add_player(username, sid)
    socketio.send(f'{username} has entered the room.', room=room)
    # If the game just became startable, push an event
    game_startable_after = game.startable
    if game_startable_after != game_startable_before:
        print('The game is startable.')
        socketio.emit('game startable', room=room)

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
    game = Game(interactions_class=NetworkedCLIInteraction, broadcast_class=NetworkedCLIBroadcast, socketio=socketio, room=room)
    # Add the game object to the global dictionary of games
    games[room] = game
    # Add the player to the game
    game.add_player(username, sid)
    socketio.send(f'{username} has created room {room}', room=room)
    return room # This activates the client.set_room() callback

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
    import eventlet
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
    # app.run(debug=True, threaded=True)