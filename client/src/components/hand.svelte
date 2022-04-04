<script>
    import CardCarousel from "./card_carousel.svelte";

    export let socket;
    export let gameStarted;

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

    function handleTreasuresSelected(selectedCards) {
        if (selectedCards.length == 0) {
            var confirmed = confirm("Are you sure you want to skip selecting Treasures from your hand?");
            if (!confirmed) {
                return false;
            }
        }
        socket.emit("response", selectedCards);
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
                socket.emit("response", null);
                return true;
            }
        }
        socket.emit("response", selectedCards[0]);
        return true;
    }

    socket.on(
        "display hand", 
        (data) => {
            cards = data.cards;
        },
    );

    socket.on(
        "choose treasures from hand",
        (data) => {
            waitingForSelection.value = true;
            waitingForSelection.prompt = data.prompt;
            waitingForSelection.handler = handleTreasuresSelected;
            waitingForSelection.type = "treasure";
        }
    );

    socket.on(
        "choose specific card type from hand",
        (data) => {
            waitingForSelection.value = true;
            waitingForSelection.prompt = data.prompt;
            waitingForSelection.handler = handleCardSelected;
            waitingForSelection.type = data.card_type.toLowerCase();
            waitingForSelection.maxCards = 1;
        }
    );

    socket.on(
        "choose card from hand",
        (data) => {
            waitingForSelection.value = true;
            waitingForSelection.prompt = data.prompt;
            waitingForSelection.handler = handleCardSelected;
            waitingForSelection.force = data.force;
            waitingForSelection.maxCards = 1;
        }
    );

    socket.on(
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

{#if gameStarted}
    <main>
        <CardCarousel
            title="Your Hand"
            {cards}
            sortByProperty = "type"
            {waitingForSelection}
            on:selected={handleSelected}
        />
    </main>
{/if}

<style>
</style>