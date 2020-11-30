import prettytable
import random
import socketio


sio = socketio.Client()


class Client:
    def __init__(self):
        # sio.connect('http://0.0.0.0:5000', transports=['websocket'])
        sio.connect('http://womboserver.duckdns.org:5000')
        self.username = self.get_username()
        self.room = None
        self.enter_room()
    
    @property
    def json(self):
        return {
            'username': self.username,
            'room': self.room,
            'room_creator': self.room_creator,
        }

    def get_username(self):
        return input('Please enter your username: ')

    def set_room(self, room):
        self.room = room

    def enter_room(self):
        prompt = 'What would you like to do?'
        options = ['Create a new room', 'Join an existing room']
        choice = choose_from_options(prompt=prompt, options=options, force=True)
        if choice == 'Create a new room':
            self.room_creator = True
            sio.emit('create room', self.json, callback=self.set_room)
        elif choice == 'Join an existing room':
            self.room_creator = False
            self.room = input('Please enter the room ID: ')
            sio.emit('join room', self.json)

# @sio.event
# def connect():
#     print("You are connected to the server.")

@sio.event
def disconnect():
    print("You have been disconnected from the server.")

@sio.on('game startable')
def game_startable():
    if client.room_creator:
        print('The game can now be started.')
        input('Press Enter when you are ready to start the game... ')
        sio.emit('start game', client.json)

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
    client = Client()


