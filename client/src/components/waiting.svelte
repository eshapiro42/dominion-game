<script>
    export let players = [];

    let show = false;
    let formattedPlayers = "";

    $: show = players.length > 0;

    $: if (players.length === 0) {
        formattedPlayers = "";
    }
    else if (players.length === 1) {
        formattedPlayers = players[0];
    }
    else {
        formattedPlayers = players.slice(0, -1).join(", ") + " and " + players.slice(-1);
    }
</script>

{#if show}
    <main class="panel-sticky">
        <div class="panel">
            <p>Waiting for {formattedPlayers}...</p>
        </div>
    </main>
{/if}

<style>
    main {
        height: 64px;
        width: 100%;
        left: 0px;
        bottom: 0;
        display: flex;
        position: fixed;
        justify-content: center;
        background-color: color-mix(in srgb, var(--blue-color) 90%, transparent 10%);
        color: var(--dark-text-color);
        text-align: center;
        z-index: 999;
    }

    .panel-sticky {
        top: unset;
        bottom: 0px;
    }

    p {
        line-height: 64px;
        /* margin-left: calc(-1 * var(--gamelog-width)); */
    }
</style>