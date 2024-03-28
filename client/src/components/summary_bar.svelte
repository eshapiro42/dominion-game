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
        <div class="field">
            <div class="field-title">
                Current Turn
            </div>
            <div class="field-value">
                {$currentPlayer == "" ? "No One" : $currentPlayer}
            </div>
        </div>
        <div class="field">
            <div class="field-title">
                Phase
            </div>
            <div class="field-value">
                {phase}
            </div>
        </div>
        <div class="field">
            <div class="field-title">
                Actions
            </div>
            <div class="field-value">
                {actions}
            </div>
        </div>
        <div class="field">
            <div class="field-title">
                Buys
            </div>
            <div class="field-value">
                {buys}
            </div>
        </div>
        <div class="field">
            <div class="field-title">
                Treasure
            </div>
            <div class="field-value">
                {coppers} <i class="fa-solid fa-coins"></i>
            </div>
        </div>
        <div class="field">
            <div class="field-title">
                Hand
            </div>
            <div class="field-value">
                {handSize}
            </div>
        </div>
        {#if coffers != null}
            <div class="field">
                <div class="field-title">
                    Coffers
                </div>
                <div class="field-value">
                    {coffers}
                </div>
            </div>
        {/if}
        <div class="field">
            <div class="field-title">
                Turns Played
            </div>
            <div class="field-value">
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
        font-family: var(--title-font-family);
    }

    .fa-arrow-up {
        position: absolute;
        left: 20px;
        transform: translateY(100%);
    }

    .fa-arrow-up:hover {
        cursor: pointer;
    }

    .isStuck {
        border-top: none;
    }

    .field {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 5px;
    }

    .field-title {
        color: color-mix(in srgb, var(--light-text-color) 60%, var(--thead-background-color) 40%);
        font-size: 80%;
        font-weight: bold;

    }
</style>