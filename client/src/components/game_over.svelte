<script>
    import { createEventDispatcher } from "svelte";
    
    const dispatch = createEventDispatcher();

    import {socket} from "../stores.js";

    import CardCarousel from "./card_carousel.svelte";

    export let endGameData;
    export let show;
    export let cards = [];
    let waitingForSelection = {
        value: false,
        handler: null,
        type: "",
        maxCards: null,
        maxCost: null,
        force: false,
        prompt: null,
    }
    let title = "Game Over";

    $: if (show) {
        // Scroll to the active carousel after a short delay to allow the page to render
        setTimeout(
            () => {
                location.hash = "#" + title;
            },
            300,
        );
    }
</script>

{#if show}
    <main>
            <CardCarousel
                {title}
                {cards}
                sortByProperty = "type"
                {waitingForSelection}
                {endGameData}
            />
    </main>
{/if}

<style>
</style>