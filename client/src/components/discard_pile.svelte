<script>
    import CardCarousel from "./card_carousel.svelte";

    export let socket;
    export let gameStarted;

    let cards = [];
    let waitingForSelection = {
        value: false,
        handler: null,
        callback: null,
        type: "",
        maxCards: null,
        maxCost: null,
        force: false,
        prompt: null,
    }

    function handleSelected(event) {
        if (waitingForSelection.value) {
            var selectedCards = event.detail.selectedCards;
            if (waitingForSelection.handler(selectedCards)) {
                waitingForSelection.value = false;
                waitingForSelection.handler = null;
                waitingForSelection.callback = null;
                waitingForSelection.type = "";
                waitingForSelection.maxCards = null;
                waitingForSelection.maxCost = null;
                waitingForSelection.force = false;
                waitingForSelection.prompt = false;
            }
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
                waitingForSelection.callback(null);
                return true;
            }
        }
        waitingForSelection.callback(selectedCards[0]);
        return true;
    }        

    socket.on(
        "display discard pile", 
        (data) => {
            cards = data.cards;
        },
    );

    socket.on(
        "choose card from discard pile",
        (data, callback) => {
            waitingForSelection.value = true;
            waitingForSelection.handler = handleCardSelected;
            waitingForSelection.callback = callback;
            waitingForSelection.maxCards = 1;
            waitingForSelection.maxCost = null;
            waitingForSelection.force = false;
            waitingForSelection.prompt = data.prompt;
        },
    )
</script>

{#if gameStarted}
    <main>
        <CardCarousel
            title="Your Discard Pile"
            {cards}
            {waitingForSelection}
            on:selected={handleSelected}
        />
    </main>
{/if}

<style>
</style>