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

    function handleEnterKey(event) {
        if (event.code == "Enter" && waitingForSelection) {
            handleSendSelection();
        }
    }

    function handleAKey(event) {
        if (event.code == "KeyA" && waitingForSelection) {
            handleSelectAll();
        }
    }

    function ignoreKeyPresses(event) {
        event.preventDefault();
    }

    $: renderedPrompt = waitingForSelection.prompt.replace("$", `<i class="fa-solid fa-coins"></i>`);

    $: selectAllEnabled = waitingForSelection.maxCards == null && waitingForSelection.maxCards != 1;

    $: if (waitingForSelection.value) {
        document.addEventListener("keyup", handleEnterKey, {once: true});
        if (selectAllEnabled) {
            document.addEventListener("keyup", handleAKey, {once: true});
        } else {
            document.addEventListener("keyup", ignoreKeyPresses);
        }
    }
</script>

<main>
    <p class="flex-item"><b>{@html renderedPrompt}</b></p>
    <div class="flex-item">
        <button type="button" on:click={handleSendSelection}>Send Selection</button>
        {#if selectAllEnabled}
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