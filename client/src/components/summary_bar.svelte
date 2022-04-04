<script>
    export let socket;
    export let gameStarted = false;
    export let currentPlayer = "";
    
    let actions = 1;
    let buys = 1;
    let coppers = 0;
    let turns_played = 0;

    socket.on(
        "current turn info",
        (data) => {
            actions = data.actions;
            buys = data.buys;
            coppers = data.coppers;
            turns_played = data.turns_played;
        }
    );
</script>

{#if gameStarted}
    <main class="container">
        <div>
            <div>
                Current Player: {currentPlayer = currentPlayer == null ? "No One" : currentPlayer}
            </div>
        </div>
        <div>
            <div>
                {actions} Actions
        </div>
        </div>
        <div>
            <div>
                {buys} Buys
        </div>
        </div>
        <div>
            <div>
                {coppers} <i class="fa-solid fa-coins"></i>
        </div>
        </div>
        <div>
            <div>
                Turn #{turns_played}
        </div>
        </div>
    </main>
{/if}

<style>
    main {
        z-index: 10;
        position: -webkit-sticky;
        position: sticky;
        top: 0;
        background-color: #343338;
        color: #dadada;
        padding-top: 20px;
        padding-bottom: 20px;
        margin-top: 20px;
        margin-bottom: 20px;
        display: flex;
        flex-direction: row;
        justify-content: space-evenly;
    }
</style>