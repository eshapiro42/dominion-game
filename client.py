import prettytable
import random
import socketio
import sys
import time
from contextlib import contextmanager
from threading import Lock


sio = socketio.Client()


lock = Lock()
username = None
room = None
room_creator = False
joined = False
startable = False


@contextmanager
def nullcontext():
    yield

def json():
    return {
        'username': username,
        'room': room,
        'room_creator': room_creator,
    }

def get_username():
    global username
    username = input('Please enter your username: ')
    print()

def set_room(room_id):
    global room
    room = room_id

def joined_room(success):
    global joined
    if success:
        joined = True
    else:
        print('Invalid room ID.')

def enter_room():
    global room
    global room_creator
    prompt = 'What would you like to do?'
    options = ['Create a new room', 'Join an existing room']
    choice = choose_from_options(prompt=prompt, options=options, force=True)
    if choice == 'Create a new room':
        room_creator = True
        sio.emit('create room', json(), callback=set_room)
        time.sleep(0.1)
    elif choice == 'Join an existing room':
        room_creator = False
        while not joined:
            room = input('Please enter the room ID: ')
            sio.emit('join room', json(), callback=joined_room)
            time.sleep(0.5)

def setup_room():
    if room_creator:
        while True:
            prompt = 'What would you like to do?'
            options = ['Add CPU', 'Start Game']
            choice = choose_from_options(prompt=prompt, options=options, force=True)
            if choice == 'Add CPU':
                sio.emit('add cpu', json())
            elif choice == 'Start Game':
                if not startable:
                    print('The game cannot be started without at least two players.')
                    continue
                else:
                    sio.emit('start game', json())
                    break
            time.sleep(0.5)
        joined_room(True)
    else:
        print('Please wait for the game to start...\n')

@sio.event
def connect():
    print("You are connected to the server.\n")
    get_username()
    enter_room()
    setup_room()

@sio.event
def connect_error(data):
    print(f"Unable to connect to the server: {data}.\n")
    
@sio.event
def disconnect():
    print("You have been disconnected from the server.\n")
    sio.disconnect()

@sio.on('game startable')
def game_startable():
    with lock:
        global startable
        if room_creator:
            startable = True
            print('The game can now be started.\n')

@sio.on('message')
def on_message(data):
    with lock:
        print(data)

@sio.on('enter choice')
def send_choice(data):
    with lock:
        prompt = data['prompt']
        try:
            return int(input(prompt))
        except:
            return None

@sio.on('choose yes or no')
def choose_yes_or_no(data):
    with lock:
        prompt = data['prompt']
        return input(prompt)

def choose_from_options(prompt, options, force):
    if joined:
        context = lock
    else:
        context = nullcontext()
    with context:
        print(prompt)
        print()
        while True:
            options_table = prettytable.PrettyTable(hrules=prettytable.ALL)
            options_table.field_names = ['Number', 'Option']
            for idx, option in enumerate(options):
                options_table.add_row([idx + 1, option])
            try:
                print(options_table)
                if force:
                    response_num = int(input(f'Enter choice 1-{len(options)}: '))
                    print()
                    response = options[response_num - 1]
                else:
                    response_num = int(input(f'Enter choice 0-{len(options)} (0 to skip): '))
                    print()
                    if response_num == 0:
                        return None
                    else:
                        response = options[response_num - 1]
                return response
            except (IndexError, ValueError):
                print('That is not a valid choice.\n')


if __name__ == '__main__':
    sio.connect('http://womboserver.duckdns.org:5000', transports=['websocket'])
