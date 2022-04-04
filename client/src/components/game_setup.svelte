<script>
    import {createEventDispatcher} from "svelte";

    const dispatch = createEventDispatcher();

    export let socket;
    export let username;
    export let room;
    export let roomJoined;
    export let roomCreator;
    
    let gameStartable = false;
    let shown = true;

    var expansions = [
        {name: "Intrigue", property: "intrigue", selected: false},
        {name: "Prosperity", property: "prosperity", selected: false},
    ]

    var supplyCustomizations = [
        {name: "Distribute cost", property: "distributeCost", selected: false},
        {name: "Disable Attacks", property: "disableAttacks", selected: false},
        {name: "Require +2 Action", property: "requirePlusTwoAction", selected: false},
        {name: "Require +1 Card", property: "requireDrawer", selected: false},
        {name: "Require +1 Buy", property: "requireBuy", selected: false},
        {name: "Require Trashing", property: "requireTrashing", selected: false},
    ]

    function addCPU() {
        socket.emit("add cpu", {room: room});
    }


    function startGame() {
        if (!gameStartable) {
            alert("The game cannot be started without at least two players.");
        }
        else {
            var gameProperties = {
                username: username,
                room: room,
            };
            expansions.forEach(
                (expansion) => {
                    gameProperties[expansion.property] = expansion.selected;
                }
            );
            supplyCustomizations.forEach(
                (customization) => {
                    gameProperties[customization.property] = customization.selected;
                }
            );
            socket.emit(
                "start game",
                gameProperties
            );
            dispatch("started");
            shown = false;
        }
    }

    socket.on("game startable", function(data) {
        gameStartable = true;
    });

    socket.on("game started", function(data) {
        dispatch("started");
        shown = false;
    })
</script>

{#if shown}
    {#if roomJoined && roomCreator}
        <main>
            <button type="button" on:click={startGame} class="btn btn-primary btn-lg btn-block">Start Game</button>
            <button type="button" on:click={addCPU} class="btn btn-secondary btn-lg btn-block">Add CPU</button>
            <div class="grid-item">
                {#each expansions as expansion}
                    <label>
                        <input type="checkbox" bind:checked={expansion.selected}>
                        {expansion.name} Expansion
                    </label>
                {/each}
            </div>
            <div class="grid-item">
                {#each supplyCustomizations as customization}
                    <label>
                        <input type="checkbox" bind:checked={customization.selected}>
                        {customization.name}
                    </label>
                {/each}
            </div>
        </main>
    {:else if roomJoined}
        <main>
            <div class="grid-item-2">
                <p>Please wait for the host to start the game.</p>
            </div>
        </main>
    {/if}
{/if}

<style>
    main {
        margin-top: 50px;
        display: grid;
        grid-template-columns: repeat(2, 50%);
        justify-items: center;
    }

    .grid-item {
        grid-column-start: auto;
        justify-self: center;
        text-align: left;
    }

    .grid-item-2 {
        grid-column: 1/-1;
        justify-self: center;
        text-align: center;
    }
</style>