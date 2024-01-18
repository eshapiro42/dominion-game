<script>
    import {socket} from "../stores.js";

    import CardCarousel from "./card_carousel.svelte";

    let cards = [];
    let waitingForSelection = {
        value: false,
        handler: null,
        type: "",
        maxCards: null,
        maxCost: null,
        force: false,
        prompt: null,
    }
    let show = false;

    function handleSelected(event) {
        if (waitingForSelection.value) {
            var selectedCards = event.detail.selectedCards;
            waitingForSelection.handler(selectedCards);
        }
    }

    function handleCardSelected(selectedCards) {
        if (selectedCards.length == 0) {
            alert("You must make a selection.");
            return false;
        }
        $socket.emit("response", selectedCards[0]);
        return true;
    }

    $socket.on(
        "display prizes", 
        (data) => {
            show = true;
            cards = data.cards;
        },
    );

    $socket.on(
        "choose card from prizes",
        (data) => {
            waitingForSelection.value = true;
            waitingForSelection.prompt = data.prompt;
            waitingForSelection.handler = handleCardSelected;
            waitingForSelection.maxCards = 1;
        }
    );

    $socket.on(
        "response received",
        (data) => {
            waitingForSelection = {
                value: false,
                handler: null,
                type: "",
                maxCards: null,
                maxCost: null,
                force: false,
                prompt: null,
            }
        }
    );
</script>

{#if show}
    <main>
        <CardCarousel
            title="Prizes"
            {cards}
            sortByProperty = "name"
            {waitingForSelection}
            on:selected={handleSelected}
        />
    </main>
{/if}

<style>
</style>