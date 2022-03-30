<script>
    export let waitingForSelection;
</script>

<main>
    <p class="flex-item"><b>{waitingForSelection.prompt}</b></p>
    <div class="flex-item">
        <button type="button" on:click>Send Selection</button>
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