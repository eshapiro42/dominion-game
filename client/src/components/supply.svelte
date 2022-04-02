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

    function handleSupplyCardClassSelected(selectedCards) {
        if (selectedCards.length == 0) {
            if (waitingForSelection.force) {
                alert("You must make a selection.");
                return false;
            }
            var confirmed = confirm("Are you sure you want to skip selecting a card from the Supply?");
            if (confirmed) {
                socket.emit("response", null);
                return true;
            }
            return false;
        }
        socket.emit("response", selectedCards[0]);
        return true;
    }

    socket.on(
        "display supply", 
        (data) => {
            cards = data.cards;
        },
    );

    socket.on(
        "choose card class from supply",
        (data) => {
            waitingForSelection.value = true;
            waitingForSelection.prompt = data.prompt;
            waitingForSelection.handler = handleSupplyCardClassSelected;
            waitingForSelection.maxCards = 1;
            waitingForSelection.maxCost = data.max_cost;
            waitingForSelection.force = data.force;
        }
    )

    socket.on(
        "choose specific card type from supply",
        (data) => {
            waitingForSelection.value = true;
            waitingForSelection.prompt = data.prompt;
            waitingForSelection.handler = handleSupplyCardClassSelected;
            waitingForSelection.maxCards = 1;
            waitingForSelection.maxCost = data.max_cost;
            waitingForSelection.type = data.card_type;
            waitingForSelection.force = data.force;
        }
    )

    socket.on(
        "response received",
        (data) => {
            console.log("server received response")
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
            title="Supply"
            {cards}
            {waitingForSelection}
            on:selected={handleSelected}
        />
    </main>
{/if}

<style>    
</style>