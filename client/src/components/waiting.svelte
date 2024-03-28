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
    <main>
        <p>Waiting for {formattedPlayers}...</p>
    </main>
{/if}

<style>
    main {
        height: 64px;
        width: 100%;
        bottom: 0;
        left: 0;
        display: flex;
        position: fixed;
        justify-content: center;
        background-color: var(--blue-color);
        color: var(--dark-text-color);
        text-align: center;
        z-index: 999;
    }

    p {
        line-height: 64px;
        margin-left: 64px;
    }
</style>