<script>
    import { createEventDispatcher } from "svelte";
    
    const dispatch = createEventDispatcher();

    import Modal from "./modal.svelte";

    export let prompt = "";
    export let force = false;
    export let show;

    export let type = null; // Allowed types: "alert", "range", "options", "boolean"
    export let range = null; // range = {start: <int>, stop: <int>}
    export let options = null; // options = [{name: <str>, id: <int>}, ...]

    let selection = null;
    let rangeList = [];

    $: if (range != null) {
        // Create a consecutive range array from the start and stop values
        rangeList = new Array(range.stop - range.start + 1).fill(range.start).map((x, y) => x + y);
    }

    function submit() {
        dispatch(
            "submit",
            {
                selection: selection,
            }
        )
    }

    function handleClick() {
        if (type == "alert") {
            show = false;
        }
    }

    $: renderedPrompt = prompt.replace("$", `<i class="fa-solid fa-coins"></i>`);
</script>

<main>
    <Modal
        {show}
        on:click={handleClick}
    >
        <span slot="contents">
            <div class="backdrop">

                <div class="flex-item">
                    <h5>{@html renderedPrompt}</h5>
                </div>

                <div class="flex-item">
                    {#if type == "range"}
                        <select bind:value={selection}>
                            {#each rangeList as option}
                                <option value={option}>
                                    {option}
                                </option>
                            {/each}
                        </select>
                    {:else if type == "options"}
                        <select bind:value={selection}>
                            {#each options as option}
                                <option value={option.id}>
                                    {option.name}
                                </option>
                            {/each}
                        </select>       
                    {/if}

                    {#if type == "alert"}
                        <button on:click={submit}>Okay</button>
                    {:else if type == "boolean"}
                        <button on:click={
                            () => {
                                selection = true;
                                submit()
                            }
                        }>
                            Yes
                        </button>

                        <button on:click={
                            () => {
                                selection = false;
                                submit()
                            }
                        }>
                            No
                        </button>
                    {:else}

                        <button on:click={submit}>Send</button>

                        {#if !force}
                        <button on:click={
                            () => {
                                selection = null;
                                submit()
                            }
                        }>
                            Skip
                        </button>
                        {/if}
                    {/if}

                </div>
            </div>
        </span>
    </Modal>
</main>

<style>
    .backdrop {
        display: flex;
        flex-direction: column;
        gap: 20px;
        padding: 50px;
        min-width: 40vw;
        min-height: 20vh;
        background-color: whitesmoke;
        align-items: center;
        justify-content: center;
    }

    .flex-item {
        flex: 0 0 100%;
    }
</style>