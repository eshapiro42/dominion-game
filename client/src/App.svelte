<script>
    import {
        socket,
        currentPlayer,
        room,
        username,
    } from "./stores.js";

    import DiscardPile from "./components/discard_pile.svelte";
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
            $socket.disconnect();
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

    $: headerClass = gameStarted ? "panel" : ""; // This will re-center the header once the game has started

    $: if ($currentPlayer === $username && $currentPlayer !== "") {
        // If the tab is not active, flash the title until it is active
        // If the tab is already active, this should just flash once
        document.title = "Your Turn!";
        let flashInterval = setInterval(
            () => {
                if (!document.hidden) {
                    document.title = "Dominion";
                    clearInterval(flashInterval);
                }
                else {
                    document.title = (document.title == "Dominion" ? "Your Turn!" : "Dominion");
                }
            },
            1000,
        );
    }
</script>

<main>
    <header>
        <div class={headerClass}>
            <div class="title">
                <h1>Dominion</h1> <Settings/>
            </div>
            {#if roomJoined}
            <p>Room ID: {$room}</p>
            {/if}
        </div>
    </header>

    <Toasts/>

    <Lobby 
        on:joined={joinedRoom}
    />

    <GameSetup
        {roomJoined}
        {roomCreator}
        on:started={startedGame}
    />

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
    {/if}
</main>

<style>
    main {
        text-align: center;
        padding-bottom: 20px;
    }

    header {
        margin: 20px;
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