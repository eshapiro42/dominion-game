# dominion-game

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

Never commit the compiled files! They are explicitly listed in `.gitignore` for a reason.

## Backend Setup

The backend is written in `Python` and uses `Flask-SocketIO` as a server. Make sure you have `Python 3.8` or newer installed. I recommend using the official installers from [Python.org](https://www.python.org/downloads/).

Navigate into the `dominion-game` repository that you just cloned and create a new virtual environment there. Make sure you are using the desired version of `Python` to create the virtual environment (i.e., replace `python3.10` in the second line below with whichever interpreter you are using).

```
cd dominion-game
python3.10 -m venv venv
```

Activate the newly create virtual environment and install dependencies.

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