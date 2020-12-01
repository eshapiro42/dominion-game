import prettytable
import random
import socketio
import time


sio = socketio.Client()


def json():
    return {
        'username': username,
        'room': room,
        'room_creator': room_creator,
    }

def get_username():
    return input('Please enter your username: ')

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
    else:
        print('Please wait for the game to start...')

# @sio.event
# def connect():
#     print("You are connected to the server.")

@sio.event
def disconnect():
    print("You have been disconnected from the server.")

@sio.on('game startable')
def game_startable():
    global startable
    if room_creator:
        startable = True
        print('The game can now be started.')

@sio.on('message')
def on_message(data):
    print(data)

@sio.on('enter choice')
def send_choice(data):
    prompt = data['prompt']
    try:
        return int(input(prompt))
    except:
        return None

@sio.on('choose yes or no')
def choose_yes_or_no(data):
    prompt = data['prompt']
    return input(prompt)

def choose_from_options(prompt, options, force):
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
    # sio.connect('http://0.0.0.0:5000', transports=['websocket'])
    sio.connect('http://womboserver.duckdns.org:5000')
    username = get_username()
    room = None
    room_creator = False
    joined = False
    startable = False
    enter_room()
    setup_room()