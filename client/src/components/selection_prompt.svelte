<script>
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher();

    export let waitingForSelection;

    function handleSendSelection() {
        dispatch(
            "sendSelection"
        );
    }

    function handleSelectAll() {
        dispatch(
            "selectAll"
        );
    }

</script>

<main>
    <p class="flex-item"><b>{waitingForSelection.prompt}</b></p>
    <div class="flex-item">
        <button type="button" on:click={handleSendSelection}>Send Selection</button>
        {#if waitingForSelection.maxCards == null}
            <button type="button" on:click={handleSelectAll}>Select All</button>
        {/if}
    </div>
</main>

<style>
    main {
        flex: 0 0 100%;
        gap: 10px;
        border: 1px solid slategrey;
    }

    .flex-item {
        flex-basis: 100%;
    }
</style>