<script>
    import {fade} from "svelte/transition";

    import {
        socket,
        currentPlayer,
    } from "../stores.js";

    import {sticky} from "../common.js";
 
    let phase = "";
    let actions = 1;
    let buys = 1;
    let coppers = 0;
    let handSize = 5;
    let turnsPlayed = 0;
    let coffers = null;

    let isStuck = false;

    $socket.on(
        "display current turn info",
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

    function handleStuck(e) {
        isStuck = e.detail.isStuck;
    }
</script>

<div class="panel-sticky"
    use:sticky
    on:stuck={handleStuck}
>
    <main class="panel"
        class:isStuck
    >
        {#if isStuck}
            <i class="fa-solid fa-arrow-up"
                transition:fade={{delay:0, duration: 300}}
                on:click={() => window.scrollTo(0, 0)}
            ></i>
        {/if}
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
        background-color: var(--thead-background-color);
        color: var(--light-text-color);
        border: 1px solid var(--border-color);
        padding-top: 20px;
        padding-bottom: 20px;
        margin-top: 20px;
        margin-bottom: 20px;
        display: flex;
        flex-direction: row;
        justify-content: space-evenly;
    }

    .fa-arrow-up {
        position: absolute;
        left: 20px;
        top: 23px;
    }

    .fa-arrow-up:hover {
        cursor: pointer;
    }

    .isStuck {
        border-top: none;
    }
</style>