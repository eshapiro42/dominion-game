<script>
    import { createEventDispatcher } from "svelte";

    const dispatch = createEventDispatcher();

    export let waitingForSelection;

    function handleSendSelection() {
        document.removeEventListener("keyup", handleEnterKey);
        dispatch(
            "sendSelection"
        );
    }

    function handleSelectAll() {
        document.removeEventListener("keyup", handleAKey);
        dispatch(
            "selectAll"
        );
    }

    function handleEnterKey(event) {
        if (event.code == "Enter" && waitingForSelection) {
            document.removeEventListener("keyup", this);
            handleSendSelection();
        }
    }

    function handleAKey(event) {
        if (event.code == "KeyA" && selectAllEnabled) {
            document.removeEventListener("keyup", this);
            handleSelectAll();
        }
    }

    function renderText(text) {
        return text
            .replaceAll("$", `<i class="fa-solid fa-coins"></i>`)
            .replaceAll("victory points", `<i class="bi bi-shield-shaded"></i>`)
            .replaceAll("victory point", `<i class="bi bi-shield-shaded"></i>`);
    }

    $: renderedPrompt = renderText(waitingForSelection.prompt);

    $: selectAllEnabled = waitingForSelection.value && waitingForSelection.maxCards == null;

    $: if (waitingForSelection.value) {
        document.addEventListener("keyup", handleEnterKey, {once: true});
        if (selectAllEnabled) {
            document.addEventListener("keyup", handleAKey, {once: true});
        }
    }
    else {
        document.removeEventListener("keyup", handleEnterKey);
        document.removeEventListener("keyup", handleAKey);
    }

</script>

<main>
    <p class="flex-item"><b>{@html renderedPrompt}</b></p>
    <div class="flex-item">
        <button class="blueButton" on:click={handleSendSelection}>Send Selection</button>
        {#if selectAllEnabled}
            <button on:click={handleSelectAll}>Select All</button>
        {/if}
    </div>
</main>

<style>
    main {
        flex: 0 0 100%;
        gap: 10px;
        padding: 20px;
        border: 1px solid var(--border-color);
        background-color: color-mix(in srgb, var(--blue-color), var(--body-background-color) 70%);
    }

    .flex-item {
        flex-basis: 100%;
    }
</style>