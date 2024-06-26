<script>
    import {
        socket,
        currentPlayer,
        room,
        username,
    } from "./stores.js";

    import {flashTitle} from "./common.js";

    import DiscardPile from "./components/discard_pile.svelte";
    import GameLog from "./components/game_log.svelte";
    import GameSetup from "./components/game_setup.svelte";
    import GameOver from "./components/game_over.svelte";
    import Hand from "./components/hand.svelte";
    import Lobby from "./components/lobby.svelte";
    import MiscellaneousSelection from "./components/miscellaneous_selection.svelte";
    import PlayedCards from "./components/played_cards.svelte";
    import PlayerInfo from "./components/player_info.svelte";
    import Prizes from "./components/prizes.svelte";
    import Settings from "./components/settings.svelte";
    import SideBar from "./components/side_bar.svelte";
    import SummaryBar from "./components/summary_bar.svelte";
    import Supply from "./components/supply.svelte";
    import Toasts from "./components/toasts.svelte";
    import TradeRoute from "./components/trade_route.svelte";
    import Trash from "./components/trash.svelte";
    import Waiting from "./components/waiting.svelte";

    let gameStarted = false;
    let roomCreator = false;
    let roomJoined = false;
    let miscellaneousSelection = {
        show: false,
    };
    let gameOver = {
        show: false,
    }
    let saveFileOptions = {
        types: [
            {
                description: "JSON Files",
                accept: {
                    "application/json": [".json"],
                }
            }
        ]
    };
    let waitingOnPlayers = [];

    function joinedRoom(event) {
        $room = event.detail.room;
        $username = event.detail.username;
        roomCreator = event.detail.roomCreator;
        roomJoined = true;
    }

    function startedGame(event) {
        gameStarted = true;
    }

    function createMiscellaneousSelection(prompt, force, type, range=null, options=null, cards=null, waitingForSelection=null) {
        miscellaneousSelection.prompt = prompt;
        miscellaneousSelection.force = force;
        miscellaneousSelection.type = type;
        if (type == "range") {
            miscellaneousSelection.range = range;
        }
        else if (type == "options") {
            miscellaneousSelection.options = options;
        }
        else if (type == "cards") {
            miscellaneousSelection.cards = cards;
            miscellaneousSelection.waitingForSelection = waitingForSelection;
        }
        miscellaneousSelection.show = true;
    }

    function submitMiscellaneousSelection(event) {
        if (miscellaneousSelection.force && event.detail.selection == null) {
            alert("You must make a selection.");
            return;
        }
        $socket.emit("response", event.detail.selection);
        miscellaneousSelection = {
            show: false,
            prompt: "",
            force: false,
            type: null,
            range: null,
            options: null,
            cards: null,
            waitingForSelection: null,
        }
    }

    function createGameOver(endGameData, cards) {
        gameOver.endGameData = endGameData;
        gameOver.cards = cards;
        gameOver.show = true;
    }

    $socket.on(
        "new turn",
        function(data) {
            $currentPlayer = data.player;
            if ($currentPlayer === $username) {
                document.documentElement.setAttribute("your-turn", true);
            }
            else {
                document.documentElement.setAttribute("your-turn", false);
            }
        }
    );

    $socket.on(
        "choose yes or no",
        function(data) {
            createMiscellaneousSelection(data.prompt, null, "boolean");
        }
    );

    $socket.on(
        "choose from range",
        function(data) {
            createMiscellaneousSelection(data.prompt, data.force, "range", {start: data.start, stop: data.stop});
        }
    );

    $socket.on(
        "choose from options",
        function(data) {
            createMiscellaneousSelection(data.prompt, data.force, "options", null, data.options);
        }
    );

    $socket.on(
        "choose cards from list",
        function(data) {
            var waitingForSelection = {
                value: true,
                type: "",
                prompt: data.prompt,
                force: data.force,
                maxCards: data.max_cards,
                ordered: data.ordered,
            }
            createMiscellaneousSelection(data.prompt, data.force, "cards", null, null, data.cards, waitingForSelection)
        }
    );

    $socket.on(
        "connect",
        function(data) {
            // console.log($socket.id);
        }
    )

    $socket.on(
        "response received",
        () => {
            miscellaneousSelection = {
                show: false,
                prompt: "",
                force: false,
                type: null,
                range: null,
                options: null,
                cards: null,
                waitingForSelection: null,
            }
        }
    )

    $socket.on(
        "game over",
        (data) => {
            createGameOver(data.endGameData, data.cards);
            // $socket.disconnect();
        }
    );

    $socket.on(
        "kingdom json",
        async (data) => {
            const fileHandle = await window.showSaveFilePicker(saveFileOptions);
            const writable = await fileHandle.createWritable();
            await writable.write(JSON.stringify(data));
            await writable.close();
        }
    );

    $socket.on(
        "waiting on player",
        (player) => {
            waitingOnPlayers = [...waitingOnPlayers, player];
        }
    );

    $socket.on(
        "not waiting on player",
        (player) => {
            waitingOnPlayers = waitingOnPlayers.filter(item => item != player);
        }
    )

    $: if ($currentPlayer === $username && $currentPlayer !== "") {
        flashTitle("Your Turn!");
    }

    function preventUnload(event) {
        event.preventDefault(); 
        event.returnValue = true; 
    }

    $: if (gameStarted) {
        window.addEventListener(
            "beforeunload", 
            preventUnload,
        );
    }

    $: if (gameOver.show) {
        window.removeEventListener(
            "beforeunload",
            preventUnload,
        );
    }
</script>

<main>
    <div class="panel">
        <div class="title">
            <h1>Dominion</h1> <Settings/>
        </div>
        {#if roomJoined}
        <p>Room ID: {$room}</p>
        {/if}
    </div>

    <!-- <Toasts/> -->

    <Lobby 
        on:joined={joinedRoom}
    />

    <GameSetup
        {roomJoined}
        {roomCreator}
        on:started={startedGame}
    />

    <GameLog/>

    {#if gameStarted}
        <SummaryBar/>

        <SideBar/>

        <MiscellaneousSelection
            show={miscellaneousSelection.show}
            prompt={miscellaneousSelection.prompt}
            force={miscellaneousSelection.force}
            type={miscellaneousSelection.type}
            range={miscellaneousSelection.range}
            options={miscellaneousSelection.options}
            cards={miscellaneousSelection.cards}
            waitingForSelection={miscellaneousSelection.waitingForSelection}
            on:submit={submitMiscellaneousSelection}
        />

        <GameOver
            show={gameOver.show}
            endGameData={gameOver.endGameData}
        />

        <PlayedCards/>

        <Hand/>

        <Supply/>

        <DiscardPile/>

        <Trash/>

        <TradeRoute/>

        <Prizes/>

        <PlayerInfo/>

        <Waiting
            players={waitingOnPlayers}
        />
    {/if}
</main>

<style>
    main {
        text-align: center;
        padding-bottom: 20px;
    }

    .title {
        width: 100%;
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: baseline;
        gap: 20px;
    }
</style>