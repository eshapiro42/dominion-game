<script>
    import {
        socket,
        currentPlayer,
    } from "../stores.js";
 
    let phase = "";
    let actions = 1;
    let buys = 1;
    let coppers = 0;
    let handSize = 5;
    let turnsPlayed = 0;
    let coffers = null;

    $socket.on(
        "current turn info",
        (data) => {
            phase = data.current_phase;
            actions = data.actions;
            buys = data.buys;
            coppers = data.coppers;
            handSize = data.hand_size;
            turnsPlayed = data.turns_played;
            if ("coffers" in data) {
                coffers = data.coffers;
            };
        }
    );
</script>

<div class="panel-sticky">
    <main class="panel">
        <div>
            <div>
                {$currentPlayer == "" ? "No One" : $currentPlayer}
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
        {#if coffers != null}
            <div>
                <div>
                    {coffers}
                </div>
            </div>
        {/if}
        <div>
            <div>
                Turn #{turnsPlayed}
            </div>
        </div>
    </main>
</div>

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