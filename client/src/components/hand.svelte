<script>
    import {socket} from "../stores.js";

    import CardCarousel from "./card_carousel.svelte";

    let cards = [];
    let invalidCardIds;
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

    function handleTreasuresSelected(selectedCards) {
        if (selectedCards.length == 0) {
            var confirmed = confirm("Are you sure you want to skip selecting Treasures from your hand?");
            if (!confirmed) {
                return false;
            }
        }
        $socket.emit("response", selectedCards);
        return true;
    }

    function handleCardSelected(selectedCards) {
        if (selectedCards.length == 0) {
            if (waitingForSelection.force) {
                alert("You must make a selection.");
                return false;
            }
            else {
                var confirmed = confirm("Are you sure you want to skip selecting cards from your hand?");
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
                var confirmed = confirm("Are you sure you want to skip selecting cards from your hand?");
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
        "display hand", 
        (data) => {
            cards = data.cards;
        },
    );

    $socket.on(
        "choose treasures from hand",
        (data) => {
            waitingForSelection.value = true;
            waitingForSelection.prompt = data.prompt;
            waitingForSelection.handler = handleTreasuresSelected;
            waitingForSelection.type = "treasure";
        }
    );

    $socket.on(
        "choose specific card type from hand",
        (data) => {
            waitingForSelection.value = true;
            waitingForSelection.prompt = data.prompt;
            waitingForSelection.handler = handleCardSelected;
            waitingForSelection.type = data.card_type.toLowerCase();
            waitingForSelection.force = data.force;
            waitingForSelection.maxCards = 1;
        }
    );

    $socket.on(
        "choose cards from hand",
        (data) => {
            invalidCardIds = data.invalid_cards;
            waitingForSelection.value = true;
            waitingForSelection.prompt = data.prompt;
            waitingForSelection.handler = handleCardsSelected;
            waitingForSelection.force = data.force;
            waitingForSelection.maxCards = data.max_cards;
        }
    );

    $socket.on(
        "response received",
        (data) => {
            invalidCardIds = [];
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
        title="Your Hand"
        {cards}
        {invalidCardIds}
        sortByProperty = "type"
        {waitingForSelection}
        on:selected={handleSelected}
    />
</main>

<style>
</style>