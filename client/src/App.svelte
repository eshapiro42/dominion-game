<script>
    import GameSetup from "./components/game_setup.svelte";
    import Hand from "./components/hand.svelte";
    import Lobby from "./components/lobby.svelte";
    import MessageBoard from "./components/message_board.svelte";
    import PlayedCards from "./components/played_cards.svelte";
    import PopUp from "./components/pop_up.svelte";
    import Supply from "./components/supply.svelte";

    export let socket;

    let roomJoined = false;
    let gameStarted = false;
    let username = "";
    let room = null;
    let roomCreator = false;
    let currentPlayer = null;
    let popUp = {
        show: false,
    };

    function joinedRoom(event) {
        roomJoined = true;
        username = event.detail.username;
        room = event.detail.room;
        roomCreator = event.detail.roomCreator;
    }

    function startedGame(event) {
        gameStarted = true;
    }

    function createPopUp(callback, prompt, force, type, range=null, options=null) {
        popUp.callback = callback;
        popUp.prompt = prompt;
        popUp.force = force;
        popUp.type = type;
        if (type == "range") {
            popUp.range = range;
        }
        else if (type == "options") {
            popUp.options = options;
        }
        popUp.show = true;
    }

    function submitPopUp(event) {
        if (popUp.force && event.detail.selection == null) {
            alert("You must make a selection.");
            return;
        }
        popUp.callback(event.detail.selection);
        popUp = {
            show: false,
            callback: null,
            prompt: "",
            force: false,
            type: null,
            range: null,
            options: null,
        }
    }

    socket.on(
        "new turn",
        function(data) {
            currentPlayer = data.player;
        }
    );

    socket.on(
        "choose yes or no",
        function(data, callback) {
            createPopUp(callback, data.prompt, null, "boolean");
        }
    );

    socket.on(
        "choose from range",
        function(data, callback) {
            createPopUp(callback, data.prompt, data.force, "range", {start: data.start, stop: data.stop});
        }
    );

    socket.on(
        "choose from options",
        function(data, callback) {
            createPopUp(callback, data.prompt, data.force, "options", null, data.options);
        }
    );
</script>

<main>
    <header>
        <h1>Dominion</h1>
        {#if roomJoined}
        <p>Room ID: {room}</p>
        {/if}
    </header>

    <PopUp
        show={popUp.show}
        prompt={popUp.prompt}
        force={popUp.force}
        type={popUp.type}
        range={popUp.range}
        options={popUp.options}
        on:submit={submitPopUp}
    />

    <Lobby 
        {socket}
        on:joined={joinedRoom}
    />

    <MessageBoard
        {socket}
        {username}
        {room}
        {roomJoined}
    />

    <GameSetup
        {socket}
        {username}
        {room}
        {roomJoined}
        {roomCreator}
        on:started={startedGame}
    />

    <PlayedCards
        {socket}
        {gameStarted}
        {currentPlayer}
    />

    <Hand
        {socket}
        {gameStarted}
    />

    <Supply
        {socket}
        {gameStarted}
    />
</main>

<style>
    main {
        text-align: center;
    }

    header {
        margin: 20px;
    }
</style>