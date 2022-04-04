<script>
    import DiscardPile from "./components/discard_pile.svelte";
    import GameSetup from "./components/game_setup.svelte";
    import Hand from "./components/hand.svelte";
    import Lobby from "./components/lobby.svelte";
    import PlayedCards from "./components/played_cards.svelte";
    import PlayerInfo from "./components/player_info.svelte";
    import PopUp from "./components/pop_up.svelte";
    import SummaryBar from "./components/summary_bar.svelte";
    import Supply from "./components/supply.svelte";
    import Toasts from "./components/toasts.svelte";
    import TradeRoute from "./components/trade_route.svelte";
    import Trash from "./components/trash.svelte";

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

    function createPopUp(prompt, force, type, range=null, options=null) {
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
        socket.emit("response", event.detail.selection);
        popUp = {
            show: false,
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
        function(data) {
            createPopUp(data.prompt, null, "boolean");
        }
    );

    socket.on(
        "choose from range",
        function(data) {
            createPopUp(data.prompt, data.force, "range", {start: data.start, stop: data.stop});
        }
    );

    socket.on(
        "choose from options",
        function(data) {
            createPopUp(data.prompt, data.force, "options", null, data.options);
        }
    );

    socket.on(
        "connect",
        function(data) {
            console.log(socket.id);
        }
    )

    socket.on(
        "response received",
        () => {
            popUp = {
                show: false,
                prompt: "",
                force: false,
                type: null,
                range: null,
                options: null,
            }
        }
    )
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

    <Toasts
        {socket}
        {username}
        {room}
    />

    <SummaryBar
        {socket}
        {gameStarted}
        {currentPlayer}
    />

    <Lobby 
        {socket}
        on:joined={joinedRoom}
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

    <DiscardPile
        {socket}
        {gameStarted}
    />

    <Trash
        {socket}
        {gameStarted}
    />

    <TradeRoute
        {socket}
        {gameStarted}
    />

    <PlayerInfo
        {socket}
        {gameStarted}
    />
</main>

<style>
    main {
        text-align: center;
        padding-bottom: 20px;
    }

    header {
        margin: 20px;
    }
</style>