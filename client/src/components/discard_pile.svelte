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

    function handleSelected(event) {
        if (waitingForSelection.value) {
            var selectedCards = event.detail.selectedCards;
            waitingForSelection.handler(selectedCards);
        }
    }

    function handleCardSelected(selectedCards) {
        if (selectedCards.length == 0) {
            if (waitingForSelection.force) {
                alert("You must make a selection.");
                return false;
            }
            else {
                var confirmed = confirm("Are you sure you want to skip selecting cards from your discard pile?");
                if (!confirmed) {
                    return false;
                }
                $socket.emit("response", null);
                return true;
            }
        }
        $socket.emit("response", selectedCards[0]);
        return true;
    }

    function handleCardsSelected(selectedCards) {
        // TODO: This shares 99% of its code with handleCardSelected and they should be merged
        if (selectedCards.length == 0) {
            if (waitingForSelection.force) {
                alert("You must make a selection.");
                return false;
            }
            else {
                var confirmed = confirm("Are you sure you want to skip selecting cards from your discard pile?");
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

    $socket.on(
        "display discard pile", 
        (data) => {
            cards = data.cards;
        },
    );

    $socket.on(
        "choose card from discard pile",
        (data) => {
            waitingForSelection.value = true;
            waitingForSelection.handler = handleCardSelected;
            waitingForSelection.maxCards = 1;
            waitingForSelection.maxCost = null;
            waitingForSelection.force = data.force;
            waitingForSelection.prompt = data.prompt;
        },
    );

    $socket.on(
        "choose cards of specific type from discard pile",
        (data) => {
            waitingForSelection.value = true;
            waitingForSelection.handler = handleCardsSelected;
            waitingForSelection.maxCards = data.max_cards;
            waitingForSelection.maxCost = null;
            waitingForSelection.force = data.force;
            waitingForSelection.prompt = data.prompt;
            waitingForSelection.type = data.card_type;
        },
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

<main>
    <CardCarousel
        title="Your Discard Pile"
        {cards}
        sortByProperty = "orderSent"
        {waitingForSelection}
        on:selected={handleSelected}
    />
</main>

<style>
</style>