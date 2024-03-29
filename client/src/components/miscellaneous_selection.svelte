<script>
    import { createEventDispatcher } from "svelte";
    
    const dispatch = createEventDispatcher();

    import {socket, username, currentPlayer} from "../stores.js";

    import {flashTitle} from "../common.js";

    import CardCarousel from "./card_carousel.svelte";

    export let prompt = "";
    export let force = false;
    export let show;

    export let type = null; // Allowed types: "alert", "range", "options", "boolean"
    export let range = null; // range = {start: <int>, stop: <int>}
    export let options = null; // options = [{name: <str>, id: <int>}, ...]
    export let cards = [];
    export let waitingForSelection = {};
    let selection = null;
    let rangeList = [];
    let title = "Miscellaneous Selection";
    let renderedPrompt = "";
    let renderedOptions = [];

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
        );
        selection = null;
    }

    function handleSelected(event) {
        if (waitingForSelection.value) {
            var selectedCards = event.detail.selectedCards;
            handleCardsSelected(selectedCards);
        }
    }

    function handleCardsSelected(selectedCards) {
        // TODO: This shares 99% of its code with handleCardSelected and they should be merged
        if (selectedCards.length == 0) {
            if (waitingForSelection.force) {
                alert("You must make a selection.");
                return false;
            }
            else {
                var confirmed = confirm("Are you sure you want to skip selecting cards?");
                if (!confirmed) {
                    return false;
                }
                $socket.emit("response", null);
                return true;
            }
        }
        $socket.emit("response", selectedCards);
        return true;
    }

    function renderText(text) {
        return text
            .replaceAll("$", `<i class="fa-solid fa-coins"></i>`)
            .replaceAll("victory points", `<i class="bi bi-shield-shaded"></i>`)
            .replaceAll("victory point", `<i class="bi bi-shield-shaded"></i>`);
    }

    $: renderedPrompt = renderText(prompt);
    $: if (options != null) {
            renderedOptions = options.map(
            option => {
                return {
                    name: renderText(option.name),
                    id: option.id,
                }
            }
        );
    }

    $: if (show) {
        // Scroll to the active carousel after a short delay to allow the page to render
        setTimeout(
            () => {
                location.hash = "#" + title;
                history.pushState("", document.title, window.location.pathname + window.location.search);
                if ($username != $currentPlayer) {
                    flashTitle("You Must React!");
                    alert(`Heads up: It is still ${$currentPlayer}'s turn!`);
                }
            },
            300,
        );
    }

    // $socket.on(
    //     "choose cards from list",
    //     (data) => {
    //         cards = data.cards;
    //         waitingForSelection.value = true;
    //         waitingForSelection.prompt = data.prompt;
    //         waitingForSelection.handler = handleCardsSelected;
    //         waitingForSelection.force = data.force;
    //         waitingForSelection.maxCards = data.max_cards;
    //     }
    // );
</script>

{#if show}
    {#if cards}
        <CardCarousel
            {title}
            {cards}
            {waitingForSelection}
            sortByProperty = "orderSent"
            on:selected={handleSelected}
        />
    {:else}
        <section id="{title}">
            <main
                class:show
                class="panel"
            >
                <div class="flex-item">
                    <h5>{@html renderedPrompt}</h5>
                </div>

                <div class="flex-item">
                    <div class="options">
                        {#if type == "range"}
                            <select bind:value={selection}>
                                {#each rangeList as option (option)}
                                    <option value={option}>
                                        {option}
                                    </option>
                                {/each}
                            </select>
                        {:else if type == "options"}
                            {#each renderedOptions as renderedOption (renderedOption.id)}
                                <label>
                                    <input type="radio" bind:group={selection} name="selection" value={renderedOption.id}>
                                    {@html renderedOption.name}
                                </label>       
                            {/each}
                        {/if}
                    </div>

                    {#if type == "alert"}
                        <button on:click={submit}>Okay</button>
                    {:else if type == "boolean"}
                        <button 
                            class="blueButton"
                            on:click={
                                () => {
                                    selection = true;
                                    submit()
                                }
                            }
                        >
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
                        <button class="blueButton" 
                            on:click={submit}
                        >
                            Send
                        </button>

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
            </main>
        </section>
    {/if}
{/if}

<style>
    main {
        margin-top: 20px;
        padding: 20px;
        border: 1px solid var(--border-color);
        display: flex;
        flex-direction: column;
        gap: 20px;
        align-items: center;
        justify-content: flex-start;        
    }

    .show {
        animation: blinking var(--blinking-speed) ease-in-out infinite;
    }

    .flex-item {
        flex: 0 0 100%;
    }

    .options {
        text-align: center;
        padding-bottom: 25px;
    }

    label {
        display: flex;
        align-items: baseline;
        gap: 5px;
    }
</style>