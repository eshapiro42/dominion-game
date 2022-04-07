<script>
    export let socket;
    export let gameStarted = false;
    export let currentPlayer = "";
    
    let phase = "";
    let actions = 1;
    let buys = 1;
    let coppers = 0;
    let handSize = 5;
    let turnsPlayed = 0;

    socket.on(
        "current turn info",
        (data) => {
            phase = data.current_phase;
            actions = data.actions;
            buys = data.buys;
            coppers = data.coppers;
            handSize = data.hand_size;
            turnsPlayed = data.turns_played;
        }
    );
</script>

{#if gameStarted}
    <div class="panel-sticky">
        <main class="panel">
            <div>
                <div>
                    {currentPlayer = currentPlayer == null ? "No One" : currentPlayer}
                </div>
            </div>
            <div>
                <div>
                    {phase}
                </div>
            </div>
            <div>
                <div>
                    {actions}
                </div>
            </div>
            <div>
                <div>
                    {buys}
                </div>
            </div>
            <div>
                <div>
                    {coppers} <i class="fa-solid fa-coins"></i>
                </div>
            </div>
            <div>
                <div>
                    {handSize}
                </div>
            </div>
            <div>
                <div>
                    Turn #{turnsPlayed}
                </div>
            </div>
        </main>
    </div>
{/if}

<style>
    main {
        z-index: 10;
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