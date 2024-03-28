<script>
    import {onMount} from "svelte";
    import {socket} from "../stores.js";

    let entries = [];

    onMount(
        () => {
            document.documentElement.setAttribute("gamelog-width", "256px");
        }
    );

    $socket.on(
        "new log entry",
        (entry) => {
            entry.timestamp = new Date(entry.timestamp);
            entries = [...entries, entry];
        }
    );
</script>

<main>
    {#each entries as entry}
        <div class="entry">
            {entry.timestamp}: {entry.message}
        </div>
    {/each}
</main>

<style>
    main {
        z-index: 9999;
        right: 0;
        top: 0;
        width: 256px;
        height: 100%;
        position: fixed;
        background-color: var(--thead-background-color);
        color: var(--light-text-color);
        border-left: 1px solid var(--border-color);
        display: flex;
        flex-direction: column;
        flex-wrap: wrap;
        gap: 20px;
        justify-content: space-around;
        align-items: stretch;
        font-family: var(--title-font-family);
    }

    /* Do not show game log on mobile devices */
    @media (max-width: 767px) {
        main {
             display: none;
        }
    }
</style>