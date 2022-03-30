<script>
    import GameSetup from "./components/game_setup.svelte";
    import Hand from "./components/hand.svelte";
    import Lobby from "./components/lobby.svelte";
    import MessageBoard from "./components/message_board.svelte";
    import PlayedCards from "./components/played_cards.svelte";
    import Supply from "./components/supply.svelte";

    export let socket;

    let roomJoined = false;
    let gameStarted = false;
    let username = "";
    let room = null;
    let roomCreator = false;
    let currentPlayer = null;

    function joinedRoom(event) {
        roomJoined = true;
        username = event.detail.username;
        room = event.detail.room;
        roomCreator = event.detail.roomCreator;
    }

    function startedGame(event) {
        gameStarted = true;
    }

    socket.on(
        "new turn", function(data) {
        currentPlayer = data.player;
    });
</script>

<main>
    <header>
        <h1>Dominion</h1>
        {#if roomJoined}
        <p>Room ID: {room}</p>
        {/if}
    </header>

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