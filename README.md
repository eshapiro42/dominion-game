# `dominion-game`

[![Documentation Status](https://readthedocs.org/projects/dominion-game/badge/?version=latest)](https://dominion-game.readthedocs.io/en/latest/?badge=latest)


## Getting Started

Clone this repository.

```
git clone https://github.com/eshapiro42/dominion-game.git
``` 

## Frontend Setup

The frontend uses the `Svelte` framework and requires compilation before it can be run. Make sure you have `Node.js` and `npm` installed. I recommend using the official installers from [Nodejs.org](https://nodejs.org/en/download/).

Navigate into the `dominion-game` repository that you just cloned and install dependencies. 

```
cd dominion-game
npm install
```

* To compile the frontend once:
    ```
    npm run build
    ```

* To compile the frontend whenever a source file changes, leave the following command running:
    ```
    npm run dev
    ```

## Backend Setup

The backend is where the game state and logic is all kept. Both the frontend and backend use the [`Socket.IO`](https://socket.io/) protocol to communicate with each other. Interfaces to the various available clients are implemented by subclassing `dominion.interactions.interaction.Interaction`. In particular, the web browser interface is defined in `dominion.interactions.browser.BrowserInteraction`. 

The backend processes game logic and keeps track of updating the game state. Each game has a heartbeat which enables displays across all clients to update whenever a change occurs on the backend, without the game need complicated logic to know when to send updates. The server also handles getting answers from each client (which card to play, which card to discard, etc.), which it does by sending the client a request for a response and waiting until one is received. Both the heartbeat and response requests are refreshable, which allows players to rejoin a game from which they have become disconnected (if they use precisely the same username as before) and pick up right where they left off.

The backend is written in `Python` and uses `Flask-SocketIO` as an HTTP and `Socket.IO` server. Make sure you have `Python 3.11` or newer installed. I recommend using the official installers from [Python.org](https://www.python.org/downloads/).

If you are using Windows (which I do not recommend), you will need to install Microsoft Visual C++ 14.0 or higher or you will encounter issues trying to install Python dependencies. You can install it from [Microsoft C++ Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/). If you're using Linux or WSL, you can skip this step.

Navigate into the `dominion-game` repository that you just cloned and create a new virtual environment there. Make sure you are using the desired version of `Python` to create the virtual environment (i.e., replace `python3.10` in the second line below with whichever interpreter you are using).

```
cd dominion-game
python3.10 -m venv venv
```

Activate the newly created virtual environment and install dependencies.

```
. venv/bin/activate
python -m pip install --upgrade pip setuptools wheel
python -m pip install -r requirements.txt
```

The backend must always be run from within this virtual environment.

* To launch the server in debug mode:
    ```
    python app.py
    ```

* To launch the server in production mode, execute the command located in `Procfile` to use `gunicorn`:

    ```
    gunicorn -k geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 --timeout 0 app:app
    ```

## Putting it Together

Assuming the frontend is compiled and the backend server is running, you should be able to play the game in your browser. If you're running the debug server, the default port is `5000` so it can be accessed at `localhost:5000`. If you're running the production server, the default port is `8000` so it can be accessed at `localhost:8000`.

![image](https://user-images.githubusercontent.com/11021129/163091317-71e3153a-dde3-467e-bd6a-27e60bc2a61c.png)

## Documentation

To build the docs for the backend, use the following command:

```
(cd docs && sphinx-apidoc -f -o source ../dominion && make html)
```
