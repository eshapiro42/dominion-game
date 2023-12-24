<script>
    import {
        socket,
        currentPlayer,
    } from "../stores.js";

    import CardCarousel from "./card_carousel.svelte";

    let cards = [];
    let waitingForSelection = {
        value: false,
        handler: null,
        type: "",
        maxCards: null,
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
                var confirmed = confirm("Are you sure you want to skip selecting cards from your played cards?");
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
                var confirmed = confirm("Are you sure you want to skip selecting cards from your played cards?");
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
        "display played cards", 
        (data) => {
            cards = data.cards;
        },
    );

    $socket.on(
        "current player",
        (data) => {
            $currentPlayer = data;
        },
    )

    $socket.on(
        "choose specific card type from played cards",
        (data) => {
            waitingForSelection.value = true;
            waitingForSelection.prompt = data.prompt;
            waitingForSelection.handler = handleCardSelected;
            waitingForSelection.type = data.card_type.toLowerCase();
            waitingForSelection.maxCards = 1;
        }
    );

    $socket.on(
        "choose cards of specific type from played cards",
        (data) => {
            waitingForSelection.value = true;
            waitingForSelection.prompt = data.prompt;
            waitingForSelection.handler = handleCardsSelected;
            waitingForSelection.type = data.card_type.toLowerCase();
            waitingForSelection.maxCards = data.max_cards;
            waitingForSelection.force = data.force;
            waitingForSelection.ordered = data.ordered;
        }
    )

    $socket.on(
        "response received",
        (data) => {
            waitingForSelection = {
                value: false,
                handler: null,
                type: "",
                maxCards: null,
                force: false,
                prompt: null,
            };
        }
    );
</script>

<section id="Played Cards">
    <main>
        <CardCarousel
            title="{$currentPlayer == "" ? "No One" : $currentPlayer}'s Played Cards"
            sortByProperty = "orderSent"
            {waitingForSelection}
            {cards}
            on:selected={handleSelected}
        />
    </main>
</section>

<style>
</style>