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

    function renderText(text) {
        return text
            .replaceAll("$", `<i class="fa-solid fa-coins"></i>`)
            .replaceAll("victory points", `<i class="bi bi-shield-shaded"></i>`)
            .replaceAll("victory point", `<i class="bi bi-shield-shaded"></i>`);
    }

    $: renderedPrompt = renderText(waitingForSelection.prompt);

</script>

<main>
    <p class="flex-item"><b>{@html renderedPrompt}</b></p>
    <div class="flex-item">
        <button type="button" on:click={handleSendSelection}>Send Selection</button>
        {#if waitingForSelection.maxCards == null && waitingForSelection.maxCards != 1}
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