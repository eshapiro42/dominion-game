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

    function handleCardSelected(selectedCards) {
        if (selectedCards.length == 0) {
            if (waitingForSelection.force) {
                alert("You must make a selection.");
                return false;
            }
            else {
                var confirmed = confirm("Are you sure you want to skip selecting cards from the Trash?");
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
        "display trash", 
        (data) => {
            cards = data.cards;
        },
    );

    socket.on(
        "choose specific card type from trash",
        (data) => {
            waitingForSelection.value = true;
            waitingForSelection.handler = handleCardSelected;
            waitingForSelection.type = data.card_type;
            waitingForSelection.maxCards = 1;
            waitingForSelection.maxCost = data.max_cost;
            waitingForSelection.force = data.force;
            waitingForSelection.prompt = data.prompt;
        },
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
            title="Trash"
            {cards}
            sortByProperty = "orderSent"
            {waitingForSelection}
            on:selected={handleSelected}
        />
    </main>
{/if}

<style>
</style>